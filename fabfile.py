# coding=UTF-8
import configparser
from fabric.api import *
import os

# 读取配置文件password.ini
cf = configparser.ConfigParser()
cf.read('passwd.ini')
# --------section-hosts
env.user = cf.get('hosts', 'localuser')
env.password = cf.get('hosts', 'localuser_passwd')
env.hosts = cf.get('hosts', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('hosts', 'sudouser')
sudouser_passwd = cf.get('hosts', 'sudouser_passwd')
# --------section-hostname
real_hosts_sum = len(env.hosts)
env.hostname = cf.get('hostname_to_host', 'hostname').split(",")  # split即以逗号分隔每项
env.hostname_sum = len(env.hostname)
real_hosts = cf.get('hostname_to_host', 'real_hosts').split(",")
# --------section-keyfree_login
hostsum = len(env.hosts)
# --------section-jdk
jdk_local_path = cf.get('jdk', 'jdk_local_path')
jdk_folder = cf.get('jdk', 'jdk_folder')  # 即解压之后的文件夹名称
jdk_upload_path = os.path.join('/home', env.user, 'jdk.tar.gz').replace('\\', '/')
java_home = os.path.join('/home', env.user, jdk_folder).replace('\\', '/')
# --------section-hadoop
hadoop_local_file = cf.get('hadoop', 'hadoop_local_file')
hadoop_folder = cf.get('hadoop', 'hadoop_folder')  # 即解压之后的文件夹名称
data_folder = cf.get('hadoop', 'data_folder')
hadoop_java_home = cf.get('hadoop', 'java_home')
dfs_replication = cf.get('hadoop', 'dfs_replication')
hadoop_upload_file_path = os.path.join('/home', env.user, 'hadoop.tar.gz').replace('\\', '/')
hadoop_home = os.path.join('/home', env.user, hadoop_folder).replace('\\', '/')
hadoop_config_folder = os.path.join(hadoop_home, 'etc/hadoop').replace('\\', '/')
hadoop_master_ip = cf.get('hadoop', 'master_ip')
hadoop_slaves = cf.get('hadoop', 'slaves').split(',')
# --------section-spark
spark_local_file = cf.get('spark', 'spark_local_file')
spark_folder = cf.get('spark', 'spark_folder')
spark_master_ip = cf.get('spark', 'master_ip')
master_public_ip = cf.get('spark', 'master_public_ip')
spark_slaves = cf.get('spark', 'slaves').split(',')
SPARK_WORKER_DIR = cf.get('spark', 'SPARK_WORKER_DIR')
spark_upload_file_path = os.path.join('/home', env.user, 'spark.tar.gz').replace('\\', '/')
spark_home = os.path.join('/home', env.user, spark_folder).replace('\\', '/')
spark_config_folder = os.path.join(spark_home, 'conf').replace('\\', '/')
spark_java_home = cf.get('spark', 'java_home')
hadoop_home = cf.get('spark', 'hadoop_home')
LD_LIBRARY_PATH = os.path.join(hadoop_home, 'lib/native').replace('\\', '/')
# --------section-pg
env.user = cf.get('pg', 'localuser')
env.password = cf.get('pg', 'localuser_passwd')
env.hosts = cf.get('pg', 'hosts').split(',')
# 定义sudo用户参数
pg_sudouser = cf.get('pg', 'sudouser')
pg_sudouser_passwd = cf.get('pg', 'sudouser_passwd')
# 定义软件参数
pg_install_path = cf.get('pg', 'install_path')
pg_data_path = cf.get('pg', 'data_path')
pg_local_file = cf.get('pg', 'pg_local_file')
pg_folder = cf.get('pg', 'pg_folder')
max_connections = cf.get('pg', 'max_connections')
superuser = cf.get('pg', 'superuser')
superuser_passwd = cf.get('pg', 'superuser_passwd')
# 需要拼接的字符串
pg_upload_file_path = os.path.join('/home', env.user, 'pg.tar.gz').replace('\\', '/')
pg_home = os.path.join(pg_install_path, 'pgsql').replace('\\', '/')


def hostname_install():
    # 做判断hostname是否于hosts数量相等
    if env.hostname_sum != real_hosts_sum:
        print('hosts and hostname must one-to-one,please check.......exit')
        exit()
    # 做循环，将IP和主机名写入hosts文件
    i = 0
    while i < env.hostname_sum:
        sudo('echo "' + real_hosts[i] + ' ' + env.hostname[i] + '" >> /etc/hosts')
        i = i + 1


def keyfree_uninstall():
    run('rm -fr ~/.ssh')


def keyfree_install():
    run('rm -rf ~/.ssh/id_rsa*')  # 删除已有的公钥私钥
    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥

    current_path = "".join(os.path.dirname(os.path.abspath('deploy_keyfree_login.py')))  # 获取当前的路径
    current_file_path = os.path.join(current_path, "".join(env.host)).replace('\\', '/')  # 写一个路径+文件名，为下一步骤get提供本地路径+文件名
    get('.ssh/id_rsa.pub', current_file_path)  # 将公钥拿到本地

    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
        os.system('fab keyfree_install2')


def keyfree_install2():
    run('echo "' + keyfree_addrsa() + '" > .ssh/authorized_keys')
    if env.host == env.hosts[-1]:
        os.system('fab keyfree_rmlocalfile')


def keyfree_addrsa():
    rsa_global = ''
    i = 0
    while i < hostsum:
        rsa = open(env.hosts[i]).read()
        rsa_global = rsa_global + rsa
        i += 1
    return rsa_global


def keyfree_rmlocalfile():
    os.remove(env.host)


def jdk_install():
    # 下载/上传
    put(jdk_local_path, jdk_upload_path)
    # run('wget -O jdk.tar.gz https://cloud.tsinghua.edu.cn/f/9a02cc0c958342c09548/?dl=1')
    # 解压&删除
    run('tar -zxvf jdk.tar.gz && rm -f jdk.tar.gz')
    # 写入
    run('echo "">> ~/.bashrc')  # 输出空行
    run('echo "">> ~/.bashrc')  # 输出空行
    run('echo "export JAVA_HOME=' + java_home + '" >> ~/.bashrc')  # JAVA_HOME
    run('echo "export JRE_HOME=' + java_home + '/jre" >> ~/.bashrc')  # JRE_HOME
    run("echo 'export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH' >>~/.bashrc")  # CLASSPATH  # 输出$环境变量必须用单引号
    run("echo 'export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH' >>~/.bashrc")  # PATH  # 输出$环境变量必须用单引号
    run('source ~/.bashrc')  # 立刻生效


def hadoop_install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 下载/上传
    put(hadoop_local_file, hadoop_upload_file_path)
    # run('wget -O hadoop.tar.gz https://cloud.tsinghua.edu.cn/f/a749b29754d7418c9bce/?dl=1')
    # 解压&删除
    run('tar -zxvf hadoop.tar.gz && rm -f hadoop.tar.gz')
    # run('rm -rf ' + hadoop_folder + ' && tar -zxvf hadoop.tar.gz')  # 测试使用，可以免删除
    # 创建目录
    run('mkdir -p ' + hadoop_home + '/tmp')
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建文件夹并授权给hadoop所属用户
        for folder in data_folder.split(','):
            sudo('mkdir -p ' + folder)
            sudo('chown -R ' + env.user + ':' + env.user + ' ' + folder)
    # 修改配置文件
    with cd(hadoop_config_folder):
        # hadoop-env.sh
        run(
            "sed -i 's:export JAVA_HOME=.*:export JAVA_HOME=" + java_home + ":g' hadoop-env.sh")  # 修改hadoop-env.sh的jdk路径
        # slaves
        run("cat /dev/null > slaves")  # 清空
        for slave in hadoop_slaves:
            run("echo " + slave + ">> slaves")  # 依次写入
        # core-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/core-default.xml
        run("sed -i '$i\<property>' core-site.xml")
        run(
            "sed -i '$i\<name>hadoop.tmp.dir</name>' core-site.xml")  # A base for other temporary directories.其他临时目录的基础，本脚本除了数据目录外未配置其他临时目录，若不配置数据目录则数据目录会在此目录下
        run("sed -i '$i\<value>" + hadoop_home + '/tmp' + "</value>' core-site.xml ")
        run("sed -i '$i\</property>' core-site.xml")

        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>fs.default.name</name>' core-site.xml")  # 真实的hdfs的链接+端口
        run("sed -i '$i\<value>hdfs://" + hadoop_master_ip + ":9000</value>' core-site.xml ")
        run("sed -i '$i\</property>' core-site.xml")

        # hdfs-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml
        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.datanode.data.dir</name>' hdfs-site.xml")  # 修改hdfs数据目录，支持多或单挂载路径
        run("sed -i '$i\<value>' hdfs-site.xml")
        run("sed -i '$i" + data_folder + "' hdfs-site.xml")
        run("sed -i '$i\</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.http.address</name>' hdfs-site.xml")  # namenode web管理链接+端口
        run("sed -i '$i\<value>" + hadoop_master_ip + ":50070</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.namenode.secondary.http-address</name>' hdfs-site.xml")  # SecondaryNameNode链接+端口
        run("sed -i '$i\<value>" + hadoop_master_ip + ":50090</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.replication</name>' hdfs-site.xml")  # 存储数据的副本数量
        run("sed -i '$i\<value>" + dfs_replication + "</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run(
            "sed -i '$i\<name>dfs.permissions</name>' hdfs-site.xml")  # hdfs的权限验证，没有特殊要求关闭即可，这个地方如果开启会造成除env.user外的用户访问hdfs会没有权限
        run("sed -i '$i\<value>false</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.webhdfs.enabled</name>' hdfs-site.xml")  # 打开这个，否则访问50070的web浏览数据时会报错
        run("sed -i '$i\<value>true</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")
        # 写mapred-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml
        run('cp mapred-site.xml.template  mapred-site.xml')
        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.jobtracker.http.address</name>' mapred-site.xml")  # 作业跟踪管理器的HTTP服务器访问端口和地址
        run("sed -i '$i\<value>" + hadoop_master_ip + ":50030</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        # 写yarn-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-common/yarn-default.xml
        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.hostname</name>' yarn-site.xml")  # 这个经实践，作用是使8088端口的web显示nodes的详细信息
        run("sed -i '$i\<value>" + hadoop_master_ip + "</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run(
            "sed -i '$i\<name>yarn.resourcemanager.scheduler.address</name>' yarn-site.xml")  # The address of the scheduler interface.调度程序接口的地址。
        run("sed -i '$i\<value>" + hadoop_master_ip + ":8030</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run(
            "sed -i '$i\<name>yarn.resourcemanager.resource-tracker.address</name>' yarn-site.xml")  # 这个经实践，作用是使8088端口的web显示nodes的详细信息
        run("sed -i '$i\<value>" + hadoop_master_ip + ":8031</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run(
            "sed -i '$i\<name>yarn.resourcemanager.address</name>' yarn-site.xml")  # The address of the applications manager interface in the RM. resourcemanager的IP+端口
        run("sed -i '$i\<value>" + hadoop_master_ip + ":8032</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run(
            "sed -i '$i\<name>yarn.resourcemanager.admin.address</name>' yarn-site.xml")  # The address of the RM admin interface.RM管理界面的地址
        run("sed -i '$i\<value>" + hadoop_master_ip + ":8033</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.webapp.address</name>' yarn-site.xml")  # nodemanager的IP+端口
        run("sed -i '$i\<value>0.0.0.0:8042</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run(
            "sed -i '$i\<name>yarn.resourcemanager.webapp.address</name>' yarn-site.xml")  # RM web application的地址，即yarn的web
        run("sed -i '$i\<value>" + hadoop_master_ip + ":8088</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        if env.host == hadoop_master_ip:  # 格式化namenode，只格式化master节点
            with cd(hadoop_home):
                run('bin/hdfs namenode -format')


def hadoop_start():
    if env.host == hadoop_master_ip:
        with cd(hadoop_home):
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-dfs.sh')


def hadoop_stop():
    if env.host == hadoop_master_ip:
        with cd(hadoop_home):
            run('sbin/stop-all.sh')


def spark_install():
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
        for slave in spark_slaves:  # 写Slaves文件
            run("echo " + slave + ">> slaves")
        # spark-env.sh
        run('cp spark-env.sh.template spark-env.sh')
        run("echo 'SPARK_MASTER_PORT=7077' >> spark-env.sh")  # spark默认端口
        run("echo 'SPARK_MASTER_HOST=" + spark_master_ip + "' >> spark-env.sh")  # spark Master节点IP
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


def spark_start():
    with cd(spark_home):
        if env.host == master_public_ip:
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-all.sh')


def spark_stop():
    with cd(spark_home):
        if env.host == master_public_ip:
            run('sbin/stop-all.sh')


def pg_install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(pg_local_file, pg_upload_file_path)
    # run('wget -O pg.tar.gz https://cloud.tsinghua.edu.cn/f/f9aefda2c5d0428fa044/?dl=1')
    # 解压&删除
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建pg_WORKER_DIR文件夹并授权给pg所属用户
        sudo('mkdir -p ' + pg_home)
        sudo('mkdir -p ' + pg_data_path)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + pg_home)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + pg_data_path)

    run('tar -zxvf pg.tar.gz' + ' -C' + pg_install_path)
    #  && rm -f pg.tar.gz

    # 开始配置pg
    with cd(pg_home + '/bin'):  # 进入pg目录
        # 初始化
        run('./initdb -D ' + pg_data_path)
    # 修改默认参数
    with cd(pg_data_path):
        run('sed -i "s:max_connections = 100:max_connections = ' + max_connections + ':g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_idle = 0:tcp_keepalives_idle = 1000:g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_interval = 0:tcp_keepalives_interval = 1000:g" postgresql.conf')
        run('sed -i "s:#tcp_keepalives_count = 0:tcp_keepalives_count = 1000:g" postgresql.conf')
        run('sed -i "s/#listen_addresses =.*/listen_addresses =' + "'" + '*' + "'" + '/g" postgresql.conf')
        run('sed -i "s:#port = 5432:port = 5432:g" postgresql.conf')
        run('echo "host    all             all             0.0.0.0/0               trust" >> pg_hba.conf')
    # 启动pg
    with settings(warn_only=True):
        with cd(pg_home):
            run('bin/pg_ctl -D ' + pg_data_path + ' start')
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
    print '--------------------------------------\nstart way:\nfab pg_start'
    print '--------------------------------------\nstart cli:'
    print pg_home + '/bin/psql -U ' + superuser + ' -d postgres\n--------------------------------------'


def pg_start():
    with settings(warn_only=True):
        with cd(pg_home):
            run('bin/pg_ctl -D ' + pg_data_path + ' start')


def pg_stop():
    with settings(warn_only=True):
        run("ps -ef|grep 'postgres'|awk '{print $2}'|xargs kill -9")
