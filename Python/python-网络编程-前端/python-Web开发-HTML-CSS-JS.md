# 前端开发VsCode插件

前端开发需要用到的vscode插件：

1. HTML Boilerplate
2. HTML CSS Support
3. HTML Format
4. HTML to CSS autocompletion
5. HTML Play
6. CLASS autocompletion to HTML
7. CSS Snippets
8. JavaScript Snippets
9. Open in Browser

# 网站开发三剑客

## HTML

HTML发展历史：HTML在上个世纪90年代由欧洲核子研究中心的物理学家蒂姆·伯纳斯-李（Tim Berners-Lee）发明。它的最大特点就是支持超链接，点击链接就可以跳转到其他网页，从而构成了整个互联网。1999年，HTML4发布，2014年HTML5发布，这也是当前使用的版本。

HTML全称：HTML是超文本标记语言（Hypertext Markup Language）。它是一种用于创建网页结构和内容的标记语言。HTML使用一系列的标签（tag）来描述网页上的各种元素，如文本、图像、链接等，并通过这些标签来定义网页的结构和布局。浏览器访问网站，其实就是从服务器下载 HTML 代码，然后渲染出网页。

## CSS

CSS，即层叠样式表（Cascading Style Sheets），是用于描述网页样式和布局的样式语言。它为网页提供了丰富的样式控制功能，包括字体、颜色、边框、背景、布局等。

## JS

定义网页与用户的互动行为。比如表单验证、按钮点击、弹出框等。

HTML 语言是网页开发的基础，CSS 和 JavaScript 都是基于 HTML 才能生效，即使没有这两者，HTML 本身也能使用，可以完成基本的内容展示。

# HTML基础语法

HTML标签是用于定义网页结构和内容的元素，它们以尖括号`< >`包围，通常成对出现，包括开始标签和结束标签。开始标签和结束标签之间是标签的内容，也可以包含其他嵌套的标签。

## 文本处理标签

| 标签名称            | 对应的功能   | 备注                                                         |
| ------------------- | ------------ | ------------------------------------------------------------ |
| \<h1> \</h1>        | 标题         | h1字号最大，h6字号最小                                       |
| \<p> \</p>          | 段落         |                                                              |
| \<i> \</i>          | 斜体         |                                                              |
| \<b> \</b>          | 加粗文本     |                                                              |
| \<br/>              | 换行         |                                                              |
| \<del> \</del>      | 删除线       |                                                              |
| \<strong>\</strong> | 强调加粗文本 | 在视觉上，`<b>` 和 `<strong>` 可能会产生相同的效果；但是在语义上，`<strong>` 更加强调文本的重要性，所以在编写 HTML 时，应根据文本的语义来选择合适的标签。适用于开发者自己标注。 |
| \<sub> \</sub>      | 下标文本     |                                                              |
| \<sup> \</sup>      | 上标文本     |                                                              |

示例：

~~~html
<!DOCTYPE html>
<!-- !DOCTYPE html用来声明是HTML文档 -->
<!-- <html>: 定义根元素 -->
<html>
    <!-- <body>: 定义主体 -->
    <body>
    <!-- <h1> - </h1>: 定义标题的，h1字号最大，h6字号最小 -->
    <h1>这是一级标题</h1>
    <h2>这是二级标题</h2>
    <h3>这是三级标题</h3>
    <!-- <p>: 定义段落的，表示一段文本的内容 -->
    <p>这是定义段落的</p>
    <!-- <strong>: 强调加粗文本 -->
    <p><strong>这段内容很重要，需要用Strong标签强调加粗文本</strong></p>
    <!-- <b>: 加粗文本 -->
    <p><b>这段内容很重要，需要用b标签加粗文档</b></p>
    <!-- <i>: 斜体 -->
    <p><i>这段内容是斜体字</i></p>
    <p>Gitee.com（码云） 是 OSCHINA.NET 推出的代码托管平台，<br/>
        支持 Git 和 SVN，提供免费的私有仓库托管。
        目前已有超过 1200万的开发者选择 Gitee
    </p>
    <p>x<sub>2+y<sup>6</p>
    </body>
</html>
~~~

## 超链接标签

### 外部链接

HTML外部链接指的是在一个网页上创建指向另一个网页或网络资源的链接。这些链接将用户从当前网页导航到其他网站或网络资源，跳转到其他域名下的页面或文件。

外部链接通常用来引导用户访问其他网站的相关内容，或者提供额外的资源，比如参考资料、下载文件等。它们可以帮助扩展网站的功能，提供更丰富的信息和体验。

| 标签名称        | 对应的功能                 |
| --------------- | -------------------------- |
| href            | 指定要跳转到哪个链接       |
| target="_blank" | 访问链接时打开一个新的标签 |

