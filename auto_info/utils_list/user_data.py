import logging
import random
import time

from lxml import etree

from utils_main import chrome_api
from utils_main.base_api import wait_ele, refresh_page

logger = logging.getLogger('django')

def get_account_info(driver):
    """
    获取邮箱，手机，是否完成身份验证
    :param driver:驱动实例对象
    :return: 返回邮箱，手机，是否完成身份验证
    """
    account_ele_href = chrome_api.get_element_href(driver, "#J_MtMainNav > li:nth-child(2) > a")
    driver.get(account_ele_href)
    refresh_page(driver, "dl.detail-info")
    html_str = driver.page_source.encode("utf-8").decode()
    html = etree.HTML(html_str)
    email_list = html.xpath("//span[contains(text(),'登 录 邮 箱：')]/../span[2]/text()")
    if len(email_list) == 0:
        email = ""
    else:
        email = email_list[0]
    binding_phone_list = html.xpath("//span[contains(text(),'绑 定 手 机：')]/../span[2]/text()")
    if len(binding_phone_list) == 0:
        binding_phone = ""
    else:
        binding_phone = binding_phone_list[0]
        binding_phone = binding_phone.replace("\n","").replace("\t","").replace(" ","")
    authentication_list = html.xpath("//span[contains(text(),'已完成')]/text()")
    if len(authentication_list) == 0:
        authentication = "未完成"
    else:
        authentication = authentication_list[0]
    return email, binding_phone, authentication


def get_personal_deal_info(driver):
    """
    获取个人真实姓名，个人地址
    :param driver: 驱动实例对象
    :return: 个人真实姓名，个人地址
    """
    deal_info_href = chrome_api.get_element_href(driver, "#newAccountProfile > a")
    driver.get(deal_info_href)
    refresh_page(driver, "h2.h2-single")
    name_ele = chrome_api.get_element(driver, "#main-content > form > h2 + ul > li:nth-child(1) > strong")
    if name_ele is None:
        name = ""
    else:
        name = name_ele.text
    address = chrome_api.get_element_value(driver, "#main-content > form > h2 + ul > li:nth-child(6) > input")
    if not address :
        address = ""
    return name, address


def get_host_age(driver):
    """获取用户年龄"""
    year_ele = wait_ele(driver, ".inputtext.input-year")
    if year_ele:
        year = chrome_api.get_element_value(driver, ".inputtext.input-year")
        month = chrome_api.get_element_value(driver, ".inputtext.input-year+input")
        day = chrome_api.get_element_value(driver, ".inputtext.input-year+input+input")
        if year and month and day:
            host_age = year + '-' + month + '-' + day
            brith_time = time.mktime(time.strptime(host_age, "%Y-%m-%d"))
            current_time = time.time()
            age = (current_time - brith_time) // (60 * 60 * 24 * 365)
        else:
            age = ""
    else:
        age = ""
    return age


def get_good_reputation(driver,user_id):
    """买家累积信用  好评率"""
    logger.info("user {}: start crawl rate_summary".format(user_id))
    rate_summary_href = chrome_api.get_element_href(driver, "#myRate > a")
    list_bought_href = chrome_api.get_element_href(driver, "#bought")
    driver.get(rate_summary_href)
    refresh_page(driver, "table.seller-rate-info")
    html_str = driver.page_source.encode("utf-8").decode()
    html = etree.HTML(html_str)
    cumulative_credit_list = html.xpath("//h4[contains(text(),'买家累积信用')]/a/text()")
    if len(cumulative_credit_list) == 0:
        cumulative_credit = ""
    else:
        cumulative_credit = cumulative_credit_list[0]
    rate_summary_list = html.xpath("//p[contains(text(),'好评率')]/strong/text()")
    if len(rate_summary_list) == 0:
        rate_summary = ""
    else:
        rate_summary = rate_summary_list[0]
    data_list = html.xpath('//table[@class="tb-rate-table align-c thm-plain"]/tbody/tr')
    one_week = {}
    one_month = {}
    for i, tr in enumerate(data_list):
        moment_list = tr.xpath('./td//text()')
        if moment_list[0] == "好评":
            key = "good"
        elif moment_list[0] == "中评":
            key = "medium"
        elif moment_list[0] == "差评":
            key = "bad"
        elif moment_list[0] == "总计":
            key = "total"
        one_week[key] = moment_list[1]
        one_month[key] = moment_list[2]
    return cumulative_credit, rate_summary, one_week, one_month, list_bought_href


def get_index_data(driver, current_mouse):
    """
    从主页面获取买家淘气值,会员等级,会员名
    :param driver: 驱动实例对象
    :param current_mouse: 上一次鼠标的位置
    :return: score
    """
    refresh_page(driver, "#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a")
    try:
        rect = chrome_api.get_element_rect(driver,
                                           '#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a')
        offset_x, offset_y = int(random.uniform(2, rect['width'] - 2)), int(random.uniform(2, rect['height'] - 2))
        current_mouse = chrome_api.move_to_position(driver, current_mouse,
                                                    [rect['left'] + offset_x, rect['top'] + offset_y])
        # 获取淘气值
        score_ele = wait_ele(driver, "div.site-nav-user-info p:nth-child(2)")
        if score_ele:
            score = chrome_api.get_element_text(driver, "div.site-nav-user-info p:nth-child(2)")
        else:
            score = ""
        # 获取会员等级
        vip_level_ele = wait_ele(driver, "div.site-nav-user-info p:nth-child(3)")
        if vip_level_ele:
            vip_level = chrome_api.get_element_text(driver, "div.site-nav-user-info p:nth-child(3)")
        else:
            vip_level = ""
        # 获取会员名
        login_name_ele = wait_ele(driver, "a.site-nav-login-info-nick")
        if login_name_ele:
            login_name = chrome_api.get_element_text(driver, "a.site-nav-login-info-nick")
        else:
            login_name = ""
    except Exception as e:
        score = ""
        vip_level = ""
        login_name = ""
    return score, vip_level, login_name, current_mouse


def get_integral(driver):
    """我的积分,页面跳转会出现bug"""
    driver.get("https://pages.tmall.com/wow/jifen/act/point-details")
    refresh_page(driver, "div#pointContent")
    wait_ele(driver, "div#pointContent")
    html_str = driver.page_source.encode("utf-8").decode()
    html = etree.HTML(html_str)
    tianmao_grade_list = html.xpath("//span[contains(text(),'可用的积分')]/../span[2]/text()")
    if len(tianmao_grade_list) == 0:
        tianmao_grade = ""
    else:
        tianmao_grade = tianmao_grade_list[0]
    return tianmao_grade
