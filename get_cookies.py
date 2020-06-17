import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from pynput.keyboard import Key, Controller as Con2
from pynput.mouse import Button, Controller as Con1


def initial_browser():
    # 驱动器地址
    # f = r'C:\Users\Administrator\Downloads\Compressed\chromedriver.exe'
    # chrome_options 初始化选项
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 关闭自动测试状态显示 // 会导致浏览器报：请停用开发者模式
    # window.navigator.webdriver还是返回True,当返回undefined时应该才可行。
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 关闭开发者模式
    chrome_options.add_experimental_option("useAutomationExtension", False)
    # 禁止图片加载
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    # 设置中文
    chrome_options.add_argument('lang=zh_CN.UTF-8')
    # 更换头部
    chrome_options.add_argument(
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36')
    # chrome_options.add_argument("--proxy--server=127.0.0.1:8080")
    # 创建浏览器对象
    driver = webdriver.Chrome(options=chrome_options)
    # 设置执行js代码转换模式
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",
    })
    # 打开网站 测试
    # driver.get('https://www.baidu.com/')
    return driver


def vcg_login(user, passwd):
    keyboard = Con2()
    mouse = Con1()
    url = 'https://www.vcg.com/login'
    driver = initial_browser()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    driver.get(url)
    time.sleep(2)
    mouse.position = (1660, 165)
    time.sleep(2)
    for i in range(5):
        keyboard.press(Key.tab)
    keyboard.type(f"{user}")
    # driver.find_element_by_name('id').send_keys('18601201376')
    time.sleep(1)
    keyboard.press(Key.tab)
    keyboard.type(f"{passwd}")
    keyboard.press(Key.enter)
    time.sleep(2)
    while True:
        time.sleep(3)
        mouse.position = (1555, 1080-680)
        mouse.press(Button.left)
        mouse.move(1890-1555, 0)
        mouse.release(Button.left)
        time.sleep(3)
        # WebDriverWait(driver, 5, 0.5).until(ec.presence_of_element_located((By.CLASS_NAME, 'nc-lang-cnt')))
        if driver.find_element_by_class_name('nc-lang-cnt').text == '验证通过':
            break
    # keyboard.press(Key.enter)
    driver.find_element_by_class_name('sign-in-form__btn').click()
    user_name = wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'FqNK-')))
    print(user_name)
    return driver


def get_cookies(driver):
    cookies = driver.get_cookies()  # Selenium为我们提供了get_cookies来获取登录cookies
    cookie = {i["name"]: i["value"] for i in cookies}
    driver.close()  # 获取cookies便可以关闭浏览器
    # 然后的关键就是保存cookies，之后请求从文件中读取cookies就可以省去每次都要登录一次的
    # 当然可以把cookies返回回去，但是之后的每次请求都要先执行一次login没有发挥cookies的作用
    jsonCookies = json.dumps(cookies)  # 通过json将cookies写入文件
    with open('vcgCookies.json', 'w') as f:
        f.write(jsonCookies)
    print(cookie)
    return cookie


if __name__ == '__main__':
    user = "18601201376"
    passwd = "lhl666666"
    driver = vcg_login(user, passwd)
    get_cookies(driver)
