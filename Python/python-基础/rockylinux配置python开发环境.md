# 安装python

1. 安装前置包

~~~sh
yum install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel libffi-devel gcc gcc-c++ make cmake lrzsz -y
~~~

2. python官网下载python源码包：https://www.python.org/downloads，选择Gzipped source tarball版本

~~~sh
wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz
~~~

2. 编译安装

~~~sh
tar zxvf Python-3.12.5.tgz
mv Python-3.12.5 /usr/local/
cd /usr/local/Python-3.12.5/
./configure
make && make install
~~~

4. 配置环境变量

~~~sh
echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bashrc
# 把export PATH=/usr/local/bin:$PATH 命令写入到当前用户的~/.bashrc，使得每次开启新session时，/usr/local/bin 目录会被自动添加到 PATH 中
source ~/.bashrc
ln -s /usr/local/bin/python3.12 /usr/bin/python
~~~

5. 验证安装版本

~~~sh
python -V
~~~

> 升级版本时，直接下载新版安装包，编译安装，软链接到新版路径即可。
