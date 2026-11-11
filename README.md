# 实验二 代码说明（HTTP 客户端与 TCP、UDP 协议分析）

- 作者：孙宇程　学号：251006112　班级：网工25
- 运行环境：Python 3.12（Windows 11），只用标准库 socket
- GitHub 公有仓库：https://github.com/syc-sun-ctrl/cn-lab2

## 文件

| 文件 | 说明 |
|---|---|
| `udpserver.py` | A1：UDP 服务器，监听 **5201**，收到数据后打印并回一句话 |
| `udpclient.py` | A1：UDP 客户端，`sendto` 发送、`recvfrom` 收；**没有 connect()**（A 部分要回答的差别就在这） |
| `tcpserver.py` | A2/B：TCP 服务器，监听 **5200**，`bind → listen → accept → recv` 循环 |
| `tcpclient.py` | A2/B：TCP 客户端，`s.connect()` 触发三次握手（第 25 行） |
| `s3_client.py` | S3：连上后 sleep 600 秒，用来演示“交互中强杀客户端进程” |
| `tw_probe.py` | S3 辅助：正常关闭一次连接，用来观察 TIME_WAIT 持续多久 |
| `d3_fragment.py` | D3：一次发送 2000 字节 UDP 载荷，用来观察 IP 分片 |
| `webget.py` | Part D 成品：T1 循环 recv、T2 解析、T3 参数化、T4 recv 统计、T5 抓包对照 |

## 运行方法

```bash
# A1 UDP
python udpserver.py                              # 一个窗口：服务器
python udpclient.py 127.0.0.1 5201 你好           # 另一个窗口：客户端

# A2 / S1 TCP
python tcpserver.py
python tcpclient.py 127.0.0.1 5200 你好

# S3 强杀演示
python tcpserver.py
python s3_client.py 127.0.0.1 5200               # 看到端口后强杀进程，同时抓包

# D3 分片（把目标换成真实网卡对端更容易抓到分片）
python d3_fragment.py 223.5.5.5 53 2000

# Part D
python webget.py www.bjfu.edu.cn 80 / out.html
python webget.py                                  # 参数不够时会打印用法
```

## 抓包

抓包文件：`251006112孙宇程-lab2.pcapng`（64 帧）

| 帧号 | 场景 |
|---|---|
| 1–2 | A1 UDP |
| 3–24 | A2 + S1 TCP 正常交互（两轮连接） |
| 25–34 | S2 顺序颠倒（5 组 SYN / RST,ACK） |
| 35–42 | S3 强杀客户端（末帧 RST,ACK） |
| 43–44 | D2 UDP 无服务器（UDP + ICMP 端口不可达） |
| 45–46 | D4 服务器关闭后发送（UDP + ICMP 端口不可达） |
| 47 | D3 回环发 2000 字节（不分片） |
| 48–49 | D3 真实网卡发 2000 字节（2 个 IP 分片） |
| 50–51 | D1 UDP 头（5301 端口，避开 5201 被当成 iPerf3） |
| 52–64 | webget 访问本机页面 127.0.0.1:8080（握手 / GET / 200 OK / FIN，13 帧） |

过滤建议：`tcp.port==5200`、`udp.port==5201`、`udp.port==5202 or icmp`、`tcp.port==80`。

## 说明

- 本实验按手册“同机”方案：client、server 都跑在本机，走 127.0.0.1，抓 Npcap 的 Loopback 网卡。
- 附录 A 的 Microsoft KM-TEST 环回适配器也装过，但 Npcap 抓不到它的包（0 帧），所以最终用 Npcap 的 Loopback 接口。
- 回环 MTU 极大，因此抓包里 MSS=65495；实验一公网路径 MSS=1460，结构相同。
