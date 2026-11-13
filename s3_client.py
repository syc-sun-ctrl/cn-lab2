#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s3_client.py —— S3 专用：连上服务器后保持连接，用于“交互过程中直接杀掉客户端进程”

实验二：HTTP 客户端与 TCP、UDP 协议分析
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

说明：本程序连上服务器、发一句话，然后把本机端口打印出来，再 sleep 600 秒。
      我们在它 sleep 的时候用任务管理器/Stop-Process 强杀它，
      操作系统会替它关闭套接字（这一步相当于异常退出），
      于是能从抓包里看到 FIN（优雅关闭）或 RST（如果有未读数据被丢弃）。
"""
import socket
import sys
import time

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5200

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_IP, PORT))
    local = s.getsockname()
    print(f"[S3客户端] 已连接，本机端口 = {local[1]}，现在保持连接并 sleep，等你强杀", flush=True)
    s.sendall("S3-我正在交互，然后会被强杀-251006112".encode("utf-8"))
    try:
        data = s.recv(4096)
        print(f"[S3客户端] 收到回信：{data.decode('utf-8', errors='replace')}", flush=True)
    except Exception as e:
        print("[S3客户端] recv 异常:", e, flush=True)
    time.sleep(600)   # 这段时间里进程会被强杀
