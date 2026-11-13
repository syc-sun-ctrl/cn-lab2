#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
d3_fragment.py —— D3：一次发送 2000 字节的 UDP 报文，观察 IP 分片

实验二：HTTP 客户端与 TCP、UDP 协议分析
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明：
1) 2000 字节是“应用层数据（UDP 载荷）”的长度；加上 UDP 首部 8 字节 = 2008 字节的 IP 载荷，
   再算上 IP 首部 20 字节，整个 IP 数据报 2028 字节，超过以太网 MTU 1500，
   所以必须分片：第一个分片装 1480 字节 IP 载荷（1500-20），剩下 528 字节装第二个分片。
2) 用同一个 2000 字节报文分别发到 127.0.0.1（回环 MTU 极大）和真实网卡地址，
   可以对比“回环不分片、真实网卡分片”。
3) 抓包过滤：ip.addr == <目标IP> and udp
"""
import socket
import sys

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "223.5.5.5"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 53
    nbytes = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    payload = (b"D3-fragment-251006112-" + b"X" * nbytes)[:nbytes]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(3)
        print(f"[D3] 发送 {len(payload)} 字节 UDP 载荷 到 {target}:{port}")
        print(f"[D3] 加上 UDP 首部 8 字节 = {len(payload)+8} 字节 IP 载荷，超过 MTU 1500 就会分片")
        s.sendto(payload, (target, port))
        try:
            data, addr = s.recvfrom(2048)
            print(f"[D3] 收到回信 {len(data)} 字节 来自 {addr}")
        except socket.timeout:
            print("[D3] 3 秒内没有回信（正常，目的端口没有服务）")
        except ConnectionResetError as e:
            print(f"[D3] 收到 ICMP 端口不可达：{e}")

if __name__ == "__main__":
    main()
