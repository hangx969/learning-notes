# VMWare虚拟机挂载共享目录

- 新建了一台Ubuntu虚拟机，在虚拟机安装了VMWare Tools，设置中开启了宿主机的共享目录，但是在客户机中没看到共享目录

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402211553583.png" alt="image-20240221152955193" style="zoom: 50%;" />

- 根据这篇KB：https://zhuanlan.zhihu.com/p/650638983，在客户机运行以下命令：

  ~~~sh
  sudo mount -t fuse.vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
  #/mnt/hgfs/ 是挂载点，我们也可以修改为其它挂载点
  #-o allow_other 表示普通用户也能访问共享目录。
  cd /mnt/hgfs
  #注意：如果虚拟机重启，需要再次挂载共享文件夹。
  ~~~

  