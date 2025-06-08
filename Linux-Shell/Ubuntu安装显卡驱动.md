1.先检查系统有没有安装好GPU驱动

```sh
nvidia-smi
```

如果报错就说明驱动未安装

2.安装驱动

系统根据GPU硬件型号推荐的GPU驱动

```sh
ubuntu-drivers devices
```

"recommended"标签表示该驱动程序被认为是最适合你的硬件设备的版本，但是并不意味着该驱动程序与你的系统完全匹配。这是因为驱动程序的版本需要与当前Ubuntu操作系统版本和其他组件（例如内核和Xorg）的版本匹配，以确保其能够正常工作。

3. 禁用nouveau

   ```sh
   sudo vim /etc/modprobe.d/blacklist.conf
   ```

   最后一行输入

   ```sh
   blacklist nouveauoptions nouveau modeset=0
   ```

   更新系统

   ```sh
   sudo update-initramfs -u
   ```

   重启

   ```sh
   sudo reboot
   ```

   以下命令验证是否禁用nouveau，若系统没有任何输出则禁用成功

   ```sh
   lsmod | grep nouveau
   ```

4. 配置环境变量

   ```sh
   sudo vim ~/.bashrc
   ```

   末尾加入：

   ```sh
   export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATHexport LD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
   ```

   保存更新：

   ```sh
   source ~/.bashrc
   ```

   2.4 安装相关依赖

   ```sh
   sudo apt-get install libprotobuf-dev libleveldb-dev libsnappy-dev libopencv-dev libhdf5-serial-dev protobuf-compiler
   sudo apt-get install --no-install-recommends libboost-all-dev
   sudo apt-get install libopenblas-dev liblapack-dev libatlas-base-dev
   sudo apt-get install libgflags-dev libgoogle-glog-dev liblmdb-dev
   ```

   2.5 安装驱动【不要用one和server的】

   ```sh
   sudo apt install nvidia-driver-535 -y
   ```

   2.6 安装完成测试

   ```sh
   nvidia-smi
   ```

   