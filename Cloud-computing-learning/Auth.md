# 认证基础

**Authentication - AuthN -** **认证**

- Authentication - AuthN - 认证：侧重于证明某实体（如用户或服务）确实是其所称的身份。

**Authorization - AuthZ -** **授权**

- Authorization - AuthZ - 授权：用于设置权限，这些权限用于评估对资源或功能的访问权限。

# SSO

- 登录原理
  - 用户登陆一个服务，输入用户名密码，服务端验证后建立session，然后把session id通过cookie发给客户端浏览器。下次浏览器访问的时候，cookie就会发过来，服务端就可以认出登录用户，实现免登陆。
  
  - SSO
    
    - 系统中有多个服务，在不同的服务器上，用户只要在某一个地方登录一个系统，另外的系统就能认出他来免登陆。
    - 共享cookie是不行的，因为cookie不能跨域，a.com的cookie，浏览器不能发送到b.com。
    - b系统内存中也没有a系统的session，即使cookie能共享，也识别不了。session如果用redis来做成多系统共享的，也不行，因为不同系统架构不同，语言不通，难以共享。
    - SSO实现：客户端登录一个系统，验证成功后，a服务端返回的cookie中带着一个token；客户端下次访问b系统，cookie中带着token，b服务端就认出来了，实现免登陆。
    - JWT的基本原理：token需要加密，可以用header+userID进行Hash和密钥加密生成一个签名；另一个系统如果收到了token，会再对header+userid进行Hash+密钥生成签名，二者签名一致，说明token有效。这种方法的问题是：userID在每个系统中都不一样，难以统一。
    
  - SSO-统一认证中心 CAS
    - 建立一个统一认证中心sso.com
    
    **首次登陆过程：**
    
    - 客户端浏览器访问a.com/pageA，这个页面需要登录才能访问；系统A服务端返回302，将请求重定向到sso.com（www.sso.com/login?redirect=www.a.com/pageA），sso让客户端去登陆，登陆成功后：
      - sso建立一个与浏览器的session
    
      - sso创建一个ticket（可以认为是一个随机字符串）
    
      - ticket放到cookie中发送给客户端（客户端有了sso.com的cookie）
    
        ![image-20230829214503882](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292145217.png)
    
      - 返回302重定向到系统A，URl中带着ticket（www.a.com/pageA?ticket=xxx）
    
      - A系统接收到www.a.com/pageA?ticket=xxx的请求，A系统要去sso认证中心，验证ticket，sso认证ticket有效
    
      - A系统就认为这个用户登录过了，A系统就返回给客户端浏览器相应的内容，发送cookie过去。（客户端有了A系统的cookie）
    
      - 此后，如果客户端再访问A系统中的别的资源，比如a.com/A1.html，那么因为客户端带着A系统的cookie，就不用再登录了。
    
        ![image-20230829214543999](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292145207.png)
      
      
      
    - 此后，如果客户端再去访问B系统（b.com）：
    
      - 由于A系统的cookie不能跨域来用；但是客户端有sso认证中心的cookie，B系统先返回302，浏览器重定向给sso认证中心(www.sso.com/login?redirect=www.b.com/pageB)。
    
      - sso识别了客户端的cookie，生成ticket，放到sso的cookie中返回给浏览器；并且再返回302，浏览器重定向回给B系统（www.b.com/pageB/Ticket=xxx）。
    
      - B系统接收到带着ticket的客户端请求（www.b.com/pageB?ticket=xxx），再向sso来验证一下，验证ticket通过。
    
      - B系统就开启session，发给客户端cookie，和想访问的页面。
    
        ![image-20230829214800669](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292148791.png)

# OAuth

## 简介

- 在RFC6749文档中提出来的，RFC中的OAuth的workflow如下：

![image-20230830134023843](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301340973.png)

- 以上流程主要是Authorization Grant需要具体确认。
- 对于应用端而言需要获取到的信息：
  - 应用名称、应用URL
  - 重定向URL或回调URL(redirect_url或callback_url)
  - client_id、client_secret

## 四种认证方式

- Resource Owner Password Credentials Grant：资源所有者密码凭据许可
- Implicit Grant：隐式许可
- Authorization Code Grant：授权码许可
- client credentials：客户端凭据

## 四种认证方式示例

（前三种来自《码农翻身》）

示例场景：开发了一个客户端app，需要读取用户网易邮箱中的邮件。

资源所有者：网易邮箱的用户。

资源服务器：网易邮箱的服务器。

授权服务器：网易邮箱认证中心。

客户端：就是开发的app。

### 资源所有者密码凭据许可

- 密码凭据许可：资源所有者（即网易邮箱的用户）直接将用户名+密码提供给client app，app去访问网易邮箱用。
- 缺点：用户通常不信任怕client app保存密码，不愿意直接提供密码给第三方app。

### 隐式许可

![image-20230829222758698](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292227860.png)

- app需要先在网易认证中心注册一下，网易颁发一个app_id和app_secret。
- app里面提供一个入口：使用网易账号登录。用户点了之后，返回302，重定向到网易的认证系统去登录（要带着app的id和secret，让网易知道是这个app在申请授权）。
- 网易的认证系统会要求用户输入用户名+密码，并且询问是否允许app访问网易邮箱。

- 允许之后，返回302重定向到app网址，同时url带了一个网易认证中心颁发的access token。
- app拿到这个access token，就可以通过API来访问网易邮箱了。

注：

- 这个return_uri就是app里面需要配置的redirect_uri，作用是告诉认证中心需要把token返回给什么url。
- 第6步，认证中心颁发token之后，以明文的形式返回给redirect_uri，www.a.com/callback#token=\<token\>，这叫做hash fragment，只停留在浏览器端，只有javascript能访问他，而且不会再次通过HTTP request发给别的服务器，提高了安全性。
- 用javascript来访问token，所有工作在浏览器前端完成，后端服务器就不需要参与了，**客户端app就不需要去找认证中心认证了。**

### 授权码许可

![image-20230829225127596](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292251745.png)

如果要将token隐藏，可以采用授权码许可的方式：

- 加一个授权码的中间层，当用户跳转到认证中心登录的时候，不直接颁发token，颁发一个授权码返回给redirect_URL。

- app端拿到授权码之后，去找认证中心兑换token（**这个过程需要客户端的后端服务器去找认证中心认证**），拿到token之后就可以用api访问服务了。

- 安全措施：

  - 授权码和app id和secret关联，确保是这个app在访问。

  - 可以让授权码有过期时间。
  - 可以让授权码只能兑换一次token。

### client_credentials

![image-20230830140740976](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301407032.png)

- grant_type=client_credentials
- 这种方式是客户端app拿着客户端自己的id和密钥去拿token，不涉及用户参与。
- 比较适合消费API的后端服务。并且也不支持refresh token。

## Token介绍

### Refresh Token

[理解OAuth 2.0——阮一峰_oauth2.0认证原理 阮一峰_Laputa_SKY的博客-CSDN博客](https://blog.csdn.net/Laputa_SKY/article/details/80428220)

- 在上述workflow中，认证服务器返回给客户端access token时，有时也会带一个refresh token：

  ![image-20230830135846613](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301358703.png)

- expires_in表示这个access token过久之后会过期

- 过期之后，客户端需要调用某个接口，将refresh token传过去，就能拿到新的access token。

- 如果不设置refresh_token，access token过期之后，就得让用户重新认证授权。