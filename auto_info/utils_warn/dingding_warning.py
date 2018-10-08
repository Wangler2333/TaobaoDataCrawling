# coding=utf-8
import requests
import logging

from django.conf import settings

from utils_warn.consul_tool import ConsulTool

logger = logging.getLogger('django')


class DingDing:
    @staticmethod
    def send(warning_content, service_id=1, warning_level='ERROR'):
        try:
            with requests.Session() as session:
                c = ConsulTool()
                service_uri_list = c.get_service_uri_list(settings.WARNING_SERVER_NAME)
                if service_uri_list and len(service_uri_list):
                    service_uri = service_uri_list[0]
                    ws = settings.DING_DING_SEND_API.format(
                        service_uri, service_id, warning_level, warning_content)
                    session.get(ws)
        except Exception as e:
            logger.error('send ding ding warning error. ', e)
