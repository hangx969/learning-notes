sudo mkdir /mnt/aliyun
if [ ! -d "/etc/smbcredentials" ]; then
sudo mkdir /etc/smbcredentials
fi
if [ ! -f "/etc/smbcredentials/onprem.cred" ]; then
    sudo bash -c 'echo "username=onprem" >> /etc/smbcredentials/onprem.cred'
    sudo bash -c 'echo "password=lTi3c5vzyvjaq16Q/fSXFaA7lUvaZB9D0BoHVtSxdWlTv5zx80HK9W7MaSjVnHFgoLeY9wc0pz7d+AStJCWYsQ==" >> /etc/smbcredentials/onprem.cred'
fi
sudo chmod 600 /etc/smbcredentials/onprem.cred

sudo bash -c 'echo "//onprem.file.core.chinacloudapi.cn/aliyun /mnt/aliyun cifs nofail,credentials=/etc/smbcredentials/onprem.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30" >> /etc/fstab'
sudo mount -t cifs //onprem.file.core.chinacloudapi.cn/aliyun /mnt/aliyun -o credentials=/etc/smbcredentials/onprem.cred,dir_mode=0777,file_mode=0777,serverino,nosharesock,actimeo=30