import logging

from lxml import etree
from selenium.webdriver import ActionChains

from utils_main import chrome_api
from utils_main.base_api import enter_next, wait_ele, refresh_page

logger = logging.getLogger('django')


def get_account_type(driver):
    """
    获取支付宝账户类别
    :param driver:
    :return: 支付宝账户类别
    """
    refresh_page(driver, "#main-content table > tbody > tr:nth-child(1) > td:nth-child(2)")
    ele = wait_ele(driver, "#main-content table > tbody > tr:nth-child(1) > td:nth-child(2)")
    if ele:
        account_type_ele = chrome_api.get_element(driver,
                                                  "#main-content table > tbody > tr:nth-child(1) > td:nth-child(2)")
        if account_type_ele:
            account_type = account_type_ele.text
            account_type = account_type.replace(" ", "").replace("\n", "").replace("\t", "")
        else:
            account_type = ""
    else:
        account_type = ""
    return account_type


def get_alipay_data(driver, current_mouse):
    # 进入支付宝引导页面
    tb_zhifubao_binding = {}
    current_mouse = enter_next(driver, current_mouse, '#newAccountManagement > a')
    tb_zhifubao_binding["account_type"] = get_account_type(driver)
    # 等待页面加载
    refresh_page(driver, "p.ui-tipbox-explain > a:nth-child(1)")
    # 进入支付宝页面
    enter_next(driver, current_mouse, "p.ui-tipbox-explain > a:nth-child(1)")
    refresh_page(driver, "td.i-assets-balance")
    try:
        # 点击屏幕
        c_url = driver.current_url.split("/")[2]
        if c_url == "my.alipay.com":
            pass
        elif c_url == "mrchportalweb.alipay.com":
            # 支付宝商家界面
            driver.get("https://personalweb.alipay.com/portal/i.htm")
        else:
            driver.get("https://personalweb.alipay.com/portal/i.htm")
        # 显示支付宝隐藏标签
        hide_label_list = driver.find_elements_by_xpath('//a[text()="显示金额"]')
        if hide_label_list != []:
            a = 1
            b = 1
            c = 1
            num = 0
            while a + b + c:
                num += 1
                if num >= 20:
                    break
                star_list = driver.find_elements_by_xpath("//strong")
                for i, star in enumerate(star_list):
                    if i == 0:
                        try:
                            if "*" in star.text:
                                hide_label_list[0].click()
                            else:
                                a = 0
                        except:
                            continue
                    elif len(star_list) > 3 and i == 3:
                        try:
                            if "*" in star.text:
                                hide_label_list[2].click()
                            else:
                                c = 0
                        except:
                            continue
                    elif len(star_list) > 3 and (i == 1 or i == 2):
                        try:
                            if "*" in star.text:
                                hide_label_list[1].click()
                            else:
                                b = 0
                        except:
                            continue
        html_str = driver.page_source.encode("utf-8").decode()
        alipay_html = etree.HTML(html_str)
        # 支付宝账户
        data_list = alipay_html.xpath('//*[@id="J-userInfo-account-userEmail"]//text()')
        tb_zhifubao_binding["zhifubao_account"] = ''.join(data_list)
        # 花呗总额度
        data_list = alipay_html.xpath('//p[text()="总额度："]//strong//text()')
        tb_zhifubao_binding["huabei_total_credit_amount"] = ''.join(data_list)
        if tb_zhifubao_binding["huabei_total_credit_amount"] == "":
            data_list = alipay_html.xpath('//h3[text()="花呗"]/../..//strong[2]//text()')
            tb_zhifubao_binding["huabei_total_credit_amount"] = ''.join(data_list)
        # 余额宝历史累计收益
        data_list = alipay_html.xpath('//*[@id="J-income-num"]//text()')
        tb_zhifubao_binding["total_profit"] = ''.join(data_list)
        # 支付宝余额
        data_list = alipay_html.xpath('//a[text()="充 值"]/../../../div/strong//text()')
        tb_zhifubao_binding["balance"] = ''.join(data_list)
        # 余额宝账户余额
        data_list = alipay_html.xpath('//tbody[1]//h3[text()="余额宝"]/../../div[2]/p[1]/strong//text()')
        tb_zhifubao_binding["total_quotient"] = ''.join(data_list)
        if tb_zhifubao_binding["total_quotient"] == "":
            data_list = alipay_html.xpath('//a[text()="转出"][1]/../..//strong//text()')
            tb_zhifubao_binding["total_quotient"] = ''.join(data_list)
        # 花呗可用额度
        data_list = alipay_html.xpath('//p[text()="可用额度"]//strong//text()')
        tb_zhifubao_binding["huabei_credit_amount"] = ''.join(data_list)
        if tb_zhifubao_binding["huabei_credit_amount"] == "":
            data_list = alipay_html.xpath('//h3[text()="花呗"]/../..//strong[1]//text()')
            tb_zhifubao_binding["huabei_credit_amount"] = ''.join(data_list)
        # 进入账户管理
        wait_ele(driver, ".userInfo-portrait")
        hua_bei = driver.find_element_by_css_selector(".userInfo-portrait")
        ActionChains(driver).move_to_element(hua_bei).click().perform()
        wait_ele(driver, ".table-list")
        html_str = driver.page_source.encode("utf-8").decode()
        basic_info_html = etree.HTML(html_str)
        # 绑定的手机号
        data_list = basic_info_html.xpath('//tbody/tr[3]/td[1]/span/text()')
        tb_zhifubao_binding["binding_phone"] = ''.join(data_list)
        # 支付宝账户类型
        tb_zhifubao_binding["account_type"] = "个人账户"
        # 支付宝实名认证的姓名
        data_list = basic_info_html.xpath('//*[@id="username"]/text()')
        tb_zhifubao_binding["verified_name"] = ''.join(data_list)
        # 支付宝实名认证的身份证号
        data_list = basic_info_html.xpath('//tbody/tr[1]/td[1]/span[3]/text()')
        tb_zhifubao_binding["verified_id_card"] = ''.join(data_list)
    except Exception as e:
        tb_zhifubao_binding = ""
        logger.error(e)
    return tb_zhifubao_binding, current_mouse