~~~html
<!DOCTYPE html>
<!-- <html>: 定义根元素 -->
<html>
    <!-- <body>: 定义主体 -->
    <body>
    <!-- <a href></a>：外部链接，不额外打开新的标签页 -->
    <a href="https://edu.51cto.com/">欢迎来到51CTO课程网站</a>
    <!-- <a href target="_blank"></a>：: 外部链接，额外打开新的标签页，
        target="_blank"表示打开新的标签访问链接地址 -->
    <br/><a href="https://gitee.com/" target="_blank">
        欢迎来到gitee</a>
    </body>
</html>
~~~

### 图片+邮件+手机号链接

| 标签名称                          | 对应的功能                 |
| --------------------------------- | -------------------------- |
| href                              | 指定要跳转到哪个链接       |
| target="_blank"                   | 访问链接时打开一个新的标签 |
| alt="wechat"                      | 图片加载失败时显示的内容   |
| border="0"                        | 不设置边框                 |
| width="400" height="150"          | 图片的像素                 |
| src="wechat.png"                  | 图片所在位置               |
| href="mailto:someone@example.com" | 链接到发邮件               |
| href="tel:+8615011572657"         | 链接到打电话               |

~~~html
<!DOCTYPE html>
<!--<html>: 定义根元素-->
<html>
    <!--<body>: 定义主体-->
    <body>
    <!--<a href></a>：外部链接，不额外打开新的标签页-->
    <a href="https://edu.51cto.com">欢迎来到51CTO课程网站</a>
    <!--<a href target="_blank"></a>：: 外部链接，额外打开新的标签页，
        target="_blank"表示打开新的标签访问链接地址-->
    <br/><a href="https://gitee.com" target="_blank">
        欢迎来到gitee</a>
    <!--<a href></a>：使用图片作为链接：点击图片跳转到链接，border="0" 属性设置图像没有边框，
        alt="wechat"定义图片加载失败时提示信息-->
    <br/><a href="https://baike.baidu.com/item/%E9%9F%A9%E5%85%88%E8%B6%85/63838699">
            <img border="0" src="wechat.png" alt="wechat" width="400" height="150">
    </a>
    <br/><a href="https://edu.51cto.com/">
        <img border="0" src="领奖.png" alt="图片加载失败" width="500" height="300">
    </a>
    <!--<a href></a>：链接到电子邮件-->
    <p><a href="mailto:someone@example.com" target="_blank">发送邮件</a></p>
    <!--<a href></a>：链接到电话号码-->
    <p><a href="tel:+8615000000000">15011572657</a></p>
    </body>
</html>
~~~

### 内部标签

HTML内部链接用于在同一个网页内部进行导航，通常是将用户从一个部分导航到另一个部分。这可以通过在`href`属性中指定锚点的名称来实现。锚点就是在页面中某个位置的标记点，可以通过给特定元素添加`id`属性来创建锚点。

| 标签名称           | 对应的功能                                                   |
| ------------------ | ------------------------------------------------------------ |
| id="section1"      | 创建锚点                                                     |
| a href="#section1" | 链接的`href`属性指向了这些锚点的名称，比如`<a href="#section1">`。当用户点击链接时，浏览器会自动滚动到相应的位置。 |

~~~html
<!DOCTYPE html>
<html>
<body>
    <h1><a href="#section1">简介</a></h1>
    <h2><a href="#section2">任职</a></2>
    <h3><a href="#section3">经历</a></h3>

    <h1 id="section1">简介</h1>
    
    <p>xxxxxx
        <br/>云计算架构师
    </p>

    <h1 id="section2">任职</h1>
    <p>xxxxx
        <br/>云计算架构师
    </p>
    
    <h1 id="section3">经历</h1>
    <p>2xxxxxx
        <br/>云计算架构师
    </p>
    
</body>
</html>
~~~

## 列表标签

