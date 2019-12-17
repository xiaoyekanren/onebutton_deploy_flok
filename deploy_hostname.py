# coding=UTF-8
from fabric.api import *
import fabfile

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('hosts', 'sudouser')
env.password = cf.get('hosts', 'sudouser_passwd')
env.hosts = cf.get('hosts', 'hosts').split(",")
# 需要拼接的字符串
real_hosts_sum = len(env.hosts)
env.hostname = cf.get('hostname_to_host', 'hostname').split(",")  # split即以逗号分隔每项
env.hostname_sum = len(env.hostname)
# 配置
real_hosts = cf.get('hostname_to_host', 'real_hosts').split(",")


# 安装
def install():
    # 做判断hostname是否于hosts数量相等
    if env.hostname_sum != real_hosts_sum:
        print('hosts and hostname must one-to-one,please check.......exit')
        exit()
    # 做循环，将IP和主机名写入hosts文件
    i = 0
    while i < env.hostname_sum:
        sudo('echo "' + real_hosts[i] + ' ' + env.hostname[i] + '" >> /etc/hosts')
        i = i + 1
