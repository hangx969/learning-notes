# ssh到单台服务器

~~~sh
ssh user@remote_host /usr/bin/bash << EOF
pwd
ls -l
whoami
EOF
~~~

# ssh到多台服务器

~~~sh
for i in `seq 1 4`; do
ssh -t test@cn01dl00$i "sudo chown munge: /etc/munge/munge.key;sudo chmod 400 /etc/munge/munge.key;sudo chmod 700 /etc/munge/;sudo chmod 711 /var/lib/munge/;sudo chmod 700 /var/log/munge/;sudo chmod 755 /var/run/munge/;sudo chown munge.munge /etc/munge/munge.key;";
done
~~~

