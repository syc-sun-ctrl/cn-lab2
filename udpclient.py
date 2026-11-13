#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
udpclient.py —— 教材第 2 章 UDP 客户端示例（A1 用）

实验二：HTTP 客户端与 TCP、UDP 协议分析
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明：
1) 对比 tcpclient.py 可以明显看到：UDP 客户端【没有 connect()】这一步。
   它只是 sendto(数据, 服务器地址)，把数据报直接丢出去，至于对方在不在听、听不听得到，
   UDP 本身不保证，也不会先握手。这就是“无连接”在代码上的体现。
2) 但 UDP 客户端通常还是会 connect() 一下（不产生网络报文，只是让内核记住对端），
   好处是能用 send()/recv() 并且能收到 ICMP 端口不可达错误。为了和教材一致，
   这里保留 sendto 的写法，D4 里再用 connect 版观察 ICMP。
"""
import socket
import sys

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
SERVER_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5201
MSG = sys.argv[3] if len(sys.argv) > 3 else "你好，我是 UDP 客户端 251006112"

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(5)  # 等回信最多 5 秒，否则程序会一直卡在 recvfrom
        print(f"[UDP客户端] 准备发送给 {SERVER_IP}:{SERVER_PORT}：{MSG!r}")
        s.sendto(MSG.encode("utf-8"), (SERVER_IP, SERVER_PORT))   # 关键行：没有 connect，直接 sendto
        try:
            data, addr = s.recvfrom(2048)
            print(f"[UDP客户端] 收到 {addr} 的回信：{data.decode('utf-8', errors='replace')!r}")
        except socket.timeout:
            print("[UDP客户端] 5 秒没收到回信（UDP 不保证对方在线）")
        except ConnectionResetError as e:
            # Windows 特有：对方端口没开时，系统会收到 ICMP Port Unreachable，
            # 下一次 recvfrom 就抛出 WinError 10054。抓包里能看到那个 ICMP 包。
            print(f"[UDP客户端] 收到 ICMP 端口不可达（WinError 10054）：{e}")
            print("[UDP客户端] 说明目的端口上没有进程在监听；UDP 本身不重传，也不保证送达")

if __name__ == "__main__":
    main()