| 标签名称               | 对应的功能                                                   | 备注                                                         |
| ---------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| \<ul>                  | Unordered List：用于创建无序列表，列表项不按顺序排列，通常使用圆点、方块或其他自定义符号作为项目标记。 |                                                              |
| \<ol>                  | Ordered List：用于创建有序列表，列表项按照指定的顺序进行排列，通常使用数字、字母或其他自定义标记作为项目编号。 | type属性（仅适用于\<ol>）：定义有序列表的项目编号类型 <br />start 属性（仅适用于  \<ol>）：定义有序列表的起始编号值  **type="1"**：数字编号（默认值）<br />**type="A"**：大写字母编号<br />**type="a"**：小写字母编号<br />**type="I"**：大写罗马数字编号<br />**type="i"**：小写罗马数字编号<br /> |
| \<li>                  | List Item: 用于定义列表中的每个项目                          | value属性（仅适用于\<li>：定义有序列表中某个项目的编号值。   |
| \<dl>                  | Description List：定义描述列表，用于显示名词和对应的描述     | ` `                                                          |
| \<dt>                  | 用于定义术语（名词）                                         | ` `                                                          |
| \<dd>                  | 标签用于定义术语的描述                                       | ` `                                                          |
| \<select> 和 \<option> | 下拉列表和选项                                               | 下面是一些常用的 \<select>和\<option>元素的参数和属性：<br />1.\<select>元素的属性:<br />name：指定\<select> 元素的名称，用于表单提交时识别该元素的值<br />multiple：定义是否允许多选。如果设置为 multiple，则用户可以通过按住 Ctrl（在 Windows 或 Linux 操作系统上）或 Command（在 macOS 上）键来选择多个选项。<br />size：定义下拉列表框中可见的行数。对于单选列表，此属性通常不需要，但对于多选列表，可以用它来设置可见行数。<br />2.\<option> 元素的属性:<br />value：指定选项的值。这是提交表单时发送给服务器的值。   selected：定义该选项是否默认选中。可以在需要默认选中的选项上添加这个属性。<br />disabled：定义该选项是否被禁用。禁用的选项不能被选择，并且在下拉列表中会显示为灰色。 |

~~~html
<!DOCTYPE html>
<!--<html>: 定义根元素-->
<html>
    <!--<body>: 定义主体-->
    <body>
        <ul>
            <li>苹果</li>
            <li>香蕉</li>
            <li>橙子</li>
        </ul>
        <ol>
            <li>学习HTML</li>
            <li>学习CSS</li>
            <li>学习JavaScript</li>
        </ol>
        <!--type 属性（仅适用于 <ol>）：定义有序列表的项目编号类型。-->
        <ol type="A">
            <li>项目一</li>
            <li>项目二</li>
            <li>项目三</li>
        </ol>
        <!--start 属性（仅适用于 <ol>）：定义有序列表的起始编号值-->
        <ol start="6">
            <li>项目五</li>
            <li>项目六</li>
            <li>项目七</li>
        </ol>
        <!--value 属性（仅适用于 <li>）：定义有序列表中某个项目的编号值。-->
        <ol>
            <li value="10">项目十</li>
            <li>项目十一</li>
            <li>项目十二</li>
        </ol>
        <!--嵌套列表，列表可以相互嵌套，即在一个列表项中嵌套另一个列表。-->
        <ul>
            <li>水果
                <ul>
                    <li>苹果</li>
                    <li>香蕉</li>
                </ul>
            </li>
            <li>蔬菜</li>
        </ul>
        <!--定义描述列表，用于显示名词和对应的描述-->
        <dl>
            <dt>HTML</dt>
            <dd>用于创建网页的标记语言</dd>
            <dt>CSS</dt>
            <dd>用于样式设计和网页布局</dd>
        </dl>
        <!--在这个示例中，<select> 元素具有 name、multiple 和 size 属性。
            其中，multiple 属性允许多选，size 属性设置为 3，可见行数为 3。
            <option> 元素具有 value、selected 和 disabled 属性。
    其中，selected 属性设置为 true，表示香蕉默认选中，disabled 属性设置为 true，表示橙子被禁用。
value 属性设置了每个选项的实际值，但是这些值不会在用户界面上直接显示出来，
而是被用于在提交表单时识别选项的值。
在下拉列表框中，用户看到的是选项的文本内容（例如 "苹果"、"香蕉" 等），
但当用户选择了某个选项并提交表单时，
表单会提交该选项的 value 属性所定义的实际值（例如 "apple"、"banana" 等）。-->
        <select name="fruits" multiple size="3">
            <option value="apple">苹果</option>
            <option value="banana" selected>香蕉</option>
            <option value="orange" disabled>橙子（不可用）</option>
            <option value="grape">葡萄</option>
        </select>
    </body>
</html>
~~~

## 表格标签

1. \<table>：用于创建表格。它是表格的容器，包含一行或多行 \<tr> 元素，表示表格的行。
2. \<tr>：表示表格中的行。它是 \<table> 元素的子元素，包含一列或多列 \<th> 或 \<td> 元素。
3. \<th>：表示表头单元格，通常位于表格的顶部行或左侧列。它用于包含表头信息，如列标题或行标题。
4. \<td>：表示数据单元格，用于包含表格中的实际数据。

~~~html
<!DOCTYPE html>
<!--<html>: 定义根元素-->
<html>
  <body>
    <!-- table定义表格，border="1" 是 HTML 中 <table> 元素的一个属性设置，
        用于指定表格的边框宽度。当设置为 "1" 时，
        表示在表格的每个单元格和表格之间显示一个像素宽度的边框 -->
    <table border="1">
        <tr>
            <th>姓名</th>
            <th>年龄</th>
            <th>城市</th>
        </tr>
        <tr>
            <td>张三</td>
            <td>25</td>
            <td>北京</td>
        </tr>
        <tr>
            <td>李四</td>
            <td>30</td>
            <td>上海</td>
        </tr>
    </table>    
  </body>
