import datetime
import re
import time

from django.conf import settings
from lxml import etree

from utils_main import chrome_api
from utils_main.base_api import wait_ele, refresh_page_xpath


def get_logistics_information(driver):
    """获取物流信息"""
    logistics_ele = wait_ele(driver, ".s-my-counts.s-content")
    logistics_information = {}
    if logistics_ele:
        index_html = chrome_api.get_page_source(driver)
        taobao_html = etree.HTML(index_html)
        data_list = taobao_html.xpath('//div[@class="s-my-counts s-content"]/ul/li//span//text()')
        moment_dict = {}
        for i, span in enumerate(data_list):
            s = re.findall(r'\D+', span)
            if s != []:
                moment_dict[span] = '0'
            else:
                moment_dict[data_list[i - 1]] = span
        logistics_information["wait_payment"] = moment_dict.get("待付款")
        logistics_information["wait_shipments"] = moment_dict.get("待发货")
        logistics_information["wait_receiving"] = moment_dict.get("待收货")
        logistics_information["wait_evaluate"] = moment_dict.get("待评价")
        logistics_information["refund"] = moment_dict.get("退款")
    else:
        logistics_information["wait_payment"] = ""
        logistics_information["wait_shipments"] = ""
        logistics_information["wait_receiving"] = ""
        logistics_information["wait_evaluate"] = ""
        logistics_information["refund"] = ""
    return logistics_information


def flip_over(driver, html0, address_list):
    """
    拿取订单数据
    :param driver:
    :param html0:
    :param address_list:
    :return:
    """
    html = etree.HTML(html0)
    newest_order_time = html.xpath(
        "//div[@class='index-mod__order-container___1ur4- js-order-container'][1]//tbody[1]/tr[1]/td[1]/label/span[2]/text()")
    newest_time = time.strptime(newest_order_time[0], "%Y-%m-%d")
    newest_time = time.mktime(newest_time)
    order_list = []
    order_list = get_order_list_data(driver, html, address_list, newest_time, order_list)
    return order_list


def split_receiver_data(address):
    if address:
        if ',' in address:
            receiver_list = address.split(',')
        elif '，' in address:
            receiver_list = address.split('，')
        else:
            receiver_list = ["", "", ""]
    else:
        receiver_list = ["", "", ""]
    return receiver_list


def get_good_data(driver, html):
    """
    获取商品金额，名称，数量
    :param driver:
    :return:
    """
    goods_list = []
    taobao_label = html.xpath("//th[contains(text(),'宝贝')]")
    if len(taobao_label) > 0:
        num = 1
        while True:
            goods_dict = {}
            product_judge = html.xpath("//tr[@class='order-item'][%d]" % num)
            if len(product_judge) == 0:
                break
            else:
                product_price = html.xpath("//tr[@class='order-item'][%d]/td[4]//text()" % num)
                if len(product_price) == 0:
                    product_price = html.xpath("//tr[@class='order-item'][%d]/td[5]//text()" % num)
                product_name = html.xpath("//tr[@class='order-item'][%d]/td[1]//a/text()" % num)
                product_quantity = html.xpath("//tr[@class='order-item'][%d]/td[5]//text()" % num)
                if len(product_quantity) == 0:
                    product_quantity = html.xpath("//tr[@class='order-item'][%d]/td[6]//text()" % num)
                if len(product_name) > 0:
                    product_name = product_name[0].replace(" ", "")
                else:
                    product_name = ""
                if len(product_quantity) > 0:
                    product_quantity = product_quantity[0]
                else:
                    product_quantity = ""
                if len(product_price) > 0:
                    product_price = product_price[0]
                else:
                    product_price = ""
            goods_dict["product_name"] = product_name
            goods_dict["product_quantity"] = product_quantity
            goods_dict["product_price"] = product_price
            goods_list.append(goods_dict)
            num += 1
    else:
        num = 1
        while True:
            goods_dict = {}
            product_judge = html.xpath("//li[@class='bought-listform-content']/table[{}]".format(num))
            if len(product_judge) == 0:
                break
            else:
                product_name = html.xpath(
                    "//li[@class='bought-listform-content']/table[{}]//td[1]//a[@title='查看宝贝详情']/text()".format(
                        num))
                product_quantity = html.xpath(
                    "//li[@class='bought-listform-content']/table[{}]//td[3]//text()".format(num))
                product_price = html.xpath(
                    "//li[@class='bought-listform-content']/table[{}]//td[2]//text()".format(num))
                if len(product_name) > 0:
                    product_name = product_name[0]
                else:
                    product_name = ""
                if len(product_price) > 0:
                    product_price = product_price[0]
                else:
                    product_price = ""
                if len(product_quantity) > 0:
                    product_quantity = product_quantity[0]
                else:
                    product_quantity = ""
            goods_dict["product_name"] = product_name
            goods_dict["product_quantity"] = product_quantity
            goods_dict["product_price"] = product_price
            goods_list.append(goods_dict)
            num += 1
    return goods_list


