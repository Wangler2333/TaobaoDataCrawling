import json
import logging

from django.conf import settings
from kafka import SimpleClient
from kafka import SimpleProducer

from df_info.models import InfoManager

logger = logging.getLogger('django')


def save_code_url(user_id, code_url, code_status, code_status_message):
    try:
        InfoManager().save_codeinfo(user_id, code_url, code_status, code_status_message)
    except Exception as e:
        logger.error(e)


def save_to_kafka(taobao_total_data):
    # 保存数据到kafka
    num = 1
    while num < 3:
        try:
            kafka_client = SimpleClient('{}:{}'.format(settings.KAFKA_IP, settings.KAFKA_PORT))
            producer = SimpleProducer(kafka_client)
            taobao_total_data = json.dumps(taobao_total_data)
            producer.send_messages('{}'.format(settings.KAFKA_TOPIC), taobao_total_data.encode("utf8"))
        except Exception as e:
            num += 1
            logger.error(e)
        else:
            break