</html>
~~~

## 表单标签

HTML 表单标签用于创建用户交互的表单，使用户能够向服务器发送数据。

| 标签             | 描述     | 属性                                                         |
| ---------------- | -------- | ------------------------------------------------------------ |
| \<form> \</form> | 表单标签 | action：定义表单数据提交的目标 URL                           |
|                  |          | \<input>：\<input> 标签用于创建各种输入控件，如文本框、单选按钮、复选框等。常见类型有：<br />**method**：定义表单提交的 HTTP 方法，常见取值为 "GET" 和 "POST"。<br />**text**：文本框。<br />**radio**：单选按钮。<br />**checkbox**：复选框。<br />**submit**：提交按钮。<br />**password**：创建一个密码输入框，用户输入的内容会被隐藏。<br />**reset**：创建一个重置按钮，用于将表单字段重置为初始值。<br />**button**：创建一个普通按钮，用于执行自定义的 JavaScript 操作。<br />**number**：创建一个数字输入框，只允许输入数字。<br />**date**：创建一个日期输入框，用于选择日期。<br />**search**：创建一个搜索框，用于输入搜索关键词。<br />**color**：创建一个颜色选择框，用于选择颜色。 |

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>用户注册表单</title>
</head>
<body>
    <h2>用户注册</h2>
<!--<form action="/register" method="post">：
    创建了一个表单，指定了表单数据提交的目标 URL 为 "/register"，并使用 POST 方法提交。
type="radio"：指定输入框的类型为单选按钮。单选按钮允许用户从一组选项中选择一个。
用户名：<input type="text"  required>：创建了一个文本框用于输入用户名，
required 属性表示这是一个必填字段。-->
    <form action="/register" method="post">

        用户名：<input type="text" id="user" name="user"  required><br/>

        性别：<br/><input type="radio" name="sex" value="male"> 男<br/>
             <input type="radio" name="sex" value="female"> 女<br/>
        <!--表单数据像后端服务器提交的时候，提交的是value值-->
        <!--注意，单选的时候必须要有name选项，对应的值要一致-->

        订阅邮件：<input type="checkbox" value="yes"><br/>

        国家：<select>
            <option id="china" value="china">中国</option>
            <option id="usa" value="usa">美国</option>
            <option id="uk" value="uk">英国</option>
        </select><br/>

        <input type="password" placeholder="请输入密码"><br/>

        <input type="reset" value="重置"><br/>

        <input type="button" value="点击我" onclick="alert('Hello!')"><br/>

        输入数字18-100：<input type="number" value="age" min="18" max="100"><br/>

        选择日期: <input type="date" value="date"><br/>

        <input type="search" name="query" placeholder="搜索..."><br/>

        <input type="color" name="color" value="color"><br/>

        <!--只读，不可修改-->
        <input type="text" value="只读，不可以修改" readonly><br/>

        <!--设置最多大字符数-->
        手机号：<input type="text" maxlength="11"><br/>

        <!--autocomplete:自动完成功能通常会根据用户以前输入的值来为用户提供建议或自动填充输入字段。
            如果将autocomplete属性设置为"off"，则会禁用浏览器的自动完成功能。-->
        <input type="text" autocomplete="off"><br/>

        <!-- 例子：允许上传多个文件的文件输入框 -->
        选择文件：<input type="file" multiple><br/>

        <!--允许选择多个选项
<input type="checkbox">：这个部分创建了一个复选框，允许用户选择多个选项。
id 属性：为每个复选框提供了一个唯一的标识符。这个标识符通常用于与标签相关联，
以便点击标签时选中相应的复选框。
name 属性：规定了在表单提交时这些复选框的名称。在这里，所有的复选框都有相同的名称 "fruit[]"，
末尾的 "[]" 表示这个字段将以数组的形式提交给后端。
value 属性：指定了每个复选框的值。在这个例子中，每个复选框分别表示不同的水果，
值分别为 "apple"、"banana" 和 "orange"。
<label>：这个元素提供了与复选框相关的标签文本。用户可以点击文本来选择相应的复选框。
for 属性：将 <label> 与相应的 <input> 元素关联起来，以确保点击标签时选中相应的复选框。
    这个属性的值应该与相应 <input> 元素的 id 属性值相匹配。
        -->
        选择多个水果：<br/>
        <input type="checkbox" id="fruit1" name="fruit[]" value="apple">
        <label for="fruit1">苹果</label>

        <input type="checkbox" id="fruit2" name="fruit[]" value="banana">
        <label for="fruit2">香蕉</label>

        <input type="checkbox" id="fruit3" name="fruit[]" value="orange">
        <label for="fruit3">橙子</label><br/>

        <label for="message">请输入您的消息：</label><br>
        <textarea id="message" name="message" rows="4" cols="50"></textarea><br/>

