# 拉取Python3.7.3镜像
FROM csighub.tencentyun.com/sdet2/tlinux_python3.7:latest

# 创建目录
RUN mkdir -p /var/www/django/message

# 设置当前工作目录
WORKDIR /var/www/django/message

# 拷贝源码
COPY ./ ./

# 执行环境初始化
RUN pip3 install --upgrade pip &&\
    pip3 install -U setuptools && \
    pip3 install uwsgi && \
    pip3 install -r requirements.txt && \
    ln -s /usr/local/python3/bin/uwsgi /usr/bin/uwsgi && \
    mkdir -p log/ && \
    chmod u+x conf/tke/start.sh

# 入口点
ENTRYPOINT ["./conf/tke/start.sh"]