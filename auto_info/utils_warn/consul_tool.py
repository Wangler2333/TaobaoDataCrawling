# -*- coding: UTF-8 -*-
import consulate

from django.conf import settings

from utils_warn import proxy_adapters


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


class ConsulTool(Singleton):
    def __init__(self):
        self.consul = consulate.Consul(host=settings.CONSUL_HOST,
                                       port=int(settings.CONSUL_PORT),
                                       adapter=proxy_adapters.Request)

    # 获取指定服务的ip:port
    def get_service_uri_list(self, service_name):
        services = self.consul.catalog.service(service_name)

        return [str(service['ServiceAddress']) + ':' + str(service['ServicePort']) for service in services]



