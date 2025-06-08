# 介绍

基于Go语言驱动、Vue.js构建前端的全栈项目，带可视化界面的cronjob调度系统

- 官网：https://github.com/flohoss/gocron

# 部署

- 先创建配置文件

~~~yaml
mkdir ./gocron-config/
tee ./gocron-config/config.yml <<'EOF'
defaults:
  # every job will be appended to this cron and the jobs will run sequentially
  cron: '0 3 * * *' # Runs daily at 3:00 AM
  # global envs to use in all jobs
  envs:
    - key: RESTIC_PASSWORD_FILE
      value: '/secrets/.resticpwd'
    - key: BASE_REPOSITORY
      value: 'rclone:pcloud:Server/Backups'
    - key: APPDATA_PATH
      value: '/mnt/user/appdata'

jobs:
  - name: Notify at 2AM
    cron: '0 2 * * *' # Runs daily at 2:00 AM
    commands:
      - command: apprise "mailto://you@example.com" -t "Daily Notification" -b "This is your 2AM notification from GoCron."
  - name: Example
    cron: '0 5 * * 0' # Runs daily at 5:00 AM
    commands:
      - command: ls -la
      - command: sleep 1
      - command: echo "Done!"
      - command: sleep 1
  - name: Test
    envs:
      - key: BACKUP_PATH
        value: '/app/config/test'
    commands:
      - command: mkdir -p ${BACKUP_PATH}
      - command: rm -rf ${BACKUP_PATH}/*
      - command: echo 'Hello World' > ${BACKUP_PATH}/backup.md
      - command: stat ${BACKUP_PATH}/backup.md
      - command: cd ${BACKUP_PATH} && find . -maxdepth 1 -name backup.md -mmin -1 | grep -q . && echo 'FILE RECENTLY GENERATED'
  - name: Set envs
    envs:
      - key: BACKUP_PATH
        value: '/app/config/test'
      - key: RESTIC_REPOSITORY
        value: '$BASE_REPOSITORY/Backups'
    commands:
      - command: echo $RESTIC_PASSWORD_FILE
      - command: echo $RESTIC_REPOSITORY   
EOF
~~~

- docker部署

~~~sh
docker run -it --rm \
  --name gocron \
  --hostname gocron \
  -p 8156:8156 \
  -e DELETE_RUNS_AFTER_DAYS=7 \
  -e LOG_LEVEL=info \
  -e PORT=8156 \
  -v ./gocron-config/:/app/config/ \
  ghcr.io/flohoss/gocron:latest
~~~

