# coding=UTF-8
import fabfile
from fabric.api import *
import os

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('pg', 'localuser')
env.password = cf.get('pg', 'localuser_passwd')
env.hosts = cf.get('pg', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('pg', 'sudouser')
sudouser_passwd = cf.get('pg', 'sudouser_passwd')
# 定义软件参数
install_path = cf.get('pg', 'install_path')
data_path = cf.get('pg', 'data_path')
pg_local_file = cf.get('pg', 'pg_local_file')
pg_folder = cf.get('pg', 'pg_folder')
max_connections = cf.get('pg', 'max_connections')
superuser = cf.get('pg', 'superuser')
superuser_passwd = cf.get('pg', 'superuser_passwd')
# 需要拼接的字符串
pg_upload_file_path = os.path.join('/home', env.user, 'pg.tar.gz').replace('\\', '/')
pg_home = os.path.join(install_path, 'pgsql').replace('\\', '/')


# 依赖


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(pg_local_file, pg_upload_file_path)
    # run('wget -O pg.tar.gz https://cloud.tsinghua.edu.cn/f/f9aefda2c5d0428fa044/?dl=1')
    # 解压&删除
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建pg_WORKER_DIR文件夹并授权给pg所属用户
        sudo('mkdir -p ' + pg_home)
        sudo('mkdir -p ' + data_path)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + pg_home)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + data_path)

    run('tar -zxvf pg.tar.gz' + ' -C' + install_path)
    #  && rm -f pg.tar.gz

    # 开始配置pg
    with cd(pg_home + '/bin'):  # 进入pg目录
        # 初始化
        run('./initdb -D ' + data_path)
    # 修改默认参数
    with cd(data_path):
        run('sed -i "s:max_connections = 100:max_connections = ' + max_connections + ':g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_idle = 0:tcp_keepalives_idle = 1000:g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_interval = 0:tcp_keepalives_interval = 1000:g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_count = 0:tcp_keepalives_count = 1000:g" postgresql.conf')
        run('sed -i "s/#listen_addresses =.*/listen_addresses =' + "'" +  '*'  +"'" + '/g" postgresql.conf')
        run('sed -i "s:#port = 5432:port = 5432:g" postgresql.conf')
        run('echo "host    all             all             0.0.0.0/0               trust" >> pg_hba.conf')
    # 启动pg
    with settings(warn_only=True):
        with cd(pg_home):
            run('bin/pg_ctl -D ' + data_path + ' start')
    # 新建超级用户
    with cd(pg_home + '/bin'):
        with settings(prompts={
            'Enter password for new role: ': superuser_passwd,
            'Enter it again: ': superuser_passwd
        }):
            run('./createuser -dlrs ' + superuser + ' -P')
    # 杀了PG
    with settings(warn_only=True):
        run("ps -ef|grep 'postgres'|awk '{print $2}'|xargs kill -9;echo 'already killed'")
    # 输出结果,输出host必须带",".join(),否则会显示[u]
    print '--------------------------------------\nfinish install pg\n'
    print 'host is %s,\npg user is %s,\npassword is %s\n' % (",".join(env.hosts), superuser, superuser_passwd)
    print '--------------------------------------\nstart way:\nfab -f deploy_pg.py start'
    print '--------------------------------------\nstart cli:'
    print pg_home + '/bin/psql -U ' + superuser + ' -d postgres\n--------------------------------------'


def start():
    with settings(warn_only=True):
        with cd(pg_home):
            run('bin/pg_ctl -D ' + data_path + ' start')


def stop():
    with settings(warn_only=True):
        run("ps -ef|grep 'postgres'|awk '{print $2}'|xargs kill -9")
