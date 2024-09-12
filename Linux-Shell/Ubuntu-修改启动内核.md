- 检查已安装的内核

  ~~~sh
  dpkg --list | grep linux-image
  
  ii  linux-image-5.15.0-102-generic          5.15.0-102.112                          amd64        Signed kernel image generic
  ii  linux-image-5.15.0-78-generic           5.15.0-78.85                            amd64        Signed kernel image generic
  ii  linux-image-5.15.0-88-generic           5.15.0-88.98                            amd64        Signed kernel image generic
  ii  linux-image-generic                     5.15.0.102.99                           amd64        Generic Linux kernel image
  ~~~

- 检查内核启动顺序

  ~~~sh
  grep 'menuentry' /boot/grub/grub.cfg
  
  menuentry 'Ubuntu' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-simple-685552fd-4f93-41d4-9337-29b88e63493a' {
  submenu 'Advanced options for Ubuntu' $menuentry_id_option 'gnulinux-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-102-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-102-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-102-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-102-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-88-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-88-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-88-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-88-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-78-generic' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-78-generic-advanced-685552fd-4f93-41d4-9337-29b88e63493a' {
          menuentry 'Ubuntu, with Linux 5.15.0-78-generic (recovery mode)' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-5.15.0-78-generic-recovery-685552fd-4f93-41d4-9337-29b88e63493a' {
  ~~~

- 修改内核启动顺序，固定为5.15

  ~~~sh
  sudo vim /etc/default/grub
  
  GRUB_DEFAULT=0
  #修改为
  GRUB_DEFAULT="Advanced options for Ubuntu>Ubuntu, with Linux 5.15.0-88-generic"
  
  sudo update-grub
  ~~~

- 卸载旧版本内核

- mark hold一下现在的内核版本，保持住现在的内核版本不升级

  ~~~sh
  sudo apt-mark hold linux-headers-generic linux-image-generic linux-generic
  ~~~

  

