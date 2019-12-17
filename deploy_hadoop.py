# coding=UTF-8
from fabric.api import *
import fabfile
import os

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('hosts', 'localuser')
env.password = cf.get('hosts', 'localuser_passwd')
env.hosts = cf.get('hosts', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('hosts', 'sudouser')
sudouser_passwd = cf.get('hosts', 'sudouser_passwd')
# 定义软件参数
hadoop_local_file = cf.get('hadoop', 'hadoop_local_file')
hadoop_folder = cf.get('hadoop', 'hadoop_folder')  # 即解压之后的文件夹名称
data_folder = cf.get('hadoop', 'data_folder')
java_home = cf.get('hadoop', 'java_home')
dfs_replication = cf.get('hadoop', 'dfs_replication')
# 需要拼接的字符串
hadoop_upload_file_path = os.path.join('/home', env.user, 'hadoop.tar.gz').replace('\\', '/')
hadoop_home = os.path.join('/home', env.user, hadoop_folder).replace('\\', '/')
hadoop_config_folder = os.path.join(hadoop_home, 'etc/hadoop').replace('\\', '/')
master_ip = cf.get('hadoop', 'master_ip')
slaves = cf.get('hadoop', 'slaves').split(',')


# 安装
def install():
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
        run("sed -i 's:export JAVA_HOME=.*:export JAVA_HOME=" + java_home + ":g' hadoop-env.sh")  # 修改hadoop-env.sh的jdk路径
        # slaves
        run("cat /dev/null > slaves")  # 清空
        for slave in slaves:
            run("echo " + slave + ">> slaves")  # 依次写入
        # core-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/core-default.xml
        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>hadoop.tmp.dir</name>' core-site.xml")  # A base for other temporary directories.其他临时目录的基础，本脚本除了数据目录外未配置其他临时目录，若不配置数据目录则数据目录会在此目录下
        run("sed -i '$i\<value>" + hadoop_home + '/tmp' + "</value>' core-site.xml ")
        run("sed -i '$i\</property>' core-site.xml")

        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>fs.default.name</name>' core-site.xml")  # 真实的hdfs的链接+端口
        run("sed -i '$i\<value>hdfs://" + master_ip + ":9000</value>' core-site.xml ")
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
        run("sed -i '$i\<value>" + master_ip + ":50070</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.namenode.secondary.http-address</name>' hdfs-site.xml")  # SecondaryNameNode链接+端口
        run("sed -i '$i\<value>" + master_ip + ":50090</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.replication</name>' hdfs-site.xml")  # 存储数据的副本数量
        run("sed -i '$i\<value>" + dfs_replication + "</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.permissions</name>' hdfs-site.xml")  # hdfs的权限验证，没有特殊要求关闭即可，这个地方如果开启会造成除env.user外的用户访问hdfs会没有权限
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
        run("sed -i '$i\<value>" + master_ip + ":50030</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        # 写yarn-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-common/yarn-default.xml
        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.hostname</name>' yarn-site.xml")  # 这个经实践，作用是使8088端口的web显示nodes的详细信息
        run("sed -i '$i\<value>" + master_ip + "</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.scheduler.address</name>' yarn-site.xml")  # The address of the scheduler interface.调度程序接口的地址。
        run("sed -i '$i\<value>" + master_ip + ":8030</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.resource-tracker.address</name>' yarn-site.xml")  # 这个经实践，作用是使8088端口的web显示nodes的详细信息
        run("sed -i '$i\<value>" + master_ip + ":8031</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.address</name>' yarn-site.xml")  # The address of the applications manager interface in the RM. resourcemanager的IP+端口
        run("sed -i '$i\<value>" + master_ip + ":8032</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.admin.address</name>' yarn-site.xml")  # The address of the RM admin interface.RM管理界面的地址
        run("sed -i '$i\<value>" + master_ip + ":8033</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.webapp.address</name>' yarn-site.xml")  # nodemanager的IP+端口
        run("sed -i '$i\<value>0.0.0.0:8042</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.webapp.address</name>' yarn-site.xml")  # RM web application的地址，即yarn的web
        run("sed -i '$i\<value>" + master_ip + ":8088</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        if env.host == master_ip:  # 格式化namenode，只格式化master节点
            with cd(hadoop_home):
                run('bin/hdfs namenode -format')


def start():
    if env.host == master_ip:
        with cd(hadoop_home):
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-dfs.sh')


def stop():
    if env.host == master_ip:
        with cd(hadoop_home):
            run('sbin/stop-all.sh')
