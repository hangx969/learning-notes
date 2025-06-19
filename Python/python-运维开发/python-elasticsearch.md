# es介绍

Elasticsearch 是一个分布式搜索和存储引擎，专门用于处理海量数据的实时搜索、分析任务。它采用开源、RESTful 风格，以快速、高效著称，广泛应用于企业的日志分析、全文搜索和实时监控等场景。

简单来说，Elasticsearch 就像一个企业内部的互联网搜索引擎，帮助你从大量数据中迅速找到所需内容。它不仅能搜索，还能对存储的数据进行实时分析，适合处理复杂的查询需求和大规模数据分析。

**为什么选择 Elasticsearch？**

当你的数据量非常大（比如上亿条记录），你需要从中快速查找有用的信息，这时候传统数据库的查询可能会变得非常慢。而 Elasticsearch 就像一个强大的 "搜索超人"，它能够在海量数据中秒级返回结果，这是它最大的亮点。

**Elasticsearch 的核心概念**

1. 索引（Index）：
   - 索引类似于传统数据库中的表，是用来存储数据的地方。每个索引包含许多文档。
2. 文档（Document）：
   - 文档是 Elasticsearch 中存储数据的基本单位。每个文档以 JSON 格式存储，类似于数据库中的一行记录。例如，一条用户信息、产品信息或日志记录都可以作为一个文档存储在 Elasticsearch 中。
3. 字段（Field）：
   - 每个文档由多个字段组成，字段相当于数据库记录中的列。例如，一个用户文档可以有名字、年龄、地址等字段。
4. 倒排索引（Inverted Index）：
   - 这是 Elasticsearch 快速搜索的核心技术。它会对存储的数据进行索引，把每个字段中的关键词和文档关联起来，这样就能快速找到包含特定关键词的文档。
5. 分片（Shard）和副本（Replica）：
   - 为了处理海量数据，Elasticsearch 会把索引分成多个分片，每个分片可以存储在不同的服务器上。这种方式不仅提升了存储能力，也提高了查询速度。此外，每个分片还可以有一个或多个副本，保证数据安全，即使某个服务器宕机，数据也不会丢失。

## 安装

1. 确保你的 linux 系统已安装 Java。es 需要 Java 运行环境（JRE）才能正常工作。es 版本是 8.x，需要依赖的 jdk 版本是 11+。

~~~sh
sudo yum install java-11-openjdk-devel -y
~~~

2. 创建一个新的 repo 文件以添加 Elasticsearch 的官方存储库：

~~~sh
sudo tee /etc/yum.repos.d/elasticsearch.repo <<'EOF'
[elasticsearch-8.x]
name=Elasticsearch repository for 8.x packages
baseurl=https://artifacts.elastic.co/packages/8.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
EOF
~~~

3. 安装es

~~~sh
yum install elasticsearch -y
~~~

4. 修改es配置文件

~~~sh
sudo vim /etc/elasticsearch/elasticsearch.yml
network.host: 0.0.0.0
http.port: 9200
xpack.security.enabled: false
~~~

5. JVM 内存设置

~~~sh
# 确认 JVM 的内存设置是否正确，确保给 Elasticsearch 分配了足够的内存。可以在/etc/elasticsearch/jvm.options 文件中进行设置。例如：
sudo vim /etc/elasticsearch/jvm.options
-Xms2g
-Xmx2g
~~~

6. 启动es

~~~sh
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
~~~

7. 验证安装

~~~sh
curl -X GET "<VM IP>:9200/"
# 看到如下输出
{
"name": "your-node-name",
"cluster_name": "your-cluster-name",
"cluster_uuid": "xxxxxxxxxxxxxx",
"version": {
"number": "8.15.2",
...
},
"tagline": "You Know, for Search"
}
~~~

## 常用命令和API

1. 查看集群健康状态

  ```sh
  GET _cluster/health
  curl -X GET "172.16.8183.80:9200/_cluster/health"
  ```
2. 查看集群信息

  ```sh
  GET _cluster/state
  curl -X GET "172.16.8183.80:9200/_cluster/state"
  ```
3. 查看节点信息

  ```sh
  GET _cat/nodes?v
  curl -X GET "172.16.8183.80:9200/_cat/nodes?v"
  ```
4. 查看集群的插件

  ```sh
  GET _cat/plugins?v
  curl -X GET "172.16.8183.80:9200/_cat/plugins?v"
  ```
5. 查看集群的分片信息

  ```sh
  GET _cat/shards?v
  curl -X GET "172.16.8183.80:9200/_cat/shards?v"
  ```

6. 查看索引列表

  ```sh
  GET _cat/indices?v
  curl -X GET "172.16.8183.80:9200/_cat/indices?v"
  ```
7. 创建索引

  ```sh
  PUT /my_index
  curl -X PUT "172.16.8183.80:9200/my_index"
  ```
8. 删除索引

  ```sh
  DELETE /my_index
  curl -X DELETE "172.16.8183.80:9200/my_index"
  ```
9. 创建索引，在索引中插入文档

  ```sh
  # 1）. 创建索引 articles
  curl -X PUT http://172.16.8183.80:9200/articles
  # 2）. 插入文档到 articles 索引中。假设我们插入一篇文章，ID 为 1：
  curl -X POST "172.16.8183.80:9200/articles/_doc/1" -H "Content-Type: application/json" -d '{"title": "这是我的第一篇文档","content":"这是第一篇文档的内容"}'
  # 现在我们把文档插入到了 articles 索引中，ID 为 1。
  # 3）. 查询插入的文档。如果你想查询 articles 索引中 ID 为 1 的文档，可以使用：
  curl -X GET http://172.16.8183.80:9200/articles/_doc/1
  ```

# 案例：检测es是否运行并根据情况重启服务

检测 Elasticsearch 是否在运行，每分钟检测一次，并根据情况重启 Elasticsearch，可以通过 requests 模块
与 subprocess 模块相结合来实现：

1. 检测 Elasticsearch 是否运行：可以通过请求 Elasticsearch 的 HTTP 接口，例如
   http://localhost:9200/，来检查是否有响应。如果没有响应，则认为 Elasticsearch 没有运行。
2. 重启 Elasticsearch：可以通过 subprocess 模块调用系统命令来重启 Elasticsearch 服务。

~~~python
import subprocess, time, requests

def check_es() -> bool:
    try:
        response = requests.get('http://172.16.183.101:9200/_cluster/health')
        if response.status_code == 200:
            print("ES is running.")
            return True
        else:
            return False
    except requests.exceptions.RequestException: # 这里会包括ConnectionError、Timeout、InvalidURL、SSLError等
        print("ES is not running.")
        return False

def restart_es():
    try:
        print("Restarting ES.")
        result = subprocess.run(["systemctl", "restart","elasticsearch"], check=True, capture_output=True, text=True)
        print("ES restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart es: {e}.")

if __name__ == '__main__':
    while True:
        if not check_es():
            restart_es()
        else:
            print("ES is running, do nothing.")
        time.sleep(60)
~~~

