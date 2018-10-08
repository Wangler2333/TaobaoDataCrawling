import json
import logging
import random
import time

from django.conf import settings
from pyvirtualdisplay import Display
from selenium.webdriver import ActionChains

from df_info.models import InfoManager
from utils_list.address_data import get_personal_address
from utils_list.after_sale_data import get_refund_number, get_after_number
from utils_list.order_data import flip_over, get_logistics_information
from utils_list.save_api import save_to_kafka
from utils_list.user_data import get_index_data, get_good_reputation, get_account_info, get_personal_deal_info, \
    get_host_age, get_integral
from utils_list.zhifubao_data import get_alipay_data
from utils_main import chrome_api
from utils_main.base_api import get_driver, login, enter_next, refresh_page, login_by_requests
from utils_main.time_util import get_now_time
from utils_warn.dingding_warning import DingDing

logger = logging.getLogger('django')

INPUT_DELAY = (0.5, 1)


class GetData:

    def __init__(self, user_id, pro_id, city_id, sr):
        self.size = (1366, 768)
        self.user_id = user_id
        self.pro_id = pro_id
        self.city_id = city_id
        self.sr = sr

    def move_get_element_text(self, driver, ele):
        """
        :param driver:
        :param ele:
        :return:
        """
        try:
            chrome_api.get_element(driver, ele)
            current_rect = chrome_api.get_element_rect(driver, ele)
            driver.execute_script("window.scrollTo(0, %d);" % (current_rect['top'] - random.randint(0, 50)))
        except:
            return None
        return chrome_api.get_element_text(driver, ele)

    def run(self, driver, taobao_total_data, size=(1366, 768)):
        tb_user = {}
        tb_order = {}
        try:
            logger.info("user {}: start crawl login_name".format(self.user_id))
            current_mouse = [random.randint(1, int(size[0] * 0.75)), random.randint(2, int(size[1] * 0.75))]
            ActionChains(driver).move_by_offset(xoffset=current_mouse[0], yoffset=current_mouse[1]).perform()
            score, vip_level, login_name, current_mouse = get_index_data(driver, current_mouse)
            tb_user["score"] = score
            tb_user["vip_level"] = vip_level
            tb_user["login_name"] = login_name
            # 进入我的淘宝页面
            current_mouse = enter_next(driver, current_mouse, '#J_SiteNavMytaobao > div.site-nav-menu-hd > a')
            refresh_page(driver,"header.mt-header")
            logistics_information = get_logistics_information(driver)
            # 进入评价管理获取买家累积信用 好评
            cumulative_credit, rate_summary, one_week, one_month, list_bought_href = get_good_reputation(driver,self.user_id)
            tb_user["cumulative_credit"] = cumulative_credit
            tb_user["rate_summary"] = rate_summary
            tb_user["one_week"] = one_week
            tb_user["one_month"] = one_month
            # 进入退款维权页面
            refresh_page(driver, "a.J_MtIndicator")
            current_mouse = enter_next(driver, current_mouse, "a.J_MtIndicator")
            time.sleep(random.uniform(1.5,2.5))
            # 进入退款管理页面
            refund_number,current_mouse = get_refund_number(driver, current_mouse)
            # 进入退款维权页面
            refresh_page(driver, "a.J_MtIndicator")
            current_mouse = enter_next(driver, current_mouse, "a.J_MtIndicator")
            time.sleep(random.uniform(1.5, 2.5))
            # 进入投诉管理页面
            current_mouse = enter_next(driver, current_mouse, "#rulesManager > a")
            # 等待售后管理页面加载完成
            refresh_page(driver, "#rightManager > a")
            # 需要往下滑动几下
            v = abs(random.gauss(200, 20))
            time.sleep(random.uniform(0.2, 0.8))
            driver.execute_script("window.scrollBy(0,%d)" % v)
            # 进入售后管理页面
            current_mouse = enter_next(driver, current_mouse, "#rightManager > a")
            refresh_page(driver,"div.table-hd")
            after_number = get_after_number(driver)
            # 进入账户设置页面
            email, binding_phone, authentication = get_account_info(driver)
            tb_user["email"] = email
            tb_user["binding_phone"] = binding_phone
            tb_user["authentication"] = authentication
            # 进入个人交易信息页面
            logger.info("user {}: start crawl deal info".format(self.user_id))
            name, address = get_personal_deal_info(driver)
            tb_user["name"] = name
            tb_user["address"] = address
            tb_user["host_age"] = get_host_age(driver)
            # 进入收货地址页面
            logger.info("user {}: start crawl address_list".format(self.user_id))
            address_list = get_personal_address(driver)
            taobao_total_data["tb_deliver_addrs"] = address_list
            logger.info("user {}: start crawl zhifubao info".format(self.user_id))
            tb_zhifubao_binding, current_mouse = get_alipay_data(driver, current_mouse)
            # 进入我的积分 获取天猫积分
            tianmao_grade = get_integral(driver)
            tb_user["tianmao_grade"] = tianmao_grade
            taobao_total_data["tb_user"] = tb_user
            # 进入商品列表页
            logger.info("user {}: start crawl goods list".format(self.user_id))
            driver.get(list_bought_href)
            # 等待已买宝贝标签加载完
            refresh_page(driver, "#bought")
            html_0 = driver.page_source
            html_str0 = html_0.encode("utf-8").decode()
            logger.info("user {}: start crawl good detail".format(self.user_id))
            order_list = flip_over(driver, html_str0, address_list)
            tb_order["order_list"] = order_list
            tb_order["refund_number"] = refund_number
            tb_order["after_number"] = after_number
            tb_order["logistics_information"] = logistics_information
            taobao_total_data["tb_order"] = tb_order
            taobao_total_data["tb_order"]["tb_order_num"] = len(taobao_total_data["tb_order"]["order_list"])
            taobao_total_data["tb_zhifubao_binding"] = tb_zhifubao_binding

        except Exception as e:
            taobao_total_data["now_time"] = get_now_time()
            taobao_total_data["status_code"] = "5002"
            taobao_total_data["data_status_message"] = "crawl server error so get data fail"
            taobao_total_data["user_id"] = self.user_id
            DingDing.send(json.dumps(taobao_total_data))
            logger.error('user {}:{}'.format(self.user_id,e))

        else:
            taobao_total_data["now_time"] = get_now_time()
            taobao_total_data["status_code"] = "2002"
            taobao_total_data["data_status_message"] = "get data success"
            taobao_total_data["user_id"] = self.user_id
            InfoManager().save_userinfo(taobao_total_data)
            InfoManager().save_deliveraddrsinfo(taobao_total_data)
            InfoManager().save_orderinfo(taobao_total_data)
            InfoManager().save_productinfo(taobao_total_data)
            InfoManager().save_zhifubaoinfo(taobao_total_data)
            logger.info("user {}: crawl completed.".format(self.user_id))
        finally:
            save_to_kafka(taobao_total_data)
            self.sr.decr(settings.SERVER_RANDOM_UUID)
            driver.quit()

        return taobao_total_data

    def main(self):
        taobao_total_data = {}
        if settings.RUN_ENV == "local":
            if settings.LOGIN_METHOD == "driver":
                driver = get_driver(self.user_id, self.pro_id, self.city_id)
                self.sr.incr(settings.SERVER_RANDOM_UUID)
                driver.set_window_position(0, 0)
                driver.set_window_size(self.size[0], self.size[1])
                logger.info("user {}: start login.".format(self.user_id))
                success = login(driver, taobao_total_data, self.user_id, self.sr)
                if not success:
                    return
                self.run(driver, taobao_total_data, self.size)
            else:
                self.sr.incr(settings.SERVER_RANDOM_UUID)
                logger.info("user {}: start login.".format(self.user_id))
                driver = login_by_requests(taobao_total_data, self.user_id, self.sr, self.pro_id, self.city_id)
                if not driver:
                    return
                self.run(driver, taobao_total_data, self.size)

        else:
            with Display(size=(1366, 768), color_depth=16) as display:
                if settings.LOGIN_METHOD == "driver":
                    logger.info("user {}:start display.".format(self.user_id))
                    driver = get_driver(self.user_id, self.pro_id, self.city_id)
                    self.sr.incr(settings.SERVER_RANDOM_UUID)
                    # 定义窗口位置
                    driver.set_window_position(0, 0)
                    # 定义窗口大小
                    driver.set_window_size(display.size[0], display.size[1])
                    logger.info("user {}: start login.".format(self.user_id))
                    success = login(driver, taobao_total_data, self.user_id, self.sr)
                    if not success:
                        return
                    self.run(driver, taobao_total_data)
                else:
                    self.sr.incr(settings.SERVER_RANDOM_UUID)
                    logger.info("user {}: start login.".format(self.user_id))
                    driver = login_by_requests(taobao_total_data, self.user_id, self.sr, self.pro_id, self.city_id)
                    if not driver:
                        return
                    self.run(driver, taobao_total_data, self.size)
