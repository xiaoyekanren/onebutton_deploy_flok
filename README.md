# auto deploy for TsFloK
------
## 软件列表
>* python==2.7
>* python==3.5
>* pip2
>* pip3
>* jdk==1.8.0_211
>* hadoop==2.8.5
>* spark==2.2.3
>* postgresql==10.10.2
## 实现的功能
>* 免密钥登陆
>* 对应ip和主机名写入hosts
## 树形图
```
├── flok_init
│   ├── apt_cache                   # apt仓库路径
│   │   ├── *.deb
│   ├── deploy_hadoop.py            # hadoop的脚本
│   ├── deploy_hostname.py          # hostname的脚本
│   ├── deploy_jdk.py               # jdk的脚本
│   ├── deploy_keyfree_login.py     # 免密钥的脚本
│   ├── deploy_pg.py                # postgresql的脚本
│   ├── deploy_spark.py             # spark的脚本
│   ├── fabfile.py
│   ├── install.sh                  # 请执行我!!
│   ├── package                     # jdk,hadoop,spark,pg,pip的安装包
│   │   ├── *.gz,*.whl
│   ├── passwd.ini                  # 配置文件!!!!!!,请修改我
│   ├── pip2_cache                  # pip2的本地库
│   │   ├── *whl
│   ├── pip3_cache                  # pip3的本地库
│   │   ├── *whl
│   ├── py2_requirements.txt        # pip2的包列表
│   ├── py3_requirements.txt        # pip3的包列表
│   └── README.md
```
## 实现方式
>* 1 apt 配置本地源,并安装
>* 2 升级pip,并安装pip2,pip3的全部包
>* 3 使用python2的fab命令去部署集群版的hadoop,spark 和 jdk,pg,免密钥,写hosts
>* ps:各类软件的配置见passwd.ini


## 运行方式
```shell script
cd flok_init
chmod +x install.sh
./install.sh
```
## 注意
>* 不提供各类软件包下载，有需要自行下载
>* https://cloud.tsinghua.edu.cn/d/bb82d1a7a4d64cc1bd52/