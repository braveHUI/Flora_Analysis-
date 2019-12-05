>Step 1, download stable version from [PYSample](http://gitlab.microbiota.git/libranjie/PYSample/tags), untar package

```Bash
tar -zxcf PYSample-2018.Jun5-13.37.tar.gz
```

>Step 2, conda create PYSample

```Bash
conda create -n PYSample python=3
source activate PYSample
pip install -r requirement.txt
```

>Step 3, configure mysql/MariaDB

```Bash
vi /etc/my.cnf
```
```configure
#!includedir /etc/my.cnf.d
[mysqld]
character-set-server=utf8
```
```Bash
systemctl start mariadb.service
systemctl enable mariadb.service
mysql -u root -p
>CREATE USER `PYSample`@`'192.168.1.%'` IDENTIFIED by `'your_passwd'`;
>CREATE DATABASE PYSample;
>GRANT ALL PRIVILEGES on PYSample.* to `PYSample`@`'192.168.1.%'`;
>FLUSH PRIVILEGES;
```

>Step 4, Initial server

```Bash
python manager.py db init
python manager.py db migrate
python manager.py db upgrade
python manager.py insert_role
python manager.py adduser -r Administrator -n `Administrator` -p `password` -u `admin`
```

>Step 5, Open Firewall for PYSample

```Bash
firewall-cmd --permanent --new-service=`PYSample` --add-port=`8080/tcp`
firewall-cmd --permanent --zone=public --add-rich-rule="rule family="ipv4" source address="192.168.1.1/24" service name="`PYSample`" accept"
firewall-cmd --reload
firewall-cmd --zone=public --list-all
```

>Step 6, Install RabbitMQ

```Bash
yum install rabbitmq-server
service rabbitmq-server start
systemctl enable rabbitmq-server.service
```

>Step 7, Install Redis

```Bash
yum install redis
vi /etc/rc.local
```

```vim
# add redis-server
/usr/bin/redis-server /etc/redis.conf &
```

>Step 8, modify config.py

```Bash
vi app/config.py
```

>Step 9, Run Server

```Bash
python manager.py runserver -h 0.0.0.0 -p `8080` --threaded
```

>Step 10, Celery Jobs

* revise `app/application/generateSampleReport.py` & `app/application/generateReportJson.py` for `PYScriptPath`
* `condapath` should be path for bin

```Shell
celery worker -A celery_worker.celery -l info --beat #-c 18
```