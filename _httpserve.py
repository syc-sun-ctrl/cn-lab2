import http.server, socketserver, os, sys
os.chdir(r"D:\Documents\实验2\www")
handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("127.0.0.1", 8080), handler) as httpd:
    print("serving 127.0.0.1:8080", flush=True)
    httpd.serve_forever()