import requests,csv
from bs4 import BeautifulSoup


#将爬取的数据存到excel中
csvfile = open('E:\lagou.csv','wt',newline='')
writer = csv.writer(csvfile)
def store(job,type,company,salary,experience,region):
    csvrow = [job,type,company,salary,experience,region]
    writer.writerow(csvrow)

#获取拉钩网岗位的链接

url = 'https://www.lagou.com' 
wb_data = requests.get(url)
soup = BeautifulSoup(wb_data.text,'lxml')
urls = []
job_links = []
def get_urls(url):
    we_data = requests.get(url)
    soup = BeautifulSoup(we_data.text,'lxml')
    job_urls = soup.select('#sidebar > div.mainNavs > div.menu_main.job_hopping > a')
    for job_url in job_urls:
        job_url = job_url.get('href')
        urls.append(job_url)

    for url in urls:
        links = [url + '{}'.format(n) for n in range(1,5,1)]
        for link in links:
            job_links.append(link)


#获取具体岗位的信息

def get_job_info(jon_url):
    soup = BeautifulSoup(wb_data.text,'lxml')
    #print(soup)
    jobs = soup.select('#s_position_list > ul > li > div.list_item_top > div.position > div.p_pop > a >h2')
    company = soup.select('#s_position_list > ul > li > div.list_item_top > div.company > div.company_name > a >a')
    experience = soup.select('#s_position_list > ul > li > div.list_item_top > div.position > div.p_bot > div')
    types = soup.select('#s_position_list > ul > li > div.company > div.industry')
    regiones = soup.select('#s_position_list > ul > li > div.list_item_top > div.position > div.p_top > a > span >em')
    print(types)
    for job,company,experience,type,region in zip(jobs,company,experience,types,regiones):
        job = job.get_text()
        type = type.get_text().strip('\n').strip()
        company = company.get_text()
        salary = experience.get_text().split('\n'[2])
        region = region.get_text()
        store(job,type,company,salary,experience,region)
        print('公司名称：',company,'岗位名称：',job,'薪水：',salary,'经验：',experience,'公司类型：',type,'地区：',region)
        print('-------------------')
get_urls(url)
for link in job_links:
    get_job_info(link)
