<!--<textarea> 元素创建了一个多行文本框。
id 属性用于唯一标识该文本框，name 属性用于在表单提交时标识该文本框的名称。
rows 和 cols 属性分别用于指定文本框的行数和列数。
这里，rows="4" 意味着看到的文本框默认有 4 行，cols="50" 意味着看到的文本框默认有 50 列。
<label> 元素用于为文本框提供标签，for 属性与文本框的 id 属性相匹配，
以确保点击标签时焦点会自动跳转到相应的文本框。-->
        <br/><input type="submit" value="提交">
    </form>
</body>
</html>
~~~

## div标签

当你在做一个网页时，你需要把页面分成不同的部分，有的部分放标题，有的部分放图片，有的部分放文本等等。

\<div>标签就像是一个透明的容器，你可以把其他元素放进去，然后通过CSS来设计这个容器的外观。它就像是一个盒子，可以把相关的东西放在一起，让网页看起来更有组织，更有层次。

~~~html
<!DOCTYPE html>
<html>
    <body>
        
    <div>
        <img src="https://img1.gamedog.cn/2018/09/07/2745860-1PZG00F10.jpg" alt="alternative_text">
    </div>
        
    <div>
        <h1>这是一个网页</h1>
    </div>
        
    </body>
</html>
~~~

# CSS

CSS，即层叠样式表（Cascading Style Sheets），可以用它来为HTML元素添加样式，是用于描述网页样式和布局的，它为网页提供了丰富的样式控制功能，包括字体、颜色、边框、背景、边距、布局等。

如，怎么设置字体是红色？怎么让内容显示在网页指定的位置？背景图片如何设置？

Vscode配置CSS属性自动补全，安装扩展插件：Autoprefixer

示例：

style.css放到html同目录中

~~~css
p{
    color: rgb(68, 0, 255);
}
~~~

~~~html
<!<!DOCTYPE>
<body>
    <link href="style.css" rel="stylesheet" />
    <div>
        <p>你好，https://edu.51cto.com</p>
    </div>
</body>
~~~

1. href属性指定的值是style.css，表示要链接的外部资源是名为style.css的CSS文件。这意味着HTML文档将会加载并应用style.css中定义的样式。

2. rel="stylesheet"：这是\<link>元素的另一个属性，用于指定被链接资源的关系。在这里，rel属性的值是stylesheet，表示被链接的资源是一个样式表。这告诉浏览器，被链接的资源是用于定义文档样式的。

## 选择器

选择器：选择HTML文档中元素的模式，可以根据元素的标签名、类名、ID、属性、位置关系等特征来选择元素，从而对这些元素应用样式或其他操作。CSS选择器允许你以非常精细的方式定位和操作文档中的元素，使得你能够对网页进行更灵活和精确的布局和样式控制。如p，就是对HTML中的p元素进行样式设计。

属性：要设置的样式属性，例如`color`（颜色）、`font-size`（字体大小）、`background-color`（背景颜色）等。

值：要应用到属性的具体样式值，可以是颜色值、长度值、字体名称等，取决于所选属性的要求。

上面整个结构称为规则集。color：black是声明。属性和对应的值保存到{}里。

### 元素选择器

通过HTML元素名称选择元素。

~~~css
h2 {
    color: blue;
}

p {
    font-size: 20px;
}

a {
    color:black;
    background-color: azure;
    font-size: 30px;
}
~~~

~~~html
<!DOCTYPE html>
<html>
    <head>
        <link href="style.css" rel="stylesheet"/>
    </head>
    <dody>
        <div>
            <h2>我是xxx</h2>
            <p>下面是链接</p>
            <a href="https://edu.51cto.com" target="_blank">欢迎</a>
        </div>
    </dody>
</html>
~~~

### 类选择器

通过HTML类名选择元素

~~~css
.title {
    font-size: 30px;
}

.content {
    color: blue;
    font-size: 50px;
}
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div>
    <h1 class="title"> 简历 </h1>
    <p> 介绍: </p>
    <a class="content" href="https://baike.baidu.com" target="_blank"> 百度百科 </p> 
    </div>
    </body>
</html>
~~~

### ID选择器

通过HTML的元素ID选择。

~~~css
#container {
    border: 1px solid black;
}

/* border: 设置边框
    1px：边框宽度1像素
     solid：实线
     black; 黑色边框 */
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="container">
        <h2>你好</h2>
        <p>欢迎</p>
    </div>
</body>
</html>

~~~

