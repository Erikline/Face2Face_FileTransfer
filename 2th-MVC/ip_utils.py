# ip_utils.py
import socket

def get_ip_addr():
    s = None
    ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            if ip_address and not ip_address.startswith("127."):
                ip = ip_address
            else:
                 ip_list = socket.gethostbyname_ex(hostname)[2]
                 non_loopback_ips = [i for i in ip_list if not i.startswith("127.")]
                 if non_loopback_ips:
                    ip = non_loopback_ips[0]
        except socket.gaierror:
            print("警告: 无法通过 gethostbyname/gethostbyname_ex 解析主机名。")
        except Exception as e:
             print(f"警告: IP解析回退期间发生意外错误: {e}")
    finally:
        if s:
            s.close()
    print(f"最终获取到的IP地址: {ip}")
    return ip