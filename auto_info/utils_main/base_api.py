import json
import random
import re

import time

import os

import requests
from django.conf import settings
from selenium.webdriver import ActionChains
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import logging

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from chrome_proxy.proxy_spider import ZhiMaProxySpider
from utils_main import chrome_api
from utils_list.save_api import save_code_url, save_to_kafka

logger = logging.getLogger('django')

login_url = "https://login.taobao.com"


def wait_ele(driver, ele, timeout=10):
    # 将显示等待时间封装
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele)))
    except Exception as e:
        ele = None
        logger.error(e)
    return ele


def refresh_page(driver, ele):
    # 刷新页面
    num = 1
    while num < 3:
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele)))
        except Exception as e:
            num += 1
            driver.refresh()
            logger.error(e)
        else:
            break
    if num >= 3:
        raise Exception('refresh page fail.')


def refresh_page_xpath(driver, ele):
    # 刷新页面
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, ele)))
    except Exception as e:
        driver.refresh()
        logger.error(e)


def enter_next(driver, current_mouse, ele):
    """
    :param driver: 驱动实例对象
    :param current_mouse: 上一次的鼠标位置
    :return: 当前的鼠标位置
    """
    rect = chrome_api.get_element_rect(driver, ele)
    offset_x, offset_y = int(random.uniform(2, rect['width'] - 2)), int(random.uniform(2, rect['height'] - 2))
    current_mouse = chrome_api.move_to_position(driver, current_mouse,
                                                [rect['left'] + offset_x, rect['top'] + offset_y])
    time.sleep(random.uniform(0.5, 1.0))
    ActionChains(driver).click().perform()
    return current_mouse


def get_proxy(pro_id, city_id):
    enable_proxy = os.getenv("ENABLE_PROXY", 'False').upper() == 'TRUE'
    proxy = None
    if enable_proxy and pro_id:
        ps = ZhiMaProxySpider(pro_id, city_id)
        pi = ps.get_proxy_info()
        if pi:
            proxy = pi['data'][0]['ip'] + ":" + str(pi['data'][0]['port'])
    proxy = '132.232.43.138:31080'
    return proxy


def get_driver(user_id, pro_id, city_id):
    num = 1
    while num <= 3:
        try:
            proxy = get_proxy(pro_id, city_id)

            executable_path = settings.CHROMEDRIVER
            capabilities = DesiredCapabilities.CHROME.copy()

            if 'chromeOptions' not in capabilities:
                capabilities['chromeOptions'] = {
                    'args': [],
                    'binary': '',
                    'extensions': [],
                    'prefs': {}
                }

            if 'chromeOptions' not in capabilities:
                capabilities['chromeOptions'] = {
                    'args': [],
                    'binary': '',
                    'extensions': [],
                    'prefs': {}
                }

            if proxy:
                capabilities['proxy'] = {
                    'httpProxy': proxy,
                    'ftpProxy': proxy,
                    'sslProxy': proxy,
                    # 'noProxy': 'redirect.' + urlparse(LOGIN_URL).netloc,
                    'proxyType': 'MANUAL',
                    'class': 'org.openqa.selenium.Proxy',
                    'autodetect': False
                }

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-setuid-sandbox')
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)

            chrome = webdriver.Chrome(
                executable_path=executable_path,
                chrome_options=chrome_options,
                desired_capabilities=capabilities,
                service_log_path='chrome.log'
            )
        except Exception as e:
            num += 1
            logger.error('user {}:{}'.format(user_id, e))
            chrome.quit()
        else:
            break
    logger.info('user {}: get driver success'.format(user_id))
    return chrome