### 后代选择器

选择嵌套在另一个元素内的元素

~~~css
/* 选择 #container 元素内部的所有 p 元素，并将它们的颜色设置为红色 */
#container p {
    color: red;
}

/* 选择 #container 元素内部的 .content 元素内部的 p 元素，并将它们的字体设置为斜体 */
#container .content p {
    font-style: italic;
}
~~~

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>CSS后代选择器示例</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="container">
        <h1>标题</h1>
        <div class="content">
            <p>这是第一段内容。</p>
            <p>这是第二段内容。</p>
        </div>
        <div >
            <p>这是侧边栏内容。</p>
        </div>
    </div>
</body>
</html>
~~~

### 相邻兄弟选择器

选择紧接在另一个元素后面的兄弟元素

~~~css
/* 选择紧接在 h2 元素后面的 p 元素，并将它们的字体样式设置为斜体 */
h2 + p {
    font-style: italic;
}
~~~

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>相邻兄弟选择器示例</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h2>标题1</h2>
    <p>这是段落1。</p>
    <p>这是段落2。</p>
    <h2>标题2</h2>
    <p>这是段落3。</p>
    <p>这是段落4。</p>
</body>
</html>
~~~

### 通用选择器

选择所有元素

~~~css
/* 选择HTML页面上的所有元素，并将它们的边框样式设置为红色 */
* {
    border: 1px solid red;
}
~~~

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>通用选择器示例</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div>
        <h2>这是标题</h2>
        <p>这是段落1。</p>
        <p>这是段落2。</p>
    </div>
    <div>
        <h2>这是另一个标题</h2>
        <p>这是段落3。</p>
        <p>这是段落4。</p>
    </div>
</body>
</html>
~~~

### 属性选择器

选择具有特定属性的元素

~~~css
/* 选择具有 href 属性且属性值为 "#" 的 <a> 元素，并将它们的文字颜色设置为蓝色 */
a[href="#"] {
    color:brown;
}
~~~

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>属性选择器示例</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div>
    <a href="#">百度</a>
    </div>
    <div>
    <a href="#">课程</a>
    </div>
</body>
</html>
~~~

### 伪类选择器

选择元素的特殊状态

~~~css
/* 选择鼠标悬停在 <a> 元素上时的状态，并将其文字颜色设置为红色 */
a:hover {
    color: red;
}
~~~

~~~html
<!DOCTYPE html>
<html>
<link href="style.css" rel="stylesheet">
<body>
    <div>
        <a href="https://baike.baidu.com/">介绍</a>
    </div>
    <div>
        <a href="https://gitee.com/">gitee地址</a>
    </div>
    <div>
        <a href="https://edu.51cto.com/">课程</a>
    </div>
    <div>
        <a href="https://www.tup.tsinghua.edu.cn/">清华</a>
    </div>
</body>
</html>
~~~

### 伪元素选择器

选择元素的特殊部分

~~~css
/* 选择html文档每个 <p> 元素的第一行文字，并将其文字样式设置为斜体 */
p::first-line {
    font-style: italic;
}
~~~

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>伪元素选择器示例</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <p>这是一段文字<br/>
       你好
    </p>
</body>
</html>
~~~

## 样式表

### 外部样式表

CSS外部样式表是一种将 CSS规则集中存放在单独的文件中，链接到 HTML 页面的方式来应用样式的方法。这种方法使得可以将样式与HTML文档内容分离，提高了代码的可维护性和可重用性。

前面讲选择器的时候都是用的CSS外部样式表。

~~~css
h2 {
    color: blue;
}

p {
    font-size: 20px;
}

a {
    color:black;
    background-color: azure;
    font-size: 30px;
}
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <link href="style.css" rel="stylesheet" />
</head>
<body>
    <div>
    <h2>我</h2>
    <p>主页</p>
    <a href="https://edu.51cto.com" target="_blank">欢迎</a>
</div>
</body>
</html>
~~~

使用场景：

1. 多页面网站：对于包含多个页面的网站，外部样式表更适合用于统一管理整个网站的样式，可以通过在每个页面引入同一个外部样式表来保持样式的一致性。

2. 大型项目：对于较大的项目或团队开发，外部样式表更容易维护和管理，可以将样式规则集中存放在单独的样式文件中，方便团队协作和版本控制。

3. 性能优化：外部样式表可以利用浏览器的缓存机制，当多个页面共享同一个外部样式表时，可以减少页面加载时间，提高网站性能。

### 内部样式表

CSS内部样式表是一种将CSS规则集直接写在HTML文件内部的方法，而不是将样式规则放在外部的CSS文件中。通过在HTML文件的\<style>标签内部编写CSS代码，可以直接为HTML文档中的元素指定样式。

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>内部样式表示例</title>
    <style>
        /* 在 <style> 标签中定义内部样式表 */
        h1 {
            color: blue;
            font-size: 20px;
        }

        p {
            font-size: 18px;
            color: black;
        }
    </style>
