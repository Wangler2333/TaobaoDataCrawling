# encoding=utf-8

import re

WORD_TYPE_ZH = 1
WORD_TYPE_EN = 2
WORD_TYPE_SEPARATOR = 3


def separate_zh_and_en(origin):
    zh_pattern = re.compile('[\u4e00-\u9fa5]+')
    strings = zh_pattern.split(origin)
    zh_strings = zh_pattern.findall(origin)
    for i in range(len(zh_strings)):
        # 倒序插入
        strings = strings[:(2 * i) + 1] + [zh_strings[i]] + strings[(2 * i) + 1:]
    result = []
    for i in range(len(strings)):
        if i % 2 == 0:
            if strings[i] != '':
                result.append({
                    'type': WORD_TYPE_EN,
                    'value': strings[i]
                })
        else:
            if strings[i] != '':
                result.append({
                    'type': WORD_TYPE_ZH,
                    'value': strings[i]
                })
    return result


def split_username(username):
    names = username.split(':', 1)
    if len(names) == 1:
        result = separate_zh_and_en(names[0])
    else:
        result = []
        result.extend(separate_zh_and_en(names[0]))
        result.append({
            'type': WORD_TYPE_SEPARATOR,
            'value': ':'
        })
        result.extend(separate_zh_and_en(names[1]))
    return result
