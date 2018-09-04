import requests
import os
import json
import re
import sys
import time
from contextlib import closing
requests.packages.urllib3.disable_warnings()


class Spider():
    def __init__(self):
        self.headers = {
        				'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        				'accept-encoding': 'gzip, deflate, br',
        				'accept-language': 'zh-CN,zh;q=0.9',
        				'cache-control': 'max-age=0',
        				'upgrade-insecure-requests': '1',
                        'user-agent': 'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; MI 4S Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.1.3',
                        }
    # 外部调用运行
    def run(self):
        user_id = input('Enter the ID:')
        watermark = input('With watermark or not(0 or 1):')
        if watermark == '0':
        	watermark = True
        else:
        	watermark = False
        video_names, video_urls, nickname = self._parse_userID(user_id)
        if nickname not in os.listdir():
            os.mkdir(nickname)
        print('[INFO]:Number of Videos <%s>' % len(video_urls))
        for num in range(len(video_names)):
            print('[INFO]:Parsing <No.%d> <Url:%s>' % (num+1, video_urls[num]))
            temp = video_names[num].replace('\\', '')
            video_name = temp.replace('/', '')
            self._downloader(video_urls[num], os.path.join(nickname, video_name), watermark)
            print('\n')
        print('[INFO]:All Done...')
    # 视频下载
    def _downloader(self, video_url, path, watermark):
        size = 0
        download_url = self._get_download_url(video_url, watermark)
        with closing(requests.get(download_url, headers=self.headers, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                sys.stdout.write('[File Size]: %0.2f MB\n' % (content_size/chunk_size/1024))
                with open(path, 'wb') as f:
                    for data in response.iter_content(chunk_size=chunk_size):
                        f.write(data)
                        size += len(data)
                        f.flush()
                        sys.stdout.write('[Progress]: %0.2f%%' % float(size/content_size*100) + '\r')
                        sys.stdout.flush()
    # 获得视频下载地址
    def _get_download_url(self, video_url, watermark):
        res = requests.get(url=video_url)
        relu = re.compile(r'playAddr: "(.+)",')
        url = relu.search(res.text).group(1)
        return url if watermark else url.replace('playwm', 'play')
    # 通过user_id获取该用户发布的所有视频
    def _parse_userID(self, user_id):
        video_names = []
        video_urls = []
        unique_id = ''
        while unique_id != user_id:
            search_url = 'https://api.amemv.com/aweme/v1/discover/search/?cursor=0&keyword=%s&count=10&type=1&retry_type=no_retry&iid=17900846586&device_id=34692364855&ac=wifi&channel=xiaomi&aid=1128&app_name=aweme&version_code=162&version_name=1.6.2&device_platform=android&ssmix=a&device_type=MI+5&device_brand=Xiaomi&os_api=24&os_version=7.0&uuid=861945034132187&openudid=dc451556fc0eeadb&manifest_version_code=162&resolution=1080*1920&dpi=480&update_version_code=1622' % user_id
            res = requests.get(url=search_url, headers=self.headers)
            res_dic = json.loads(res.text)
            uid = res_dic['user_list'][0]['user_info']['uid']
            aweme_count = res_dic['user_list'][0]['user_info']['aweme_count']
            nickname = res_dic['user_list'][0]['user_info']['nickname']
            unique_id = res_dic['user_list'][0]['user_info']['unique_id']
        user_url = 'https://www.amemv.com/aweme/v1/aweme/post/?user_id={}&max_cursor=0&count={}'.format(uid, aweme_count)
        res = requests.get(url=user_url, headers=self.headers)
        res_dic = json.loads(res.text)
        i = 1
        for each in res_dic['aweme_list']:
            share_desc = each['share_info']['share_desc']
            if share_desc in ['抖音-原创音乐短视频社区', 'TikTok']:
                video_names.append(str(i) + '.mp4')
                i += 1
            else:
                video_names.append(share_desc + '.mp4')
            video_urls.append(each['share_info']['share_url'])
        return video_names, video_urls, nickname



if __name__ == '__main__':
    sp = Spider()
    sp.run()