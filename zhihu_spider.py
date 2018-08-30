import requests
import http.cookiejar
import re
import time
import os.path
from PIL import Image
from lxml import etree


#构造headers
user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':'www.zhihu.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':user_agent,
            }


#使用登录cookies信息
session = requests.session()    #实例化一个session类，session能够用同一个cookies访问不同的url
session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print('cookie未加载')


def get_xsrf():
    #_xrsf是一个动态参数
    start_url = 'https://www.zhihu.com/#signin'
    start_response = session.get(start_url,headers=headers)
    html = start_response.text
    #print(html)
    select = etree.HTML(html)   #使用lxml库解析
    _xsrf = select.xpath('//html/body/input[@name="_xsrf"]/@value')[0]
    return _xsrf

def get_captcha():
    t = str(int(time.time()*1000))
    captcha_url =  'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"   #获得验证码图片的地址，t是需要用到格林威治时间戳
    print(captcha_url)
    r = session.get(captcha_url,headers=headers)
    with open('captcha.jpg','wb') as f:
        f.write(r.content)  #r.content 是二进制内容，r.text为unicode内容

    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入

    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
         print(r'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input('请输入验证码：\n')
    return captcha

def islogin():
    #通过查看用户个人信息来判断是否已经登录
    url = 'https://www.zhihu.com/settings/profile'
    login_code = session.get(url,headers=headers,allow_redirects=False).status_code   #不允许重定向
    if login_code == 200:
        return True
    else:
        return  False

def login(account,secret):
    #通过输入的用户名判断是否是手机号
    if re.match(r'^1\d{10}$',account):
        print("手机号登录 \n")
        post_url = 'https://www.zhihu.com/login/phone_num'
        post_data = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account,
        }
    else:
        if '@' in account:
            print("邮箱登录 \n")
        else:
            print("您输入的账号有问题，请重新输入")
            return 0    #这里的return起的作用是跳出去本次登录
        post_url = 'https://www.zhihu.com/login/email'
        post_data = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account,
        }
    try:
        # 不需要验证码直接登录成功
        login_page = session.post(post_url,data=post_data,headers=headers)
        login_code = login_page.text    #获得网站的内容
        print(login_page.status_code)   #测试是否登录成功
        print(login_code)   #打印网站的内容
    except:
        post_data['captcha'] = get_captcha()
        login_page = session.post(post_url,data=post_data,headers=headers)
        login_code = eval(login_page.text) #eval函数可以把list,tuple,dict和string相互转化
        print(login_code['msg'])
    session.cookies.save() #保存cookies,后续爬取内容时需要


try:
    input = raw_input
except:
    pass

if __name__ == '__main__':
    if islogin():
        print('您已经登录')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        login(account,secret)
