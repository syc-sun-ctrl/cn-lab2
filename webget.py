#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GitHub: https://github.com/syc-sun-ctrl/cn-lab2

import socket
import sys

BUF = 4096  # 一次 recv 最多收多少字节


def make_request(host, path):
    # 拼 HTTP 请求。Connection: close 让服务器回完就关连接，
    # 这样 recv 最后能收到 b""，循环不会卡在 keep-alive 上。
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
    """把响应收完，返回 (全部字节, recv 次数, 每次字节数)。

    循环什么时候结束，就两种情况：
    1) 响应头里有 Content-Length：正文收够这么多字节就 break；
    2) 头里没有 Content-Length：只能一直收，直到 recv 返回 b""（对端关了连接）。
    判断正文长度要用 len(buf) - 头的长度，不能直接拿 len(buf) 比，
    不然会把响应头也算进去，永远收不够。
    """
    buf = b""
    counts = []
    header_end = None
    content_length = None

    while True:
        chunk = sock.recv(BUF)
        if not chunk:  # b"" = 对端 close，结束条件(2)
            print("  [recv #%d] 收到 0 字节，对端关闭，结束" % (len(counts) + 1))
            break

        counts.append(len(chunk))
        buf += chunk
        print("  [recv #%d] 收到 %d 字节，累计 %d 字节" % (len(counts), len(chunk), len(buf)))

        # 第一次收到数据时找一下头结束的位置（\r\n\r\n）和 Content-Length
        if header_end is None:
            pos = buf.find(b"\r\n\r\n")
            if pos != -1:
                header_end = pos + 4
                head = buf[:pos].decode("iso-8859-1")
                for line in head.split("\r\n")[1:]:
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":", 1)[1].strip())
                        break
                if content_length is None:
                    print("  [提示] 没有 Content-Length，等对端关连接")
                else:
                    print("  [提示] Content-Length: %d，收够就停" % content_length)

        # 结束条件(1)：正文收够 Content-Length
        if header_end is not None and content_length is not None:
            if len(buf) - header_end >= content_length:
                print("  [结束] 正文够 %d 字节，break" % content_length)
                break

    return buf, len(counts), counts


def split_response(raw):
    """按空行把头/正文分开，头里第一行是状态行，后面是响应头。"""
    pos = raw.find(b"\r\n\r\n")
    if pos == -1:
        head, body = raw, b""
    else:
        head, body = raw[:pos], raw[pos + 4:]

    lines = head.decode("iso-8859-1").split("\r\n")
    status_line = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status_line, headers, body, lines


def main():
    # 参数不够就打印用法退出（T3）
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
    s.settimeout(10)  # 防止服务器不回，一直卡着
    try:
        print("[1] connect ...")
        s.connect((host, port))

        req = make_request(host, path)
        print("[2] 发请求，%d 字节" % len(req))
        s.sendall(req)

        print("[3] 收响应：")
        raw, n_recv, counts = recv_all(s)
    finally:
        s.close()

    print("")
    print("[4] 收到 %d 字节，recv %d 次，每次字节数：%s" % (len(raw), n_recv, counts))
    status_line, headers, body, head_lines = split_response(raw)
    print("    状态行：" + status_line)
    print("    响应头：")
    for line in head_lines[1:]:
        print("      " + line)

    # T2：正文必须用 wb 存。w 模式会改 \r\n 还会按编码解码，存图片会坏。
    print("")
    print("[5] 正文 %d 字节，wb 写到 %s" % (len(body), outfile))
    with open(outfile, "wb") as f:
        f.write(body)

    # T4 要的统计
    print("")
    print("[统计] recv 次数 = %d" % n_recv)
    print("[统计] 每次字节数 = %s" % counts)
    print("[统计] 总共 %d 字节 = 响应头 %d + 正文 %d"
          % (len(raw), len(raw) - len(body), len(body)))
    print("[统计] 一次 recv 不等于一个 HTTP 报文，TCP 是字节流，"
          "要靠 Content-Length 或对端关闭才知道收完")


if __name__ == "__main__":
    main()
