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
# 定义软件参数
jdk_local_path = cf.get('jdk', 'jdk_local_path')
jdk_folder = cf.get('jdk', 'jdk_folder')  # 即解压之后的文件夹名称
# 需要拼接的字符串
jdk_upload_path = os.path.join('/home', env.user, 'jdk.tar.gz').replace('\\', '/')  # Windows's os.path.join会出现反斜杠，用replace将反斜杠替换成斜杠
java_home = os.path.join('/home', env.user, jdk_folder).replace('\\', '/')  # JAVA_HOME  # Windows's os.path.join会出现反斜杠，用replace将反斜杠替换成斜杠


# local
def install():
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
