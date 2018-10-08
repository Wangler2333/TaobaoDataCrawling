# -*- coding:utf-8 -*-
import threading

from django.conf import settings
from django.http import JsonResponse

from df_info.models import InfoManager
from utils_main.data_crawl import GetData
from utils_main.redis_util import RedisUtil
from utils_main.time_util import get_now_time


def run_crawl(user_id, pro_id, city_id, sr):
    # 调用爬虫程序
    get_data = GetData(user_id, pro_id, city_id, sr)
    get_data.main()


def code_deal(request):
    # 打开淘宝登录页，获取二维码返回
    user_id = request.GET.get("user_id")
    pro_id = request.GET.get("pro_id", '')
    city_id = request.GET.get("city_id", '')
    if not user_id:
        return JsonResponse({"code": 400, "message": "the parameter error.", "now_time": get_now_time()})
    res = InfoManager().get_code_obj(user_id)
    if res["res"] == 0:
        return JsonResponse({"code": 403, "message": "repeat request.", "now_time": get_now_time()})
    redis_util = RedisUtil()
    sr = redis_util.get_connection()
    id_count = sr.get(settings.SERVER_RANDOM_UUID)
    if id_count is not None and int(id_count) > settings.SERVER_ID_FORBIDDEN_COUNT:
        return JsonResponse(
            {"code": 404, "message": "the network is busy, please try again later", "now_time": get_now_time()})
    crawl = threading.Thread(target=run_crawl, args=(user_id, pro_id, city_id, sr))
    crawl.start()
    for i in range(2):
        code_obj = InfoManager().get_code_info(user_id)
        if code_obj:
            code_url = code_obj.code_url
            code_status = code_obj.code_status
            code_status_message = code_obj.code_status_message
            return JsonResponse(
                {"status_code": code_status, "code_url": code_url, "code_status_message.": code_status_message,
                 "user_id": user_id, "now_time": get_now_time()})

    return JsonResponse(
        {"status_code": 5000, "code_url": "get code_url fail", "code_status_message.": "Failed to get QR code",
         "user_id": user_id, "now_time": get_now_time()})
