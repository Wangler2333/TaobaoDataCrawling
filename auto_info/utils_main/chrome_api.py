# encoding=utf-8
from __future__ import absolute_import, unicode_literals, division

import random
import numpy as np
import scipy.interpolate as si
import time
from selenium.webdriver import ActionChains
import logging
from django.conf import settings

logger = logging.getLogger('django')

FIX_DOC_CACHE_KEY = 'delete document.$cdc_asdjflasutopfhvcZLmcfl_;'


def get_current_url(chrome):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return location.href;')


def get_page_source(chrome):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return new XMLSerializer().serializeToString(document);')


def get_element(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '");')


def get_element_href(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").href;')


def get_element_title(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").title;')


def get_element_title_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").title;')


def get_element_src(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").src;')


def get_element_class_name(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").className;')


def get_element_content(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").content;')


def get_element_text(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").textContent;')


def get_element_text_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").textContent;')


def get_element_html_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").innerHTML;')


def get_element_value(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").value;')


def clear_element_value(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").value="";')


def get_element_value_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").value;')


def click_element(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").click();')


def focus_element(chrome, css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'return document.querySelector("' + css_selector + '").focus();')


def get_element_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").click();')


def click_element_within_frame(chrome, css_selector, frame_css_selector):
    return chrome.execute_script(FIX_DOC_CACHE_KEY +
                                 'var frame_doc = document.querySelector(\'' + frame_css_selector +
                                 '\').contentWindow.document;'
                                 'return frame_doc.querySelector("' + css_selector + '").click();')


def get_element_rect(chrome, css_selector):
    #获取元素的大小和相对视口的位置
    return chrome.execute_script(
        FIX_DOC_CACHE_KEY + 'return document.querySelector("' + css_selector + '").getBoundingClientRect();')

def humanize_curve(src_point, dst_point, v, move_interval):
    #src_point=[0,0] dst_point=[1.25,-1.86] v=632 move_inter=0.018
    # 计算中间基准点可取区域
    #[-1, 0] [-1.2899844323179144, 0.47926351030376013] 580.7183639385278 0.018
    x_max_boundary = int(min(1.25 * max(src_point[0], dst_point[0]), int(1366 * 0.9)))  #x_max=1
    x_min_boundary = int(max(0.75 * min(src_point[0], dst_point[0]), int(1366 * 0.1)))  #x_min=136
    y_max_boundary = int(min(1.25 * max(src_point[1], dst_point[1]), int(768 * 0.9)))  #y_max=0
    y_min_boundary = int(max(0.75 * min(src_point[1], dst_point[1]), int(768 * 0.1)))  #y_min=76.8
    # 计算直线距离
    if x_max_boundary < x_min_boundary:
        x_max_boundary,x_min_boundary = x_min_boundary,x_max_boundary
    if y_max_boundary < y_min_boundary:
        y_max_boundary,y_min_boundary = y_min_boundary,y_max_boundary
    line_distance = np.sqrt(np.square(dst_point[0] - src_point[0]) + np.square(dst_point[1] - src_point[1]))
    distance = 0
    points = []
    for i in range(10):
        # 构建基准点，随机选取1~2个中间基准点
        points = [src_point]
        for i in range(random.randint(1, 2)):
            points.append([random.randint(x_min_boundary, x_max_boundary), random.randint(y_min_boundary, y_max_boundary)])
        points.append(dst_point)
        # 计算距离
        distance = 0
        for i in range(1, len(points)):
            point1 = points[i - 1]
            point2 = points[i]
            distance += np.sqrt(np.square(point1[0] - point2[0]) + np.square(point1[1] - point2[1]))
        if distance > 1.25 * line_distance:
            break

    # 计算采样个数，至少两个点
    num = max(int((distance / v) / move_interval), 2)

    points = np.array(points)

    x = points[:, 0]
    y = points[:, 1]

    t = range(len(points))
    ipl_t = np.linspace(0.0, len(points) - 1, num)

    x_tup = si.splrep(t, x, k=2)
    y_tup = si.splrep(t, y, k=2)

    x_list = list(x_tup)
    xl = x.tolist()
    x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

    y_list = list(y_tup)
    yl = y.tolist()
    y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

    x_i = si.splev(ipl_t, x_list)  # x interpolate values
    y_i = si.splev(ipl_t, y_list)  # y_interpolate values
    tmp = zip([int(x) for x in x_i], [int(y) for y in y_i])
    tmp = list(tmp)
    # 潜规则：去除src_point以及重复的点
    result = []
    for i in range(1, len(tmp)):
        if tmp[i][0] != tmp[i - 1][0] or tmp[i][1] != tmp[i - 1][1]:
            result.append(tmp[i])
    return result


# return final position
def move_to_position(driver, src_point, dst_point, v=None):
    final_point = src_point
    if v is None:
        v = abs(random.gauss(settings.MOUSE_MOVE_SPEED_MEAN, settings.MOUSE_MOVE_SPEED_SIGMA))
    prev_point = src_point
    last_time = None
    records = []
    for mouse_x, mouse_y in humanize_curve(src_point, dst_point, v, settings.MOUSE_MOVE_INTERVAL_MEAN):
        offset_x, offset_y = mouse_x - prev_point[0], mouse_y - prev_point[1]
        if last_time is None:
            records.append({'x': mouse_x, 'y': mouse_y, 'interval': 0})
            last_time = time.time() * 1000
        else:
            records.append({'x': mouse_x, 'y': mouse_y, 'interval': time.time() * 1000 - last_time})
            last_time = time.time() * 1000
        ActionChains(driver).move_by_offset(offset_x, offset_y).perform()
        time.sleep(abs(random.gauss(settings.MOUSE_MOVE_INTERVAL_MEAN, settings.MOUSE_MOVE_INTERVAL_SIGMA)))
        prev_point = [mouse_x, mouse_y]
        final_point = [final_point[0] + offset_x, final_point[1] + offset_y]
    message = ''
    for record in records:
        message += '%s\t%s\t%s\n' % (record['x'], 768 - record['y'], record['interval'])
    return final_point
