# docker部署homebox

Homebox（家庭盒子）是专为居家用户打造的库存和组织系统！注重简洁和易用性，Homebox 是您家庭库存、组织和管理需求的完美解决方案。在开发该项目时，作者一直牢记以下原则：

- 简洁 – HomeBox 的设计简单易用。无需复杂的设置或配置。您可选择使用单个 Docker 容器，或通过编译适用于您所选择的平台的二进制文件自行部署。
- 极速 – HomeBox 采用 Go 语言编写，使其运行速度极快，并且所需的资源很少。通常，整个容器的空闲内存使用量不到 50MB。
- 便携 – HomeBox 设计为便携式并可在任何地方运行。我们使用 SQLite 和内置的 Web 界面，使部署、使用和备份变得简单。

- https://github.com/hay-kot/homebox
- https://hay-kot.github.io/homebox/

## 安装homebox

- 首先安装好docker和docker-compose

~~~sh
cd /home
mkdir homebox
cd homebox

#创建docker-compose文件
tee docker-compose.yaml <<'EOF'
version: "3.4"

services:
  homebox:
    image: ghcr.io/hay-kot/homebox:latest
    container_name: homebox
    restart: always
    environment:
    - HBOX_LOG_LEVEL=info
    - HBOX_LOG_FORMAT=text
    - HBOX_WEB_MAX_UPLOAD_SIZE=10
    volumes:
      - ./data:/data/
    ports:
      - 31521:7745 #自定义容器暴露的端口
EOF
#启动容器
docker-compose up -d

#注：如果更改了docker-compose.yml文件，需要docker-compose stop之后再重新docker-compose up -d启动容器
~~~

