from utils_main import chrome_api
from utils_main.base_api import wait_ele, enter_next, refresh_page


def get_refund_number(driver, current_mouse):
    """退款数量"""
    refund_number_ele = wait_ele(driver, "#refundList > a")
    if refund_number_ele:
        current_mouse = enter_next(driver, current_mouse, "#refundList > a")
        refresh_page(driver, "#topContainer_1")
        refund_div = chrome_api.get_element(driver, '#bottomContainer_1 > div:nth-child(2)')
        refund_number = 0
        if refund_div is not None:
            num = 2
            while True:
                current_div = chrome_api.get_element(driver, '#bottomContainer_1 > div:nth-child({})'.format(num))
                if current_div is None:
                    break
                num += 2
                refund_number += 1
        return refund_number, current_mouse
    else:
        refund_number = 0
        return refund_number, current_mouse


def get_after_number(driver):
    """售后服务数量"""
    after_num = 1
    while True:
        tr_after_css = chrome_api.get_element(driver, 'table > tbody:nth-child(1) > tr:nth-child({})'.format(after_num))
        if tr_after_css is None:
            after_num = 0
            break
        after_num += 1
    return after_num
