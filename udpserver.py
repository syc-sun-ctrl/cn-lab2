#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
udpserver.py —— 教材第 2 章 UDP 服务器示例（A1 用，监听端口已改为 5201）

实验二：HTTP 客户端与 TCP、UDP 协议分析
作者：孙宇程  学号：251006112  班级：网工25
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明：
1) UDP 是无连接的：服务器只要 bind 好端口，就能一直 recvfrom 收数据，
   不需要 listen()，也不需要 accept()。
2) recvfrom 会阻塞，直到有任何一个客户端发来数据报；
   返回值是 (数据, 对端地址)，有了对端地址才能把回信发回去。
3) 数据报的边界由一次 recvfrom 对应一次 sendto，不会像 TCP 那样粘在一起。
"""
import socket

HOST = "0.0.0.0"   # 监听所有网卡，这样本机 127.0.0.1 和局域网地址都能访问
PORT = 5201        # A1 要求：把监听端口改成 5201

def main():
    # AF_INET = IPv4，SOCK_DGRAM = UDP（数据报）
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"[UDP服务器] 已绑定 {HOST}:{PORT}，等待客户端发数据……")
        while True:
            data, addr = s.recvfrom(2048)          # 一次收一个数据报
            text = data.decode("utf-8", errors="replace")
            print(f"[UDP服务器] 收到来自 {addr} 的数据：{text!r}")
            # 回一句话，证明双向通信（A1 验收：服务器把客户端发的内容打印出来）
            s.sendto(f"服务器收到：{text}".encode("utf-8"), addr)

if __name__ == "__main__":
    main()
