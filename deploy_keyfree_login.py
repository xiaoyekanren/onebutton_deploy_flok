# coding=UTF-8
# Must already install [sshpass]
import fabfile
from fabric.api import *
import os

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('hosts', 'localuser')
env.password = cf.get('hosts', 'localuser_passwd')
env.hosts = cf.get('hosts', 'hosts').split(",")
# 需要拼接的字符串
hostsum = len(env.hosts)


# 卸载
def uninstall():
    run('rm -fr ~/.ssh')


# 安装
def install():
    run('rm -rf ~/.ssh/id_rsa*')  # 删除已有的公钥私钥
    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥

    current_path = "".join(os.path.dirname(os.path.abspath('deploy_keyfree_login.py')))  # 获取当前的路径
    current_file_path = os.path.join(current_path, "".join(env.host)).replace('\\', '/')  # 写一个路径+文件名，为下一步骤get提供本地路径+文件名
    get('.ssh/id_rsa.pub', current_file_path)  # 将公钥拿到本地

    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
        os.system('fab -f deploy_keyfree_login.py install2')


def install2():
    run('echo "' + addrsa() + '" > .ssh/authorized_keys')
    if env.host == env.hosts[-1]:
        os.system('fab -f deploy_keyfree_login.py rmlocalfile')


def addrsa():
    rsa_global = ''
    i = 0
    while i < hostsum:
        rsa = open(env.hosts[i]).read()
        rsa_global = rsa_global + rsa
        i += 1
    return rsa_global


def rmlocalfile():
    os.remove(env.host)