</head>
<body>
    <h1>这是一个标题</h1>
    <p>这是一个段落。</p>
</body>
</html>
~~~

使用场景：
1.	特定页面样式：对于只需要在特定页面或特定部分应用样式的情况，内部样式表更适合，可以直接在HTML文件内部定义样式，避免了引入外部文件的额外开销。
2.	临时样式调整：在开发阶段或调试过程中，如果需要临时调整某个页面或元素的样式，可以直接在HTML文件内部使用内部样式表进行修改，而不必修改外部样式文件。
3.	样式独立性：对于特定的样式定义，如果不希望其他页面或元素受到影响，可以将样式规则直接嵌入到HTML文件内部，确保样式的独立性和局部性。

在实际应用中，外部样式表的使用频率更高一些，特别是对于大型项目和多页面网站。外部样式表可以提高代码的可维护性和可重用性，更适合用于统一管理整个项目的样式。而内部样式表通常用于一些特定的场景，如临时样式调整或特定页面样式定义，使用频率相对较低。

### 内联样式表

CSS内联样式表是一种直接将 CSS 样式规则写在 HTML 元素的 style 属性中的方法。这种方法使得可以为特定的 HTML 元素指定个性化的样式，而不必将样式规则放在外部的 CSS 文件或 HTML 文件的 \<style> 标签中。

~~~html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>内联样式表示例</title>
</head>
<body>
    <h1 style="color: blue; font-size: 20px;">这是一个标题</h1>
    <p style="font-size: 50px; color: black;">这是一个段落。</p>
</body>
</html>
~~~

内联样式表的使用相对较少，通常只在一些特定的场景下使用。以下是内联样式表的主要使用场景：
1.	个性化样式：当需要为特定的 HTML 元素指定个性化的样式时，可以使用内联样式表。例如，如果只需要为某个元素添加临时的样式调整，而不想修改外部或内部样式表，就可以使用内联样式表。
2.	邮件和简单页面：在编写邮件或简单的静态页面时，为了简化样式管理，有时会直接使用内联样式表。这样可以避免引入外部样式表或在 HTML 文件中定义样式。
3.	单个样式元素：当只需要对单个元素应用样式，并且该样式不会被其他元素共享时，可以考虑使用内联样式表。这样可以将样式与特定元素绑定在一起，提高了样式的局部性和可读性。

在大多数情况下，外部样式表或内部样式表更适合用于统一管理和维护整个网站或项目的样式。内联样式表用的相对会少一些。

## 字体设置

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>CSS字体样式设置</title>
    <style>
        /* 设置字体颜色为红色、背景色为浅灰色、字体大小为24像素、边框为1像素实线红色 */
        .red-text {
            color: red;
            background-color: lightgray;
            font-size: 24px;
            border: 1px solid red;
            margin: 10px;
        }

/*
border：
1px：边框像素
solid：实线边框，除了实线边框，还有如下几种：
dashed：虚线边框。
dotted：点线边框。
double：双线边框。
groove：3D凹陷边框。
ridge：3D凸起边框。
inset：3D内嵌边框。
outset：3D外嵌边框。
none：无边框。
此外，还可以使用 border-top-style、border-right-style、
border-bottom-style、border-left-style 分别设置上、右、下、左边框的样式。
*/
        /* 设置字体颜色为白色、背景色为黑色、字体大小为18像素、边框为2像素实线白色 */
        .white-text {
            color: white;
            background-color: black;
            font-size: 18px;
            border: 5px dashed red;
            margin: 10px;
        }

        /* 设置字体颜色为黑色、背景色为橙色、字体大小为20像素、边框为3像素实线黑色 */
        .black-text {
            color: black;
            background-color: orange;
            font-size: 20px;
            border: 3px dotted red;
            margin: 10px;
        }

        /* 设置字体颜色为橙色、背景色为白色、字体大小为22像素、边框为4像素实线橙色 */
        .orange-text {
            color: orange;
            background-color: white;
            font-size: 22px;
            border: 4px double orange;
            margin: 10px;
        }
        .green-text{
            color: green;
            background-color: red;
            font-size: 22px;
            border: 5px black;
            border-top-style:  dashed;
            border-right-style: double;
            border-bottom-style: groove;
            border-left-style: solid;
        }
    </style>
</head>
<body>
    <!-- 红色字体 -->
    <div class="red-text">红色字体</div>
    <!-- 白色字体 -->
    <div class="white-text">白色字体</div>
    <!-- 黑色字体 -->
    <div class="black-text">黑色字体</div>
    <!-- 橙色字体 -->
    <div class="orange-text">橙色字体</div>
    <div class="green-text">绿色字体</div>
