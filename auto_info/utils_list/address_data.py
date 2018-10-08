from lxml import etree

from utils_main import chrome_api


def get_personal_address(driver):
    """
    获取收货人，收货地区，收货详细地址，邮编，电话，是否为默认地址
    :param driver:
    :return: address_list
    """
    personal_address_href = chrome_api.get_element_href(driver, "#newDeliverAddress > a")
    driver.get(personal_address_href)
    address_list = []
    html_str = driver.page_source.encode("utf-8").decode()
    html = etree.HTML(html_str)
    add_list_ele = html.xpath("//tbody[@class='next-table-body']/tr")
    for addr_ele in add_list_ele:
        address_dict = {}
        receiver_name = addr_ele.xpath("./td[1]/div/text()")
        if len(receiver_name) > 0:
            address_dict["receiver_name"] = receiver_name[0]
        else:
            address_dict["receiver_name"] = ""
        area = addr_ele.xpath("./td[2]//span/text()")
        if len(area) > 0:
            address_dict["area"] = area[0]
        else:
            address_dict["area"] = ""
        address = addr_ele.xpath("./td[3]/div/text()")
        if len(address) > 0:
            address_dict["address"] = address[0]
        else:
            address_dict["address"] = ""
        zip_code = addr_ele.xpath("./td[4]/div/text()")
        if len(zip_code) > 0:
            address_dict["zip_code"] = zip_code[0]
        else:
            address_dict["zip_code"] = ""
        phone = addr_ele.xpath("./td[5]//span/text()")
        if len(phone) > 0:
            address_dict["phone"] = phone[0]
        else:
            address_dict["phone"] = ""
        is_addr_default = addr_ele.xpath("./td[7]//span/text()")
        if len(is_addr_default) > 0:
            is_addr_default = is_addr_default[0]
            if is_addr_default == "默认地址":
                address_dict["is_default_address"] = "是默认地址"
            else:
                address_dict["is_default_address"] = "不是默认地址"
        else:
            address_dict["is_default_address"] = ""
        address_list.append(address_dict)
    return address_list



