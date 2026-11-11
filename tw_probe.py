#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tw_probe.py —— S3 辅助：正常连接→发一句→正常关闭，并打印本机端口，
                 方便外部脚本用 netstat 观察该端口在 TIME_WAIT 里待多久。

实验二：HTTP 客户端与 TCP、UDP 协议分析
作者：孙宇程  学号：251006112  班级：网工25
GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2
"""
import socket
import sys

SERVER_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5200

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))
local = s.getsockname()[1]
print(f"LOCAL_PORT={local}", flush=True)
s.sendall("tw_probe-正常关闭测 TIME_WAIT".encode("utf-8"))
s.recv(4096)
s.close()          # 客户端先关：会发 FIN，之后本机端口进入 TIME_WAIT
print("CLOSED", flush=True)
