#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tcpserver.py —— 教材第 2 章 TCP 服务器示例（A2、B 部分用）

实验二：HTTP 客户端与 TCP、UDP 协议分析
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明：
1) TCP 服务器必须按 bind -> listen -> accept 的顺序：listen 之后内核才开始接 SYN，
   accept 只是把已经完成三次握手的连接“取”出来。
2) accept 返回新的已连接套接字 conn，它和监听套接字 s 是两个不同的东西：
   s 继续负责接新连接，conn 负责这条连接上的收发。
3) recv 返回空 bytes(b"") 表示对端关闭了连接（收到了 FIN），循环要据此结束，
   否则会一直空转。
"""
import socket

HOST = "0.0.0.0"
PORT = 5200        # TCP 服务器监听端口

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 让端口在程序退出后能马上重用，避免 S3 反复启动时报“端口被占用”
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)                       # backlog=5，允许 5 个连接排队等 accept
        print(f"[TCP服务器] 正在 {HOST}:{PORT} 监听，等待连接……")
        while True:
            conn, addr = s.accept()       # 阻塞，直到有人完成三次握手
            print(f"[TCP服务器] 已接受来自 {addr} 的连接")
            with conn:                    # with 保证退出时关闭 conn（会发 FIN）
                while True:
                    data = conn.recv(4096)
                    if not data:          # b"" 表示对端发了 FIN，连接要关了
                        print(f"[TCP服务器] {addr} 已断开（收到 FIN）")
                        break
                    text = data.decode("utf-8", errors="replace")
                    print(f"[TCP服务器] 收到 {len(data)} 字节：{text!r}")
                    conn.sendall(f"服务器收到 {len(data)} 字节".encode("utf-8"))

if __name__ == "__main__":
    main()
