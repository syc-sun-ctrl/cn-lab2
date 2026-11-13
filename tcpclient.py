#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tcpclient.py —— 教材第 2 章 TCP 客户端示例（A2、B 部分用）

实验二：HTTP 客户端与 TCP、UDP 协议分析
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明（A 部分要回答的问题就在这几行里）：
    UDP 客户端比 TCP 客户端少的那一步是 connect()。
    本文件第 26 行 s.connect((SERVER_IP, PORT)) 就是 TCP 独有的：
      这一行会触发内核发 SYN、等 SYN+ACK、再回 ACK（三次握手），
      握手成功 connect 才返回；UDP 客户端没有这一步，直接 sendto 就发了。
"""
import socket
import sys

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5200
MSG = sys.argv[3] if len(sys.argv) > 3 else "你好，我是 TCP 客户端 251006112"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:   # SOCK_STREAM = TCP
        s.connect((SERVER_IP, PORT))          # ← 关键行：三次握手就发生在 connect 里
        print(f"[TCP客户端] 已连接到 {SERVER_IP}:{PORT}")
        s.sendall(MSG.encode("utf-8"))        # sendall 保证全部字节都发出去
        data = s.recv(4096)
        print(f"[TCP客户端] 收到回信 {len(data)} 字节：{data.decode('utf-8', errors='replace')!r}")
    print("[TCP客户端] 退出 with 块，套接字关闭 → 会走四次挥手")

if __name__ == "__main__":
    main()
