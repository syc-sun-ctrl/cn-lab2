#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 实验二 Part D：自己写一个 HTTP 客户端（webget）
# 孙宇程 251006112 网工25
# GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2
#
# 用法：python webget.py <host> <port> <path> [保存文件名]
# 例：python webget.py 127.0.0.1 8080 / out.html
#
# 这个程序是从老师给的 8 行起点代码一点点改出来的：
# 一开始只是 connect + send + recv 一次 + 打印，后来发现 recv 一次根本收不全，
# 才把 recv 放进循环里，又加上了响应头解析、命令行参数和统计打印。

import socket
import sys

# 一次 recv 最多要多少字节。4096 是我随手定的，改大改小都能跑
BUF = 4096


def make_request(host, path):
    # 拼 HTTP/1.1 请求。
    # 这里故意加 Connection: close，让服务器回完就把连接关掉，
    # 这样下面的 recv 最后一定能收到 b""，循环不会卡在 keep-alive 上。
    req = (
        "GET " + path + " HTTP/1.1\r\n"
        "Host: " + host + "\r\n"
        "User-Agent: webget/1.0 (251006112)\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return req.encode("ascii")


def recv_all(sock):
    """把响应整个收下来。

    循环什么时候结束？我遇到的就两种情况：
      (1) 响应头里有 Content-Length：按它写的字节数，正文收够就 break；
      (2) 头里没有 Content-Length：那就没法提前知道多长，只能一直收，
          直到 recv 返回 b""（说明服务器把连接关了）。
    注意判断“正文收了几个字节”要用 len(buf) - 头长度，
    不能直接拿 len(buf) 跟 Content-Length 比，我一开始就这么写的，
    结果一直多算了几百字节的头，循环收不完。

    返回：全部字节、recv 调了几次、每次收了多少字节的列表
    """
    buf = b""
    counts = []
    header_end = None      # 空行 \r\n\r\n 结束的位置（也就是正文开始的位置）
    content_length = None  # 响应头里写的 Content-Length

    while True:
        chunk = sock.recv(BUF)
        if not chunk:
            # 空 bytes，说明对端 close 了（收到 FIN），这就是结束条件(2)
            print("  [recv #%d] 收到 0 字节，对端关了，结束" % (len(counts) + 1))
            break

        counts.append(len(chunk))
        buf += chunk
        print("  [recv #%d] 收到 %d 字节，一共 %d 字节" % (len(counts), len(chunk), len(buf)))

        # 头还没解析过就找一次空行，看有没有 Content-Length
        if header_end is None:
            pos = buf.find(b"\r\n\r\n")
            if pos != -1:
                header_end = pos + 4
                head_text = buf[:pos].decode("iso-8859-1")
                for line in head_text.split("\r\n")[1:]:
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":", 1)[1].strip())
                        break
                if content_length is None:
                    print("  [提示] 头里没有 Content-Length，只能等对端关连接")
                else:
                    print("  [提示] Content-Length: %d，收够就停" % content_length)

        # 结束条件(1)：正文已经收够 Content-Length 了
        if header_end is not None and content_length is not None:
            body_len = len(buf) - header_end
            if body_len >= content_length:
                print("  [结束] 正文收够 %d 字节，break" % content_length)
                break

    return buf, len(counts), counts


def split_response(raw):
    """按空行把头、正文分开。
    头里面第一行是状态行，剩下的每一行都是 响应头: 值。
    """
    pos = raw.find(b"\r\n\r\n")
    if pos == -1:
        head, body = raw, b""
    else:
        head, body = raw[:pos], raw[pos + 4:]

    lines = head.decode("iso-8859-1").split("\r\n")
    status_line = lines[0] if len(lines) > 0 else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status_line, headers, body, lines


def main():
    # T3：参数不够就直接打印用法退出
    if len(sys.argv) < 4:
        print("用法: python webget.py <host> <port> <path> [保存文件名]")
        print("例: python webget.py 127.0.0.1 8080 / out.html")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    path = sys.argv[3]
    if not path.startswith("/"):
        path = "/" + path
    outfile = sys.argv[4] if len(sys.argv) > 4 else "body.bin"

    print("目标：%s:%d%s" % (host, port, path))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)  # 防止服务器不回，一直卡在这
    try:
        print("[1] connect ...（抓包里的三次握手就是这里）")
        s.connect((host, port))

        req = make_request(host, path)
        print("[2] 发请求，%d 字节" % len(req))
        s.sendall(req)

        print("[3] 开始收响应：")
        raw, n_recv, counts = recv_all(s)
    finally:
        s.close()

    print("")
    print("[4] 一共收到 %d 字节，recv 了 %d 次，每次字节数：%s" % (len(raw), n_recv, counts))
    status_line, headers, body, head_lines = split_response(raw)
    print("    状态行：" + status_line)
    print("    响应头：")
    for line in head_lines[1:]:
        print("      " + line)

    # T2：正文用 wb 存。文本模式(w)会把 \r\n 改成 \n，还会按编码解码，
    # 存图片直接就是坏文件，我试过，所以这里必须二进制。
    print("")
    print("[5] 正文 %d 字节，用 wb 写到 %s" % (len(body), outfile))
    f = open(outfile, "wb")
    f.write(body)
    f.close()

    # T4 要的统计，直接打印出来看
    print("")
    print("[统计] recv 次数 = %d" % n_recv)
    print("[统计] 每次字节数 = %s" % counts)
    print("[统计] 总共 %d 字节 = 响应头 %d + 正文 %d"
          % (len(raw), len(raw) - len(body), len(body)))
    print("[统计] 一次 recv 不等于一个 HTTP 报文，TCP 是字节流，"
          "得靠 Content-Length 或者对端关闭才知道收完没有")


if __name__ == "__main__":
    main()