def get_order_detail_data(driver, detail_url, address_list, good_order_dict):
    """
    获取商品详情页数据：商品时间，收货人姓名，手机号，收货地址,商品名称，商品金额，商品数量
    :param driver:
    :param detail_order_list:
    :param status_list:
    :return:
    """
    data_time_list = []
    driver.get("https:" + detail_url)
    refresh_page_xpath(driver, "//span[contains(text(),'您的位置')]")
    html_str = driver.page_source.encode("utf-8").decode()
    html = etree.HTML(html_str)
    baobei_ele = html.xpath("//th[contains(text(),'宝贝')]")
    shangpin_ele = html.xpath("//dd[contains(text(),'商品')]")
    if len(baobei_ele) == 0 and len(shangpin_ele) == 0:
        good_order_dict["transaction_time"] = "0000-00-00 00:00:00"
        good_order_dict["payment_time"] = "0000-00-00 00:00:00"
        good_order_dict["confirmation_time"] = "0000-00-00 00:00:00"
        good_order_dict["receiver_name"] = ""
        good_order_dict["receiver_phone"] = ""
        good_order_dict["receiver_address"] = ""
        good_order_dict["products"] = ""
        return good_order_dict
    times_list = re.findall(r"<span.*?>(\d+-\d+-\d+ \d+:\d+:\d+)</span>?", html_str)
    times_list = set(times_list)
    for i in times_list:
        data_time = datetime.datetime.strptime(i, "%Y-%m-%d %H:%M:%S")
        data_time_list.append(data_time)
    data_time_list.sort()
    if len(data_time_list) >= 3:
        transaction_time = str(data_time_list[0])
        payment_time = str(data_time_list[1])
        confirmation_time = str(data_time_list[-1])
    else:
        transaction_time = str(data_time_list[-1])
        payment_time = "0000-00-00 00:00:00"
        confirmation_time = "0000-00-00 00:00:00"
    good_order_dict["transaction_time"] = transaction_time
    good_order_dict["payment_time"] = payment_time
    good_order_dict["confirmation_time"] = confirmation_time
    # 获取收货地址列表
    for addr_dict in address_list:
        receiver_name = addr_dict["receiver_name"]
        addr_list = html.xpath("//span[contains(text(),'{}')]/text()".format(receiver_name))
        if len(addr_list) == 0:
            addr_list = html.xpath("//dd[contains(text(),'{}')]/text()".format(receiver_name))
        if len(addr_list) == 0:
            addr_list = html.xpath("//td[contains(text(),'{}')]/text()".format(receiver_name))
        if len(addr_list) > 0:
            break
    try:
        addr_list = addr_list[0]
    except Exception as e:
        addr_list = ""
    receiver_list = split_receiver_data(addr_list)
    try:
        receiver_name = receiver_list[0]
    except Exception as e:
        receiver_name = ""
    try:
        receiver_phone = receiver_list[1]
    except Exception as e:
        receiver_phone = ""
    try:
        receiver_address = receiver_list[2]
    except Exception as e:
        receiver_address = ""
    good_order_dict["receiver_name"] = receiver_name
    good_order_dict["receiver_phone"] = receiver_phone
    good_order_dict["receiver_address"] = receiver_address
    goods_list = get_good_data(driver, html)
    good_order_dict["products"] = goods_list
    return good_order_dict


def get_order_list_data(driver, html, address_list, newest_time, order_list):
    """
    在订单列表页获取订单id，订单状态，订单金额，在商品详情页获取其他数据
    :param html_str0:
    :return:
    """
    num = 1
    while True:
        order_judge = html.xpath("//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]" % num)
        if len(order_judge) == 0:
            break
        current_order_time = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//tbody[1]/tr[1]/td[1]/label/span[2]/text()" % num)
        current_time = time.strptime(current_order_time[0], "%Y-%m-%d")
        current_time = time.mktime(current_time)
        if newest_time - current_time > settings.DEADLINE_TIME:
            break
        good_order_dict = {}
        phone_order_ele = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//tbody[2]/tr[1]/td[5]/div/p[2]/a/img" % num)
        if len(phone_order_ele) > 0:
            good_order_dict["phone_order"] = "手机订单"
        else:
            good_order_dict["phone_order"] = "电脑订单"
        order_id = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//tbody[1]//span[contains(text(),'订单号')]/../span[3]/text()" % num)
        status = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//tbody[2]/tr[1]/td[6]//span/text()" % num)
        actual_yuan = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//tbody[2]/tr[1]//strong/span[2]/text()" % num)
        if len(order_id) > 0:
            good_order_dict["order_id"] = order_id[0]
        else:
            good_order_dict["order_id"] = ""
        if len(status) > 0:
            good_order_dict["status"] = status[0]
        else:
            good_order_dict["status"] = ""
        if len(actual_yuan) > 0:
            good_order_dict["actual_yuan"] = actual_yuan[0]
        else:
            good_order_dict["actual_yuan"] = ""
        detail_order_url = html.xpath(
            "//div[@class='index-mod__order-container___1ur4- js-order-container'][%d]//a[contains(text(),'订单详情')]/@href" % num)

        good_order_dict = get_order_detail_data(driver, detail_order_url[0], address_list, good_order_dict)
        order_list.append(good_order_dict)
        num += 1
    return order_list
