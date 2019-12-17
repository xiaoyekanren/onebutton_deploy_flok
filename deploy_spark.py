# coding=UTF-8
import fabfile
from fabric.api import *
import os

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('hosts', 'localuser')
env.password = cf.get('hosts', 'localuser_passwd')
env.hosts = cf.get('hosts', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('hosts', 'sudouser')
sudouser_passwd = cf.get('hosts', 'sudouser_passwd')
# 定义软件参数
spark_local_file = cf.get('spark', 'spark_local_file')
spark_folder = cf.get('spark', 'spark_folder')
master_ip = cf.get('spark', 'master_ip')
master_public_ip = cf.get('spark', 'master_public_ip')
slaves = cf.get('spark', 'slaves').split(',')
SPARK_WORKER_DIR = cf.get('spark', 'SPARK_WORKER_DIR')
# 需要拼接的字符串
spark_upload_file_path = os.path.join('/home', env.user, 'spark.tar.gz').replace('\\', '/')
spark_home = os.path.join('/home', env.user, spark_folder).replace('\\', '/')
spark_config_folder = os.path.join(spark_home, 'conf').replace('\\', '/')
# 依赖
java_home = cf.get('spark', 'java_home')
hadoop_home = cf.get('spark', 'hadoop_home')
LD_LIBRARY_PATH = os.path.join(hadoop_home, 'lib/native').replace('\\', '/')


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 下载
    put(spark_local_file, spark_upload_file_path)
    # run("wget -O spark.tar.gz https://cloud.tsinghua.edu.cn/f/d0e43e20be9043aaaf79/?dl=1")
    # 解压&删除
    run('tar -zxvf spark.tar.gz  && rm -f spark.tar.gz')
    #

    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建SPARK_WORKER_DIR文件夹并授权给spark所属用户
        sudo('mkdir -p ' + SPARK_WORKER_DIR)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + SPARK_WORKER_DIR)

    # 开始配置spark
    with cd(spark_config_folder):  # 进入配置文件目录
        run('cp slaves.template slaves')
        run("cat /dev/null > slaves")  # 清空slaves文件
        for slave in slaves:  # 写Slaves文件
            run("echo " + slave + ">> slaves")
        # spark-env.sh
        run('cp spark-env.sh.template spark-env.sh')
        run("echo 'SPARK_MASTER_PORT=7077' >> spark-env.sh")  # spark默认端口
        run("echo 'SPARK_MASTER_HOST=" + master_ip + "' >> spark-env.sh")  # spark Master节点IP
        run("echo 'SPARK_LOCAL_IP=" + env.host + "' >> spark-env.sh")  # SPARK_LOCAL_IP
        # SPARK_HOME
        run("echo 'SPARK_HOME=" + spark_home + "' >> spark-env.sh")
        # JAVA_HOME
        run("echo 'JAVA_HOME=" + java_home + "' >> spark-env.sh")
        # SPARK_WORKER_DIR
        run("echo 'SPARK_WORKER_DIR=" + SPARK_WORKER_DIR + "' >> spark-env.sh")
        # SPARK_WORKER_OPTS
        spark_work_opts = '"-Dspark.worker.cleanup.enabled=true -Dspark.worker.cleanup.interval=1800 -Dspark.worker.cleanup.appDataTtl=3600" '
        run("echo 'SPARK_WORKER_OPTS=" + spark_work_opts + "' >> spark-env.sh")
        # LD_LIBRARY_PATH
        if hadoop_home != '':
            run("echo 'LD_LIBRARY_PATH=" + LD_LIBRARY_PATH + "' >> spark-env.sh")


def start():
    with cd(spark_home):
        if env.host == master_public_ip:
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-all.sh')


def stop():
    with cd(spark_home):
        if env.host == master_public_ip:
            run('sbin/stop-all.sh')
