import requests
from bs4 import BeautifulSoup
import urllib.request
import time
import pytesseract
from PIL import Image
from PIL import ImageEnhance

def yanzheng(filepath):
    '''
    给一个图片路径，识别出来结果并且返回
    '''
    img = Image.open(filepath)
    # 转化为灰度图片
    img = img.convert('L')
    # 二值化处理
    threshold = 140
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    out = img.point(table, '1')
    ret = pytesseract.image_to_string(img)
    print(ret)
    return ret

def main():
    # 创建一个会话
    s = requests.Session()
    i = 1
    while True:
        login_url = 'https://so.gushiwen.org/user/login.aspx?from=http://so.gushiwen.org/user/collect.aspx'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        login_r = s.get(url=login_url, headers=headers)
        # 解析这个网页，获取得到验证码图片的地址
        soup = BeautifulSoup(login_r.text, 'lxml')
        img_src = 'https://so.gushiwen.org' + soup.find('img', id='imgCode')['src']
        # 将图片保存到本地
        img_r = s.get(url=img_src, headers=headers)
        with open('code.png', 'wb') as fp:
            fp.write(img_r.content)
        # 获取得到表单里面的隐藏数据
        views = soup.find('input', id='__VIEWSTATE')['value']
        viewg = soup.find('input', id='__VIEWSTATEGENERATOR')['value']

        code = yanzheng('code.png')
        # 模拟发送post请求
        post_url = 'https://so.gushiwen.org/user/login.aspx?from=http%3a%2f%2fso.gushiwen.org%2fuser%2fcollect.aspx'
        formdata = {
            '__VIEWSTATE': views,
            '__VIEWSTATEGENERATOR': viewg,
            'from': 'http://so.gushiwen.org/user/collect.aspx',
            'email': '783654214@qq.com',
            'pwd': 'lhl666666',
            'code': code,
            'denglu': '登录',
        }
        post_r = s.post(url=post_url, headers=headers, data=formdata)
        # print(post_r.text)
        # 判断有没有登录成功，如果失败，上面的操作接着做，如果成功，循环就可以退出
        if '退出登录' in post_r.text:
            print('第--%s--次登录成功--^_^' % i)
            break
        print('第--%s--次登录失败--o(╯□╰)o' % i)
        i += 1
        time.sleep(2)


if __name__ == '__main__':
    main()
