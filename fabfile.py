# coding=UTF-8
# fabfirc==1.14.1
import configparser
from fabric.api import *

# 读取配置文件password.ini
cf = configparser.ConfigParser()
cf.read('passwd.ini')
# 读取password.ini的全部section内容
# print cf.sections()
# 读取password.ini里面的"server"的内容
# print cf.options("hadoop")
