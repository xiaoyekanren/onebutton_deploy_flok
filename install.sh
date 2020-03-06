#/bin/bash
# deploy flok's dependence,but no flok
# apply to ubuntu 16.04.05,no test other system version
# before install ,you must make sure all hostnames cannot be the same!!!!!!!!!!!!!!!!!!!!!!
# by zhangzhengming 2019-12-13 11:03
#------python config------
pip_whl_path=package/pip-19.3.1-py2.py3-none-any.whl
pip2_cache=pip2_cache
pip3_cache=pip3_cache
py2_requirement=py2_requirements.txt
py3_requirement=py3_requirements.txt
#------apt config------
# sample:
# deb file:///home/ubuntu/flok_init/ apt_cache/
apt_cache="deb file:///home/ubuntu/flok_init/ apt_cache/"
#------system config------
current_user=`whoami`

# change apt sources to local file
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak
sudo chown -R ${current_user}:${current_user} /etc/apt/sources.list
sudo echo ${apt_cache} > /etc/apt/sources.list
sudo apt-get update
sudo apt-get install python2.7 python-pip python3 python3-pip python3-apt libcurl4-openssl-dev -y --allow-unauthenticated

# upgrade pip2 and 3
python3 -m pip install --upgrade ${pip_whl_path} --user
python2 -m pip install --upgrade ${pip_whl_path} --user
echo "export PATH=/home/${current_user}/.local/bin:\${PATH}" >> ~/.bashrc
source ~/.bashrc

# install python 2 and 3's packages
pip2 install --no-index --find-links=${pip2_cache} -r ${py2_requirement} --user
#pip3 install --no-index --find-links=${pip3_cache} -r ${py2_requirement} --user

# use python to install jdk,hadoop,spark,postgresql
#(!!!!before install,mush to modify password.ini,make sure true!!!!)
#------ssh no password------
fab -f deploy_keyfree_login.py install
#-----auto write hostname to hosts,for hadoop-----
fab -f deploy_hostname.py install
#------install jdk------
fab -f deploy_jdk.py install
#------install hadoop,and start------
fab -f deploy_hadoop.py install
fab -f deploy_hadoop.py start
#------install spark,and start------
fab -f deploy_spark.py install
fab -f deploy_spark start
#------install alone node's pg,and start------
fab -f deploy_pg.py install
fab -f deploy_pg.py start
