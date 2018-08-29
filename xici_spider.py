import requests,random,csv,re,time
from multiprocessing import Pool,cpu_count

"""常见的User_Agent"""
userAgentList =[
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
]

"""爬取代理及多进程验证IP是否可用"""

def getProxyList(url):
    proxyIPs =[] #代理IP数组
    headers = {'User-Agent': random.choice(userAgentList)}
    try:
        res= requests.get(url,headers=headers,timeout = 3) 
        if res.status_code ==200:
            # 获取元组数组，元组是（ip,port）格式
            results = re.findall(r'<td>(\d+\.+\d+\.+\d+\.+\d+)</td>.*?>(.*?)</td>',res.text,re.S) # 使用正则表达式
            for (ip,port) in results:
                proxyIP = 'http://{}:{}'.format(ip,port)
                # 将所有代理IP 添加到数组里
                proxyIPs.append(proxyIP)
            # 创建进程池对代理IP验证
            pool = Pool(cpu_count())
            pool.map(verifyProxy,proxyIPs)
            pool.join()
            pool.close()
        else:
            print('无法获取网页内容')
    except Exception as e:
        print('出错啦:{}'.format(e))
        pass
def verifyProxy(ip):
    # 验证代理是否可用的网站（可以使用其他大型网站）
    verifyUrl = 'https://www.baidu.com'
    proxy = {'http' : ip,
             'https': ip
             }
    headers = {'User-Agent': random.choice(userAgentList)}
    with open('代理IP地址文件.txt', 'a+', newline='') as f:
        writer = csv.writer(f)
        try:
            # 使用代理IP访问百度，如果能够正常访问，则将IP写入txt
            r = requests.get(verifyUrl,proxies = proxy,headers = headers,timeout = 5) #这边的超时时间自行定义
            if r.status_code == 200:
                writer.writerow([ip])
                f.close()
        except Exception as e:
            print('出错啦{}'.format(e))
            pass

def main():
    start = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime((time.time())))

    print('开始时间是：{}'.format(start))

    for page in range(1,3):
        url = 'http://www.xicidaili.com/wt/{}'.format(page)
        getProxyList(url)

    end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((time.time())))

    print('结束时间是：{}'.format(end))


if __name__ == '__main__':
     main()

