import os

def set_proxy():
    os.environ['HTTP_PROXY'] = 'http://l0k00au:GNR_welcome22@sysproxy.wal-mart.com:8080'
    os.environ['HTTPS_PROXY'] = 'http://l0k00au:GNR_welcome22@sysproxy.wal-mart.com:8080'

    os.environ['NO_PROXY'] = 'localhost,127.0.0.1,192.168.0.0/16,10.0.0.0/8'

    import requests
    try:
        response = requests.get('https://www.bing.com', timeout=5)
        print("代理配置成功，状态码：", response.status_code)
    except Exception as e:
        print("代理配置失败，错误：", e)

def unset_roxy():
    os.environ['HTTP_PROXY'] = None
    os.environ['HTTPS_PROXY'] = None