</body>
</html>
~~~

## 背景图片

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  color: red;
  font-size: 20px;
  background-image: url("./领奖.png"); /*默认情况下，图像在水平和垂直方向上都重复，以覆盖整个元素。*/
  background-repeat: no-repeat; /*图像不重复*/
  background-position: center; /* 将背景图片在窗口中水平和垂直居中 */
  background-size: contain;/*背景图片会被等比例缩放，以完全包含在背景区域内，并且不会变形。*/
  background-attachment: fixed; /* 将背景图片固定在窗口中，不随元素滚动而滚动 注释掉这一行就会随着页面滚动而滚动 */
}
</style>
</head>
<body>

<h1>全球大会</h1>

<p>领奖</p>

</body>
</html>
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
body {
  color: red;
  font-size: 20px;
  background-image: url("./领奖.png"); /*默认情况下，图像在水平和垂直方向上都重复，以覆盖整个元素。*/
  background-repeat: no-repeat; /*图像不重复*/
  background-position: right top; /* 背景图像不会随页面的其余部分一起滚动*/
  background-attachment: fixed; /* 将背景图片固定在窗口中，不随元素滚动而滚动 */
}
</style>
</head>
<body>

<h1>全球大会</h1>

<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
<p>领奖</p>
</body>
</html>
~~~

## 内外边距

1. 内边距：控制元素内部内容与其边框之间的距离。
2. 外边距：控制元素与其相邻元素之间的距离。

内边距padding基本语法：

| 属性               | 用法                               | 描述                                   |
| ------------------ | ---------------------------------- | -------------------------------------- |
| padding            | **padding: 20px;**                 | 内边距上下左右都是20                   |
| padding            | **padding: 10px 20px 15px  25px;** | 内边距顺序是上右下左                   |
| padding            | **padding: 10px 20px ;**           | 上下内边距为 10px，左右内边距为 20px。 |
| **padding-top**    | **padding-top: 10px;**             | 上内边距像素是10                       |
| **padding-right**  | **padding-right: 10px;**           | 右内边距像素是10                       |
| **padding-bottom** | **padding-bottom****：10px**       | 下内边距像素是10                       |
| **padding-left**   | **padding-left****：10px**         | 左内边距像素是10                       |

外边距margin基本语法：

| 属性              | 用法                                  | 描述                                          |
| ----------------- | ------------------------------------- | --------------------------------------------- |
| margin            | margin**: 20px;**                     | 外边距上下左右都是20                          |
| margin            | margin**: 10px 20px 15px 25px;**      | 外边距顺序是上右下左                          |
| margin            | margin**: 10px 20px ;**               | 上下外边距为 10px，左右外边距为 20px。        |
| margin**-top**    | margin**-top: 10px;**                 | 上外边距像素是10                              |
| margin**-right**  | margin**-right: 10px;**               | 右外边距像素是10                              |
| margin**-bottom** | margin**-bottom**：10px               | 下外边距像素是10                              |
| margin**-left**   | margin**-left**：10px                 | 左外边距像素是10                              |
|                   | margin-left: auto; margin-right: auto | 元素会水平居中，因为左右外边距都设置为 auto。 |

~~~html
<!DOCTYPE html>
<html>
<head>
  <title>Padding and Margin Example</title>
  <style>
    .container {
      width: 600px;
      margin: 0 auto; /* 居中显示 */
      background-color: #f0f0f0;
      padding: 20px; /* 容器内边距 */
    }
    .item {
      width: 100px;
      height: 100px;
      background-color: #ccc;
      margin: 20px; /* 项目外边距 */
    }
/*
.container 类：
width: 600px;：设置容器的宽度为 600 像素。
margin: 0 auto;：将容器水平居中显示，这是通过将左右外边距设为 auto 实现的。
background-color: #f0f0f0;：设置容器的背景颜色为浅灰色。
padding: 20px;：给容器设置了上、右、下、左各 20px 的内边距。

.item 类：
width: 100px;、height: 100px;：设置每个项目的宽度和高度均为 100 像素。
background-color: #ccc;：设置项目的背景颜色为灰色。
margin: 20px;：给每个项目设置了上、右、下、左各 20px 的外边距。

这段代码创建了一个宽度为 600px 的容器，容器内部有 20px 的内边距。
在容器中包含多个宽高均为 100px 的项目，相邻项目之间有 20px 的外边距，
从而在视觉上形成了一种间隔。整个容器会水平居中显示在页面上，并且背景为浅灰色。

*/
  </style>
</head>
<body>
  <div class="container">
    <div class="item">1</div>
    <div class="item">2</div>
    <div class="item">3</div>
    <!-- 更多项目 -->
  </div>
</body>
</html>
~~~

