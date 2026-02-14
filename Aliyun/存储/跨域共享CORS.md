### 1. 一句话总结

CORS 是一种基于 **HTTP 头部** 的机制，它允许**浏览器**打破“同源策略”的限制，去访问不同域名下的资源。

**对于运维来说，CORS 就是：**

> 只要是跨域请求，你的后端服务（或网关、CDN、存储桶）必须在响应头里带上特定的 `Access-Control-Allow-*` 字段，否则浏览器会拦截响应数据并报错。

---

### 2. 为什么会有这个问题？（背景）

互联网有一个核心安全规则叫 **同源策略 (Same-Origin Policy)**。

- **规定**：浏览器出于安全考虑，默认禁止 `a.com` 的网页通过 JS 代码去读取 `b.com` 的数据。
- **什么是“同源”**：协议（http/https）、域名（example.com）、端口（80/443）必须完全一致。

**运维场景：**  
现在的架构大多是前后端分离：

- **前端静态资源** 部署在 S3/CDN 上，域名是 `www.example.com`。
- **后端 API** 部署在 K8s/EC2 上，域名是 `api.example.com`。

当用户访问 `www` 时，前端 JS 试图请求 `api` 的数据。域名不同，这就是**跨域**。如果没有 CORS 配置，浏览器直接拦截，前端对此无能为力，只能找运维报修。

---

### 3. CORS 的工作原理（运维视角）

CORS 其实是浏览器和服务器之间的一次“握手”协商。

#### 场景 A：简单请求 (Simple Request)

如果是简单的 GET/POST 请求（且没有自定义 Header），流程如下：

1. **浏览器**：发出请求，Header 里带上 `Origin: https://www.example.com`。
2. **服务器/网关**：收到请求，检查 Origin。
    - 如果允许，响应 Header 加上 `Access-Control-Allow-Origin: https://www.example.com`。
3. **浏览器**：收到响应，检查 Header。如果有这个允许字段，JS 就能拿到数据；否则报错。

#### 场景 B：预检请求 (Preflight Request) —— _运维重点关注_

如果请求比较复杂（比如用了 `PUT`/`DELETE` 方法，或者带了 `Authorization`、`Content-Type: application/json` 等自定义头），浏览器会**先发一个 `OPTIONS` 请求**进行探路。

1. **浏览器**：先发一个 `OPTIONS` 请求给服务器。
    - `Origin: https://www.example.com`
    - `Access-Control-Request-Method: POST`
2. **服务器/网关**：必须正确响应这个 `OPTIONS` 请求（状态码 200/204），并返回允许的规则：
    - `Access-Control-Allow-Origin: https://www.example.com`
    - `Access-Control-Allow-Methods: GET, POST, OPTIONS`
    - `Access-Control-Allow-Headers: Authorization, Content-Type`
3. **浏览器**：收到通过的“通行证”后，才会发出真正的 POST 请求。

**运维痛点**：如果你发现日志里有很多 `OPTIONS` 请求，或者 API 延迟变高（多了一次 RTT），就是这个机制在起作用。

---

### 4. 运维主要在哪里配置 CORS？

作为运维，你通常需要在流量入口或资源托管处配置这些 Header。

#### A. 对象存储 (S3, OSS, COS)

前端静态资源或图片跨域时：

- **位置**：存储桶 (Bucket) 的属性页面 -> "跨域设置" (CORS)。
- **配置**：上传一段 XML 或 JSON，允许特定的 Origin 和 Method。

#### B. CDN (CloudFront, Cloudflare, 阿里云 CDN)

这是最容易坑的地方：

1. **响应头处理**：CDN 可能会把源站返回的 CORS 头给缓存了，或者过滤掉了。
2. **Vary 头**：你需要配置 CDN 转发 `Origin` 请求头回源站，并且配置缓存策略基于 `Origin` 头进行区分（`Vary: Origin`）。否则，A 域名的用户可能会缓存了 B 域名允许的 Header，导致 B 域名用户访问报错。

#### C. API 网关 / Nginx / Ingress

这是后端接口跨域的主战场。

**Nginx 配置示例：**

```nginx
server {
    location /api/ {
        # 允许所有域名（生产环境建议指定具体域名）
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        
        # 处理 OPTIONS 预检请求，直接返回 204，不转发给后端代码
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        proxy_pass http://backend_upstream;
    }
}
```

---

### 5. 运维常见故障与排查 (Troubleshooting)

当前端喊“CORS 报错了”，你该怎么办？不要只听前端截图，用命令行工具验证。

**工具：`curl`**

**1. 模拟请求：**  
使用 `-H` 伪造 Origin 头部，看服务器回不回 `Access-Control-Allow-Origin`。

```bash
curl -I -X POST \
  -H "Origin: https://www.example.com" \
  https://api.example.com/v1/data
```

**2. 常见错误及原因：**

- **错误：`No 'Access-Control-Allow-Origin' header is present`**
    
    - **原因**：Nginx/网关没配置，或者后端代码没处理。
- **错误：`The 'Access-Control-Allow-Origin' header contains multiple values`**
    
    - **原因**：**重复配置**。比如 Nginx 加了一次，后端代码（如 SpringBoot/Node.js）又加了一次。浏览器看到两个头就会报错。**解决办法：只在一个层级配置（建议在网关层统一处理）。**
- **错误：`Method not supported`**
    
    - **原因**：Nginx 拦截了 `OPTIONS` 请求并返回了 403/404，或者 `Access-Control-Allow-Methods` 里没包含当前用的方法。
- **CDN 缓存坑**
    
    - 如果你更新了 CORS 配置但没生效，记得刷新 CDN 缓存。

### 总结

CORS 本质上是**浏览器**用来防范恶意网站窃取数据的盾牌，但它需要**服务端（运维侧）**发放“通行证”（Header）。你的任务就是确保你的基础设施（Nginx/CDN/S3）在收到合法的跨域请求时，能正确返回这些 Header。