FROM python:3-jessie

ENV DISPLAY=:0
ENV TERM=xterm
ENV TZ=Asia/Shanghai
ENV LANG C.UTF-8
ENV CHROME_VERSION 58.0.3029.96
ENV CHROME_DRIVER_VERSION 2.29
# update sources.list
COPY docker/sources.list.jessie /etc/apt/sources.list
COPY docker/chromedriver /usr/local/bin/chromedriver
COPY docker/chrome64_$CHROME_VERSION.deb /tmp/google-chrome.deb
RUN apt-get update && \
    apt-get install -y --assume-yes build-essential python-dev libmysqlclient-dev wget \
    vim supervisor uwsgi uwsgi-plugin-python python-pip Xvfb cron python-numpy python-scipy \
    # google-chrome deps
    libasound2 libgtk2.0-0 libpango1.0-0 libcurl3 libxss1 gconf-service libgconf-2-4 libnspr4 fonts-liberation libappindicator1 libnss3 xdg-utils lsb-release \
    # install fonts
    fonts-ipafont-gothic xfonts-100dpi xfonts-75dpi xfonts-cyrillic xfonts-scalable ttf-wqy-microhei && \
    ln /etc/fonts/conf.d/65-wqy-microhei.conf /etc/fonts/conf.d/69-language-selector-zh-cn.conf && \
    # install google-chrome and chrome-driver
    dpkg -i /tmp/google-chrome.deb && \
    chmod a+x /usr/local/bin/chromedriver && \
    # clean
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /usr/src/info_server/auto_info
COPY docker/sources.list.jessie /etc/apt/sources.list
RUN apt-get update && apt-get install -y supervisor
COPY auto_info/requirement.txt /usr/src/info_server/auto_info
WORKDIR /usr/src/info_server/auto_info
RUN pip install -r requirement.txt -i https://pypi.douban.com/simple
COPY docker/entrypoint.sh /usr/src/info_server/entrypoint.sh
COPY docker/supervisord.conf /etc/supervisor/supervisord.conf
RUN mkdir log_path
COPY auto_info/ /usr/src/info_server/auto_info
EXPOSE 8080
ENTRYPOINT ["/bin/bash", "/usr/src/info_server/entrypoint.sh"]
CMD [""]

