# SSO

- 登录原理
  - 登陆一个服务，输入用户名密码，服务端验证后建立session，然后把session id通过cookie发给客户端浏览器。下次浏览器访问的时候，cookie就会发过来，服务端就可以认出登录用户，实现免登陆。
  - SSO
    - 系统中由多个服务，在不同的服务器上，用户只要在某一个地方登录一个系统，另外的系统就能认出他来免登陆。
    - 共享cookie是不行的，因为cookie不能跨域，a.com的cookie，浏览器不能发送到b.com。session如果用redis来做成多系统共享的，也不行，因为不同系统架构不同，语言不通，难以共享。
    - SSO实现-JWT的基本原理，客户端登录一个系统，验证成功后，服务端返回的cookie中带着一个token；客户端下次访问别的系统，cookie中带着token，服务端就认出来了。这种方法可以对token进行加密，header+userID进行Hash和密钥加密生成一个签名；另一个系统如果收到了token，会再对header+userid进行Hash+密钥生成签名，二者签名一致，说明token有效。这种方法的问题是：userID在每个系统中都不一样，难以统一
  - SSO-统一认证中心 CAS
    - 建立一个统一认证中心sso.com
    - 客户端浏览器访问a.com，需要登录才能访问；系统A服务端将请求重定向到sso.com，sso让客户端去登陆，登陆成功后：
      - sso建立一个session，
      - sso创建一个ticket（可以认为是一个随机字符串）
      - ticket放到cookie中发送给客户端（客户端有了sso的cookie）
      - 重定向到系统A，URl中带着ticket（a.com?ticket=xxx）
      - A系统接收到a.com?ticket=xxx的请求，要再去sso认证中心，验证ticket，sso认证ticket有效
      - A系统就认为这个用户登录过了，A系统就返回给客户端浏览器相应的内容，发送cookie过去。（客户端有了A系统的cookie）
    - 此后，如果客户端再访问A系统中的别的资源，比如a.com/A1.html，那么因为客户端带着A系统的cookie，就不用再登录了。
    - 此后，如果客户端再去访问B系统（b.com）：
      - 由于A系统的cookie不能跨域来用；但是客户端有sso认证中心的cookie，B系统先重定向给sso认证中心。
      - sso识别了客户端的cookie，生成ticket，放到sso的cookie中返回给浏览器；并且再重定向回给B系统。
      - B系统接收到带着ticket的客户端请求（b.com?ticket=xxx），再向sso来验证一下，验证ticket通过。
      - B系统就开启session，发给客户端cookie，和想访问的页面。

# OAuth

- 三种认证方式
  - Resource Owner Password Credentials Grant：资源所有者密码凭据许可
  - Implicit Grant 隐式许可
  - Authorization Code Grant：授权码许可