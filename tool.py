import netifaces
import requests
import time
import socket


def get_ip():
    """
    返回本机当前用于连接校园网的内网IPv4地址。
    优先返回非回环、非链路本地、有网关的接口IP。
    """
    interfaces = netifaces.interfaces()             # 获取所有网络接口
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)        # 检查是否有IPv4地址
        if netifaces.AF_INET not in addrs:
            continue                                # 检查是否有网关（通常表示这个接口是活跃的）
        gateways = netifaces.gateways()
        default_gateway = gateways.get('default', {}).get(netifaces.AF_INET)
        if default_gateway:                         # 如果有默认网关，检查是否匹配该接口
            gateway_ip, iface_name = default_gateway
            if iface_name == iface:                 # 返回该接口的第一个IPv4地址
                ip = addrs[netifaces.AF_INET][0]['addr']
                                                    # 排除回环和链路本地地址
            if not ip.startswith('127.') and not ip.startswith('169.254.'):
                print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} get_ip() ipv4:{ip}")
                return ip                           # 如果没找到，尝试使用socket获取（备选方案）
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('127.'):
            print(f"[INFO]:{time.strftime('%Y-%m-%d%H:%M:%S')} get_ip() ipv4:{ip}")
            return ip
    except:
        print(f"[WARN]:{time.strftime('%Y-%m-%d %H:%M:%S')} get_ip() 获取ipv4失败")
        # 最后回退到主机名解析（可能不准确）
        ip = socket.gethostbyname(socket.gethostname())
        print(f"[WARN]:{time.strftime('%Y-%m-%d %H:%M:%S')} get_ip() 最终ipv4:{ip}(可能错误)")
        return ip


def verify(wifi_type, account, password):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Referer': 'http://10.0.100.3/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/53>'
    }

    params = [
        ('callback', 'dr1003'),
        ('login_method', '1'),
        ('user_account', f',0,{account}@{wifi_type}'),
        ('user_password', f'{password}'),
        ('wlan_user_ip', f'{get_ip()}'),
        ('wlan_user_ipv6', ''),
        ('wlan_user_mac', '000000000000'),
        ('wlan_ac_ip', ''),
        ('wlan_ac_name', 'ME60-CSDX'),
        ('jsVersion', '4.2.1'),
        ('terminal_type', '2'),                     # 1电脑, 2手机
        ('lang', 'zh-cn'),
        ('v', '2315'),
        ('lang', 'zh'),
    ]

    response = requests.get('http://10.0.100.3:801/eportal/portal/login', params=params, headers=headers, verify=False)
    json_str = response.text[response.text.index('(') + 1: response.text.rindex(')')]
    print(f"[INFO]:{time.strftime('%Y-%m-%d %H:%M:%S')} run verify() {json_str}")
    return json_str

