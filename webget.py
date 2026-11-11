#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webget.py —— 手搓一个 HTTP 客户端（实验二 Part D，T1~T5 全部实现）

实验二：HTTP 客户端与 TCP、UDP 协议分析
作者：孙宇程  学号：251006112  班级：网工25
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

用法：
    python webget.py <host> <port> <path> [保存文件名]
    例：python webget.py www.bjfu.edu.cn 80 / index.html

功能对应：
    T1 循环 recv：把 recv 放进 while 循环，结束条件两种——
       (a) 响应头里有 Content-Length，按它收够就停；
       (b) 没有 Content-Length（或 Connection: close），一直收到对端关闭（recv 返回 b""）。
       同时打印每次 recv 的序号、字节数，方便 T4 观察。
    T2 解析：按空行把「状态行 / 响应头 / 正文」分开；打印状态行和全部响应头；
       正文用二进制模式 wb 写文件（文本模式会把 \r\n 改写、还可能因编码报错，图片会坏）。
    T3 参数化：host / port / path 都不写死，从命令行参数取；参数不够就打印用法并退出。
    T4 观察题：程序会打印 recv 次数、每次字节数、总字节数，直接能看出「一次没到齐」。
    T5 抓包对照：程序只用了 socket 标准库，抓包时能看到 SYN/SYN+ACK/ACK + 请求 + 响应 + FIN。
"""
import socket
import sys

USAGE = "用法: python webget.py <host> <port> <path> [保存文件名]\n例: python webget.py www.bjfu.edu.cn 80 / index.html"


def build_request(host, path):
    """构造 HTTP/1.1 请求。
    用 Connection: close 是为了让服务器回完就关连接，这样 recv 最终能收到 b""，
    循环一定能结束（不会挂死在 keep-alive 上）。"""
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: webget/1.0 (251006112)\r\n"
        f"Accept: */*\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return req.encode("ascii")


def recv_all(sock):
    """T1：循环 recv，直到收够 Content-Length 或对端关闭。
    返回 (完整字节, recv 次数, 每次字节数列表)。"""
    buf = b""
    counts = []
    header_end = None
    content_length = None

    while True:
        chunk = sock.recv(4096)          # 一次最多收 4096 字节，实际收到多少不确定
        if not chunk:                    # b"" 表示对端关闭了连接（FIN）
            print(f"  [recv #{len(counts)+1}] 收到 0 字节 → 对端关闭，循环结束")
            break
        counts.append(len(chunk))
        buf += chunk
        print(f"  [recv #{len(counts)}] 收到 {len(chunk)} 字节，累计 {len(buf)} 字节")

        # 头还没解析过就先找空行，拿到 Content-Length
        if header_end is None:
            idx = buf.find(b"\r\n\r\n")
            if idx != -1:
                header_end = idx + 4
                head = buf[:idx].decode("iso-8859-1")
                for line in head.split("\r\n")[1:]:
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":", 1)[1].strip())
                        break
                if content_length is not None:
                    print(f"  [提示] 响应头里有 Content-Length: {content_length}，收够就停")
                else:
                    print("  [提示] 响应头里没有 Content-Length，只能靠对端关闭来判断结束")

        # 结束条件 (a)：头里的 Content-Length 已经收满
        if header_end is not None and content_length is not None:
            if len(buf) - header_end >= content_length:
                print(f"  [结束] 正文已收够 {content_length} 字节，停止 recv")
                break
        # 结束条件 (b)：没声明长度时，只能等上面的 b"" 分支
    return buf, len(counts), counts


def parse_response(raw):
    """T2：按空行切开，返回 (状态行, 响应头字典, 正文字节, 响应头原文列表)"""
    idx = raw.find(b"\r\n\r\n")
    if idx == -1:                       # 万一只收到头没收到正文（D4 那种异常也会这样）
        head, body = raw, b""
    else:
        head, body = raw[:idx], raw[idx + 4:]
    lines = head.decode("iso-8859-1").split("\r\n")
    status_line = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status_line, headers, body, lines


def main():
    if len(sys.argv) < 4:               # T3：参数不够就给用法并退出
        print(USAGE)
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    path = sys.argv[3]
    outfile = sys.argv[4] if len(sys.argv) > 4 else "body.bin"

    print(f"== webget == 目标 {host}:{port}{path}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(10)                # 防止挂在坏服务器上（DNS 失败/端口不通也会抛异常）
        print(f"[1] 连接 {host}:{port} ……（抓包里这里的三个包就是三次握手）")
        s.connect((host, port))
        req = build_request(host, path if path.startswith("/") else "/" + path)
        print(f"[2] 发送请求 {len(req)} 字节：")
        print("    " + req.decode("ascii").replace("\r\n", "\n    "))
        s.sendall(req)

        print("[3] 循环接收响应：")
        raw, n_recv, counts = recv_all(s)

    print(f"\n[4] 解析：共收到 {len(raw)} 字节，recv 调用 {n_recv} 次，每次字节数 = {counts}")
    status_line, headers, body, head_lines = parse_response(raw)
    print(f"    状态行：{status_line}")
    print("    响应头：")
    for line in head_lines[1:]:
        print("      " + line)

    print(f"\n[5] 写正文：{len(body)} 字节 → {outfile}（用 wb 二进制模式写）")
    with open(outfile, "wb") as f:      # 二进制模式：不翻译换行、不猜编码
        f.write(body)

    # T4 观察题要的统计，直接打出来
    print(f"\n[T4 观察] recv 次数={n_recv}，每次字节数={counts}")
    print(f"[T4 观察] 总收到 {len(raw)} 字节，其中响应头 {len(raw) - len(body)} 字节、正文 {len(body)} 字节")
    print("[T4 观察] 这说明一次 recv 并不等于一个 HTTP 报文，TCP 是字节流，"
          "要靠 Content-Length 或对端关闭才能知道“收完了”")


if __name__ == "__main__":
    main()
