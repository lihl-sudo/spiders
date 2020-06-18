from capcha.get_cookies import *
import requests
import cv2
import random
import numpy
from selenium.webdriver.common.action_chains import ActionChains


def douban_login(user, passwd):
    # 声明浏览器对象
    # url = 'https://www.douban.com'
    url = 'https://accounts.douban.com/passport/login'
    driver = initial_browser()
    driver.get(url)
    driver.maximize_window()
    # iframe = driver.find_element_by_xpath('//*[@id="anony-reg-new"]/div/div[1]/iframe')
    # # 切换到iframe
    # driver.switch_to.frame(iframe)
    # 通过类名查找  若遇到复合类（即中间有空格）class='account-tab-account on'，选取其中一个类即可，#若其再html中不唯一，可采用[index]定位
    driver.find_element_by_class_name("account-tab-account").click()
    driver.find_element_by_id('username').send_keys(f'{user}')
    driver.find_element_by_id('password').send_keys(f'{passwd}')
    driver.find_element_by_class_name('btn-account').click()
    time.sleep(3)
    # driver.switch_to.default_content()
    # 切换到iframe
    # driver.switch_to.frame(iframe)
    # 定位到滑块验证码的iframe
    # slider_iframe = driver.find_elements_by_xpath('//*[@id="TCaptcha"]/iframe')[0]
    # slider_iframe = driver.find_element_by_xpath('//*[@id="tcaptcha_transform"]')
    # print(slider_iframe)
    # 切换到iframe
    driver.switch_to.frame(0)
    while True:
        action_captcha(driver)
        time.sleep(3)
        iframe = driver.find_elements_by_tag_name("iframe")
        print(iframe)
        if not iframe:
            break
    return driver


# 下载图片到本地
def get_image(img_url, imgname):
    # 以流的形式下载文件
    image = requests.get(img_url, stream=True)
    # str.join()方法用于将序列中的元素以指定的字符(str)连接生成一个新的字符串
    imgName = ''.join(["./", imgname])
    with open(imgName, 'wb') as f:
        for chunk in image.iter_content(chunk_size=1024):  # 循环写入  chunk_size：每次下载的数据大小
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()


# 显示图片
def show(name):
    cv2.startWindowThread()
    cv2.imshow('Show', name)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 使用opencv模块 计算缺口的偏移值
def get_image_offset(background_url, slider_url):
    back_image = 'back_image.png'  # 背景图像命名
    slider_image = 'slider_image.png'  # 滑块图像命名
    get_image(background_url, back_image)
    get_image(slider_url, slider_image)
    # 获取图片并灰度化
    block = cv2.imread(slider_image, 0)
    template = cv2.imread(back_image, 0)
    w, h = block.shape[::-1]
    print(w, h)
    # 二值化后图片名称
    block_name = 'block.jpg'
    template_name = 'template.jpg'
    # 保存二值化后的图片
    cv2.imwrite(block_name, block)
    cv2.imwrite(template_name, template)
    block = cv2.imread(block_name)
    block = cv2.cvtColor(block, cv2.COLOR_RGB2GRAY)
    block = abs(255 - block)
    cv2.imwrite(block_name, block)
    block = cv2.imread(block_name)
    template = cv2.imread(template_name)
    # 获取偏移量
    # 模板匹配，查找block在template中的位置，返回result是一个矩阵，是每个点的匹配结果
    result = cv2.matchTemplate(block, template, cv2.TM_CCOEFF_NORMED)
    x, y = numpy.unravel_index(result.argmax(), result.shape)
    print(x, y)
    # 由于获取到的验证码图片像素与实际的像素有差(实际：340*195 原图：680*390)，故对获取到的坐标进行处理
    offset = y/2
    # 画矩形圈出匹配的区域
    # 参数解释：1.原图 2.矩阵的左上点坐标 3.矩阵的右下点坐标 4.画线对应的rgb颜色 5.线的宽度
    cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
    # show(template)
    return offset, template


# 采用物理加速度位移相关公式按照先快后慢的人工滑动规律进行轨迹计算，
# 同时还采用了模拟人滑动超过了缺口位置再滑回至缺口的情况以使轨迹更契合人工滑动轨迹
def get_tracks(distance):
    distance += 10
    tracks = []
    current = 0
    mid = distance*3/5
    t = random.randint(2, 3)/10
    v0 = 0
    while current < distance:
        if current < mid:
            a = 50
        else:
            a = -70
        v = v0
        v0 = v+a*t
        move = v*t+1/2*a*t**2
        current += move
        tracks.append(round(move, 2))
    return tracks + [0, -1, -1, -1, -2, -2, -2, -1, -1, 0, 0, 1]


def get_captcha_tracks(driver):
    # 获取背景图和滑块图的url
    background_image_url = driver.find_element_by_id('slideBkg').get_attribute('src')
    slider_image_url = driver.find_element_by_id('slideBlock').get_attribute('src')
    time.sleep(2)
    # 获取轨迹
    distance, template = get_image_offset(background_image_url, slider_image_url)
    print(distance-12)
    tracks = get_tracks(distance - random.randint(10, 12))
    return tracks


def move_captcha(driver):
    WebDriverWait(driver, 5, 0.5).until(ec.presence_of_element_located((By.ID, 'tcaptcha_drag_thumb')))
    tracks = get_captcha_tracks(driver)
    print(f"{sum(tracks)}: ", tracks)
    mouse = Con1()
    mouse.position = (840, 680)
    mouse.press(Button.left)
    for index, i in enumerate(tracks):
        mouse.move(i, 0)
        time.sleep(0.03)
        print(index + 1, i)
    mouse.release(Button.left)
    return driver


def action_captcha(driver):
    # 等待加载验证框
    WebDriverWait(driver, 5, 0.5).until(ec.presence_of_element_located((By.ID, 'tcaptcha_drag_thumb')))
    # 定位到滑块按钮
    button = driver.find_element_by_id('tcaptcha_drag_thumb')
    # 拖动操作用到ActionChains类，实例化
    action = ActionChains(driver)
    # perform()用来执行ActionChains中存储的行为
    action.click_and_hold(button).perform()
    # 清除之前的action
    action.reset_actions()
    tracks = get_captcha_tracks(driver)
    print(f"{sum(tracks)}: ", tracks)
    try:
        for index, i in enumerate(tracks):
            action.move_by_offset(xoffset=i, yoffset=0).perform()
            action = ActionChains(driver)
            print(index + 1, i)
        time.sleep(1)
        action.release().perform()
        # show(template)
    except Exception as e:
        print(e)
    return driver


if __name__ == '__main__':
    user = "18601201376"
    passwd = "lhl66666"
    driver = douban_login(user, passwd)
    get_cookies(driver)
