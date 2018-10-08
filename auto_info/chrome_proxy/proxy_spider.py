import json
import logging
import requests
import time

logger = logging.getLogger('django')


class ZhiMaProxySpider():
    def __init__(self, region_id='', city_id='', get_num=1):
        self.region_id = region_id
        self.city_id = city_id
        self.get_num = get_num
        self.url = "http://webapi.http.zhimacangku.com/getip"

    def gen_para(self):
        return {
            "time": 1,
            "pro": self.region_id,
            "city": self.city_id,
            "num": self.get_num,
            "type": 2,
            "yys": 0,
            "port": 1,
            # "pack": 25740,
            "ts": 1,
            "ys": 0,
            "cs": 1,
            "lb": 1,
            "sb": 0,
            "pb": 45,
            "mr": 1,
            "regions": ""
        }

    def get_proxy_info(self):
        retry_times = 0
        while True and retry_times < 5:
            try:

                response = requests.get(self.url, params=self.gen_para())
                if response.ok:
                    proxy_json_str = response.content.decode()
                    proxy_dict = json.loads(proxy_json_str)

                    if proxy_dict.get("success"):
                        return proxy_dict
                    else:
                        response_code = proxy_dict.get("code")
                        # 需要人工介入的情况
                        if response_code == 114 or response_code == 116 or response_code == 118 or response_code == 121:
                            logger.error(proxy_dict.get("msg"), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                          proxy_dict)
                            logger.error(proxy_info)
                            # todo send ding ding warning
                        # 请更换地区等条件重新生成api连接地址
                        elif proxy_dict.get("code") == 115:
                            logger.info(proxy_dict.get("msg"), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                         proxy_dict)
                            logger.info(proxy_dict)
                            if self.city_id and retry_times > 2:
                                self.city_id = ''
            # 其他异常暂不处理
            except Exception as e:
                logger.error(e)
            finally:
                retry_times += 1

        return None


if __name__ == '__main__':
    zs = ZhiMaProxySpider('410000', '410400')
    proxy_info = zs.get_proxy_info()
    print("*" * 20, proxy_info, "*" * 20)