def login_by_requests(taobao_total_data, user_id, sr, pro_id, city_id, size=(1366, 768)):
    scan_flag = False
    try:
        proxy = get_proxy(pro_id, city_id)

        request = requests.Session()

        if proxy:
            proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
            request.proxies.update(proxies)

        res = request.get("https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do")
        r_dict = json.loads(res.text)
        if r_dict and 'url' in r_dict and 'lgToken' in r_dict:
            code_url = r_dict.get("url")
            if not str(code_url).startswith('http:'):
                code_url = 'http:' + code_url
            save_code_url(user_id, code_url, "2000", "Success to get QR code")
            # 验证用户是否扫码
            request_time = int(time.clock() * 800)
            lg_token = r_dict.get("lgToken")

            time_count = 180
            time_num = 0
            while time_num < time_count:
                request_time += int(time.clock() * 800)
                ts = str(round(time.time() * 1000)) + '_' + str(request_time)
                j_s = str(request_time + 1)

                params = {
                    "lgToken": lg_token,
                    "defaulturl": "",
                    "_ksTS": ts,
                    "callback": j_s
                }
                res = request.get("https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do", params=params)
                text_str = res.text
                if text_str and "code" in text_str:
                    code = re.search(r'.*?code":"(.*?)"', text_str).group(1)
                    logger.info("code {} ok".format(code))
                    if code == "10006":
                        url = re.search(r'.*?url":"(.*?)"', text_str).group(1)
                        driver = get_driver(user_id, pro_id, city_id)
                        logger.info("start open taobao")
                        driver.get('https://www.taobao.com/')
                        retry_times = 0
                        while retry_times < 30:
                            if driver.current_url == "https://www.taobao.com/":
                                break
                            driver.get('https://www.taobao.com/')
                            retry_times += 1
                            time.sleep(1)
                        if retry_times >= 30:
                            logger.warning(user_id + ": can't open taobao.")
                            sr.decr(settings.SERVER_RANDOM_UUID)
                            driver.quit()
                            return None
                        for cookie in request.cookies:
                            # "path", "domain", "secure", "expiry"
                            driver.add_cookie({'domain': cookie.domain, 'path': cookie.path, 'name': cookie.name,
                                               'value': cookie.value})

                        driver.set_window_position(0, 0)
                        # 定义窗口大小
                        driver.set_window_size(size[0], size[1])
                        driver.get(url)
                        retry_times = 0
                        while retry_times < 30:
                            if driver.current_url == "https://www.taobao.com/":
                                scan_flag = True
                                break
                            retry_times += 1
                            time.sleep(1)
                        if retry_times >= 30:
                            logger.warning(user_id + ': user need confirm again.')
                            sr.decr(settings.SERVER_RANDOM_UUID)
                            driver.quit()
                            return None

                        taobao_total_data["status_code"] = "2001"
                        taobao_total_data["user_status_message"] = "user scan QR code"
                        taobao_total_data["user_id"] = user_id
                        try:
                            save_to_kafka(taobao_total_data)
                            return driver
                        except Exception as e:
                            logger.error('user {}:{}'.format(user_id, e))

                    # 验证码失效
                    elif code == "10004":
                        break

                time.sleep(2)
                time_num += 2
        else:
            save_code_url(user_id, "get code_url fail", "5000", "Failed to get QR code")
            return None
    except Exception as e:
        # 如果15秒没有获取到，就保存失败状态
        save_code_url(user_id, "get code_url fail", "5000", "Failed to get QR code")
        logger.error('user {}:{}'.format(user_id, e))

    if not scan_flag:
        taobao_total_data["status_code"] = "5001"
        taobao_total_data["user_status_message"] = "QR code overtime so get data fail"
        taobao_total_data["user_id"] = user_id
        save_to_kafka(taobao_total_data)
        sr.decr(settings.SERVER_RANDOM_UUID)
        return None


def login(driver, taobao_total_data, user_id, sr, size=(1366, 768)):
    try:
        # 定义窗口位置
        driver.set_window_position(0, 0)
        # 定义窗口大小
        driver.set_window_size(size[0], size[1])
        current_mouse = [random.randint(1, int(size[0] * 0.75)), random.randint(2, int(size[1] * 0.75))]
        ActionChains(driver).move_by_offset(xoffset=current_mouse[0], yoffset=current_mouse[1]).perform()
        # # 请求登陆页面
        driver.get(login_url)
    except Exception as e:
        refresh_page(driver, "#J_QRCodeImg > img")
        ele = wait_ele(driver, "#J_QRCodeImg > img")
        if not ele:
            save_code_url(user_id, "get code_url fail", "5000", "Failed to get QR code")
            sr.decr(settings.SERVER_RANDOM_UUID)
            driver.quit()
            logger.error('user {}:{}'.format(user_id, e))
            return None
    finally:
        try:
            wait_ele(driver, "#J_QRCodeImg > img")
            code_url = chrome_api.get_element_src(driver, "#J_QRCodeImg > img")
        except Exception as e:
            # 如果15秒没有获取到，就保存失败状态
            save_code_url(user_id, "get code_url fail", "5000", "Failed to get QR code")
            logger.error('user {}:{}'.format(user_id, e))
            return None
        else:
            save_code_url(user_id, code_url, "2000", "Success to get QR code")
            time_num = 0
            time_count = 180
            # 让浏览器停留在登陆页面
            while time_num < time_count:
                current_url = driver.current_url
                if current_url != "https://login.taobao.com/":
                    taobao_total_data["status_code"] = "2001"
                    taobao_total_data["user_status_message"] = "user scan QR code"
                    taobao_total_data["user_id"] = user_id
                    try:
                        save_to_kafka(taobao_total_data)
                    except Exception as e:
                        logger.error('user {}:{}'.format(user_id, e))
                    return current_mouse
                else:
                    time.sleep(5)
                    time_num += 5
            if time_num >= 180:
                taobao_total_data["status_code"] = "5001"
                taobao_total_data["user_status_message"] = "QR code overtime so get data fail"
                taobao_total_data["user_id"] = user_id
                save_to_kafka(taobao_total_data)
                sr.decr(settings.SERVER_RANDOM_UUID)
                driver.quit()
                return None
