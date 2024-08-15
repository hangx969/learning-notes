# 认证基础

### **Authentication - AuthN -** **认证**

- Authentication - AuthN - 认证：侧重于证明某实体（如用户或服务）确实是其所称的身份。

### **Authorization - AuthZ -** **授权**

- Authorization - AuthZ - 授权：用于设置权限，这些权限用于评估对资源或功能的访问权限。

### Permission vs previlege vs scopes

- permission: 是对resource而言的，代表这个resource能被执行什么操作。
- previlege：是给某个user授予某资源的permission，这个user就有了previlege
- scopes: define what an app can do on behalf of the user. (OAuth2里面用的)



# 基于CAS的SSO

## CAS

- central authentication server，是一种仅用于authentication的协议，与OAuth、OIDC不同，不能作为authorization的协议。
- CAS的参与者包含三部分：
  - client：通常是使用浏览器的用户
  - CAS client：实现CAS协议的web应用
  - CAS server：作为统一认证的CAS服务器
- CAS是一个比较简陋的SSO协议，能够解决的场景比较单一，目前基本不用了。

## SSO

- 系统中有多个服务，在不同的服务器上，用户只要在某一个地方登录一个系统，另外的系统就能认出他来免登陆。
- 共享cookie是不行的，因为cookie不能跨域，a.com的cookie，浏览器不能发送到b.com。
- b系统内存中也没有a系统的session，即使cookie能共享，也识别不了。session如果用redis来做成多系统共享的，也不行，因为不同系统架构不同，语言不通，难以共享。
- SSO实现：客户端登录一个系统，验证成功后，a服务端返回的cookie中带着一个token；客户端下次访问b系统，cookie中带着token，b服务端就认出来了，实现免登陆。
- JWT的基本原理：token需要加密，可以用header+userID进行Hash和密钥加密生成一个签名；另一个系统如果收到了token，会再对header+userid进行Hash+密钥生成签名，二者签名一致，说明token有效。这种方法的问题是：userID在每个系统中都不一样，难以统一。

- 登录原理
  - 用户登陆一个服务，输入用户名密码，服务端验证后建立session，然后把session id通过cookie发给客户端浏览器。下次浏览器访问的时候，cookie就会发过来，服务端就可以认出登录用户，实现免登陆。
  
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

- 是一种授权协议，主要解决：第三方应用如何被授权访问资源服务器。（delegated authorization）

- 认证部分在Oauth中没怎么涉及，基本是由厂商自己解决。目前比较流行的认证的协议是用的OIDC。

  > OIDC是基于OAuth2.0扩展出来的协议，除了能够实现OAuth2.0的的Authorization场景，也额外定义了Authentication的场景。

