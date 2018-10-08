import datetime


def get_now_time():
    # 记录当前时间
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time