- OAuth在RFC6749文档中提出来的（[RFC 6749: The OAuth 2.0 Authorization Framework (rfc-editor.org)](https://www.rfc-editor.org/rfc/rfc6749.html)），RFC中的OAuth的workflow如下：

![image-20230830134023843](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301340973.png)

- 以上流程主要是Authorization Grant需要具体确认。
- 对于应用端而言需要获取到的信息：
  - 应用名称、应用URL
  - 重定向URL或回调URL(redirect_url或callback_url)
  - client_id、client_secret

## 术语

- Resource owner：某个用户，其拥有用户信息、可以执行一些Action等。
- client：需要被授权来代表用户获取数据、执行操作的客户端app。
- resource server：是client需要去代表用户拿信息而调用的API/service。
- authorization server：保存了用户账户信息的认证服务器。
- Redirect URL/Callback URL：认证服务器grant permission之后，重定向到的URL。
- Response type：client期望收到的类型。
- Scope：定义了client拥有的permission，比如Read、Write、Delete等
- Consent：认证Server弹出Promt，询问resource owner是否愿意给client相应的scope权限。

## 四种认证方式

- Resource Owner Password Credentials Grant：资源所有者密码凭据许可
- Implicit Grant：隐式许可
- Authorization Code Grant：授权码许可
- client credentials：客户端凭据

## 四种认证方式示例

（前三种来自《码农翻身》）

示例场景：开发了一个客户端app，需要读取用户网易邮箱中的邮件。

资源所有者：网易邮箱的用户。(拥有account data、actions)

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

- 允许之后，返回302重定向到app的redirect url，同时url带了一个网易认证中心颁发的access token。
- app拿到这个access token，就可以通过API来访问网易邮箱了。

注：

- 这个return_uri就是app里面需要配置的redirect_uri，作用是告诉认证中心需要把token返回给什么url。
- 第6步，认证中心颁发token之后，以明文的形式返回给redirect_uri，www.a.com/callback#token=\<token\>，这叫做hash fragment，只停留在浏览器端，只有javascript能访问他，而且不会再次通过HTTP request发给别的服务器，提高了安全性。
- 用javascript来访问token，所有工作在浏览器前端完成，后端服务器就不需要参与了（或者有些时候你的app根本没有后端服务器，只有前端的web page），**客户端app就不需要去找认证中心认证了。**

### 授权码许可

![image-20230829225127596](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308292251745.png)

如果要将token隐藏，可以采用授权码许可的方式：

- 加一个授权码的中间层，当用户跳转到认证中心登录的时候，不直接颁发token，颁发一个授权码返回给redirect_URL。
- app端拿到授权码之后，去找认证中心兑换token（**这个过程需要客户端的后端服务器去找认证中心认证**），拿到token之后就可以用api访问服务了。

> 关于为何要用authorization code，这涉及到安全原因：
>
> 1. front-end channel - 浏览器前端 - less secure
> 2. backend channel - 后端服务器 - more secure
>
> 授权码是通过浏览器，也就是frontend传回来的，随后client app的backend server去找IdP拿token，这个过程是安全的，有HTTPS加密保障，access token不会泄露。
>
> 如果授权码被窃取，窃取者也无法去找IdP兑换token，因为窃取者没有app_id\app_secret的信息，这些信息只保存在后端server上。

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

### Access Token

- 包含了client app的scopes（权限）

### Refresh Token

[理解OAuth 2.0——阮一峰_oauth2.0认证原理 阮一峰_Laputa_SKY的博客-CSDN博客](https://blog.csdn.net/Laputa_SKY/article/details/80428220)

- 在上述workflow中，认证服务器返回给客户端access token时，有时也会带一个refresh token：

  ![image-20230830135846613](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301358703.png)

- expires_in表示这个access token过久之后会过期

- 过期之后，客户端需要调用某个接口，将refresh token传过去，就能拿到新的access token。

- 如果不设置refresh_token，access token过期之后，就得让用户重新认证授权。

### ID token

- JWT格式的token，有一段signature部分，确保header部分的user info信息未被篡改。

## CLient种类

- Confidential的client
  - 例如web-based server，可以安全的存储secert。
  - 这种情况，在back channel去找IdP用auth code兑换access token，是安全的。
- public的client
  - 比如single page app、native app等，无法机密存储secret。可以抓traffic随便看到。
  - 这种情况，没有back channel，怎么安全兑换token？==》PKCE（proof key for code exchange）
    - PKCE是一种cipher，由client生成，在一开始的AuthN request通过Https发送给了IdP，后续兑换token的时候也带着，证明app的身份。

# OIDC

> 参考视频：
>
> - https://www.youtube.com/watch?v=t18YB3xDfXI，https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc
> - https://www.youtube.com/watch?v=996OiexHze0&t=7s, https://speakerdeck.com/nbarbettini/oauth-and-openid-connect-in-plain-english?slide=33

## 简介

- OAuth只负责完成了授权部分，返回给client的access token，client不懂，也不知道这个token包含的是哪个用户，只是发给resource server来获取信息。

- Oauth2.0授权服务器能够对用户进行身份验证，但该框架也没有提供一种标准的方法来将经过身份验证的用户的身份安全地传递给应用程序。OIDC为这一需求提供了解决方案。OIDC被设计为OAuth2.0协议之上的一个层，以标准格式向应用程序提供有关经过身份验证的用户的身份的信息。这为用户身份验证和API授权的应用程序提供了一个解决方案。

- OIDC在OAuth基础上增加了login和profile的功能，可以让client建立一个login session来认证。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308301838405.png" alt="image-20230830183814266"  />

![image-20230830220204277](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308302202387.png)

- 如果一个authentication server支持OIDC，那么会被称为IdP，因为会对client提供resource provider的信息。

- What OIDC adds:

  - ID token
  - User Info endpoint - 获取更多的user info
  - Standard set of scopes
  - Standard implemention

- 作用对比

  ![image-20230830222037577](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308302220722.png)

## 认证流程

![image-20230830204631831](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308302046964.png)

![image-20230830204655256](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308302046342.png)

- 基本流程与OAuth2的授权码流程类似，除了：

  - 在第2步重定向到IdP的时候，会带一个scope=openid，让IdP知道这是一个OIDC的exchange。

  - 在第7步client找IdP兑换token的时候。IdP会返回access token + ID token。

    - ID token是JWT格式的token，包含用户信息，client可以decode出用户信息

      <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308302053765.png" alt="image-20230830205345680" style="zoom:67%;" />

    - JWT里面的data被称为**claim**
    - client可以拿着access token再去IdP拿一些其他用户信息

# SAML

## 简介

- Security Assertion Markup Language，是基于XML的标准协议。定义了身份提供者IDP和服务提供者Service Provider之间，如何通过SAML规范，采用加密和签名的方式建立互信，从而交换用户身份信息。是一个非常古老的Authentication协议，在早期B/S架构中比较流行。
- 当用户登录到启用SAML的应用程序时，服务提供商会从相应的身份提供商请求授权。 身份提供商验证用户的凭据，然后将用户的授权返回给服务提供商，用户现在可以使用该应用程序。

### 涉及到的三方

- 用户、IdP、SP
- SP需要IdP的身份验证服务才能授予用户授权。
- IdP执行用户的身份验证，并将数据和用户对服务的访问权限一起发送到SP。

### 名词解释

- Federation
  - Access to protected resrouces can be gratned to security principals existing in different realms <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309031008389.png" alt="image-20230903100810194" style="zoom: 33%;" />
- WS-FED \ SAMl - signin protocols
  - Protocol used by application and identity provider to communicate with each other.
    - 用户通过某些user agent来访问application保护的资源（DB、Api等），application需要向IdP发送request，来询问这个用户是否登陆了。application向IdP以什么格式发送信息？这种约定就是sign-in protocols，约定了SP和IdP如何交流。

- SAML assertion

  - 是IdP发送给SP的XML文档，包含用户授权协议。（wsfed和saml都是通过https发送xml格式的request）

  - 有三种类型：身份验证、属性、授权决策
    - 身份验证断言：证明了用户的身份，并提供了用户登录的时间以及他们使用的身份验证方法（即，Kerberos，双因素等）

    - 归属断言：将SAML属性传递给服务提供商 - SAML属性是提供有关用户信息的特定数据片段。

    - 授权决策断言：表示如果用户被授权使用该服务，或者由于密码失败或缺乏对服务的权限，身份提供商拒绝了他们的请求。


## 如何工作

### workflow

- SAML通过在身份提供商和服务提供商之间传递有关用户，登录和属性的信息来工作。

- 每个用户使用标识提供程序登录一次到Single Sign On，然后标识提供程序可以在用户尝试访问这些服务时将SAML属性传递给服务提供商。 服务提供商从身份提供商请求授权和身份验证。 由于这两个系统都使用相同的语言 - SAML - 用户只需登录一次。

- 每个身份提供商和服务提供商需要就SAML的配置达成一致。 两端都需要具有SAML身份验证的确切配置才能工作。

  ![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202308312311143.webp)

### request header

![image-20230903134500266](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309031345394.png)

### Request Secutiry Token Response

- WS-Fed - SAML 1.0
- SAML - SAML 2.0

# WS-FED

## 简介

- 2002年4月11日，微软、IBM和VeriSign三公司联合发表了Web服务的新安全规格“WS-Security”和Web安全蓝图“Security in a Web Services World”。在当时的安全蓝图说明中就包括了WS-Federation规范的基本轮廓。并于2003年7月9日发布规范的说明草案。
- 2009年，WS-Fed1.2规范正式作为OASIS的标准发布。该版本提供了“可以向在其他领域管理其身份的安全主体提供对在一个领域中管理的资源的授权访问”的机制，该标准得到了微软ADFS服务器以及许多其他商业SSO产品和服务的支持。
- WS-Federation（简称: WS-Fed )联合框架属于Web Services Security(简称: WS-Security、WSS: 针对web-service安全性方面扩展的协议标准集合) 的一部分。WS-Federation规范采用了XML以及其他Web服务标准，从而可以使开发者能够实现在不同环境下的网络安全管理及建立相互协调信赖关系的目的。
- 不用看协议的具体内容，光看到协议的框架，就可以感知到整个协议的功能之强大，细节之周全。然而，这也意味着实现起来会比较重，因此，除非为了能和微软的服务整合，才会优先考虑该协议。所以，该协议主要用于微软自己的生态。

  ![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202309031449985.webp)