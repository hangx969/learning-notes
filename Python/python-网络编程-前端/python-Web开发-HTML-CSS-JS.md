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

# CSS基础语法

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

## display调整网页布局

CSS 的 display 属性定义了一个元素应该如何显示在页面中。通过设置不同的 display 值，可以使元素以块级、内联、弹性盒子等形式进行布局，从而更灵活地构建页面结构。

块级元素：

- 块级元素会独占一行，即使宽度设置为小于容器的宽度，也会占据一整行。

- 可以设置宽度、高度、外边距和内边距。

- 常见的块级元素有 \<div>、\<p>、\<h1> 到 \<h6>、\<form> 等。

内联元素：

- 内联元素会在同一行内显示，不会独占一行，只会占据它所需要的宽度。

- 不可以设置宽度和高度，设置宽度和高度会被忽略。

- 常见的内联元素有 \<span>、\<a>、\<strong>、\<em>、\<img> 等。

~~~html
<!<!DOCTYPE>
<style>
    .div1{
        background-color: blue
    }
    .div2{
        background-color: goldenrod
    }
    span{
        background-color: red
    }
</style>
<body>
  <div class="div1">
    这是第一个div标签
  </div>
  <div class="div2">
    这是第二个div标签
  </div>
  <span>这是span元素，属于行内元素</span>
</body>
~~~

### display属性block

元素显示为块级元素，会独占一行，可以设置宽度、高度以及外边距和内边距。

应用场景： 常用于让元素独占一行，比如段落、标题等。

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
/* 将所有段落显示为块级元素 */
p {
  display: block;
  background-color: lightblue;
  margin: 10px;
  padding: 10px;
}
</style>
</head>
<body>

<p>这是第一个段乱</p>
<p>这是第二个段落</p>

</body>
</html>
~~~

### display属性inline

元素显示为内联元素，会在同一行内显示，并且不会独占一行，不可以设置宽度和高度。

应用场景：常用于让元素与相邻元素在同一行内显示，比如链接、强调文字等。

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
/* 将所有链接显示为内联元素 */
a {
  display: inline;
  padding: 5px;
  background-color: lightblue;
}
</style>
</head>
<body>

<a href="#">Link 1</a>
<a href="#">Link 2</a>
<a href="#">Link 3</a>

</body>
</html>
~~~

### display属性inline-block

元素显示为内联块级元素，与 inline 类似，但是可以设置宽度和高度。

应用场景：常用于让元素在同一行内显示，并且可以设置宽度和高度，比如按钮、图片等。

~~~html
<!DOCTYPE html>
<style>
    button{
        display: inline-block;
        width: 100px;
        height: 50px;
        background-color: lightblue;
        margin: 10px;
    }
</style>

<body>
    <button>Button 1</button>
    <button>Button 2</button>
    <button>Button 3</button>
</body>
~~~

### display属性none

元素不显示，即在页面中不占据空间，相当于隐藏。

应用场景：常用于隐藏元素，比如通过 JavaScript 控制的显示/隐藏元素。

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
/* 将类名为 hidden 的元素隐藏 */
.hidden {
  display: none;
}
</style>
</head>
<body>

<p>这是没有定义隐藏模式的段落</p>
<p class="hidden">这是定义隐藏模式的段落</p>

</body>
</html>
~~~

### display属性Flex

display: flex 表示将一个容器元素变成一个 "Flex Container"（弹性容器），容器内的子元素将会按照一定的规则进行布局，这些规则由 Flexbox 模型所定义。

好处：
1.	简单易用：使用 display: flex; 可以很方便地实现灵活的布局
2.	响应式布局：弹性容器布局适用于各种屏幕尺寸和设备，使得页面可以轻松适应不同的浏览器窗口大小和设备类型。
3.	自适应布局：弹性容器布局可以根据容器的大小自动调整项目的排列和尺寸，使得页面的布局更加灵活和自适应。
4.	项目对齐：可以通过 justify-content 和 align-items 等属性控制项目在主轴和交叉轴上的对齐方式，实现灵活的对齐效果。

语法：

~~~css
.container {
  display: flex;
}
~~~

将具有 .container 类名的 HTML 元素转换为 Flex 容器：

- .container：这是一个 CSS 类选择器，用于选择 HTML 中具有 class="container" 属性的元素。

- display: flex;：将所选元素转换为 Flex 容器。一旦应用了 display: flex;，该容器内的子元素（项目）就可以按照 Flexbox 布局规则进行排列和对齐。

Flex的常用属性：

1.	flex-direction: row|row-reverse|column|column-reverse;： 定义主轴的方向，可选值有水平方向（row）、水平方向反向（row-reverse）、垂直方向（column）和垂直方向反向（column-reverse）。
2.	justify-content: flex-start|flex-end|center|space-between|space-around|space-evenly;： 定义项目在主轴上的对齐方式，可选值包括起点对齐、终点对齐、居中对齐、两端对齐、每个项目周围具有相同的空间以及每个项目周围和容器之间具有相同的空间。
3.	align-items: flex-start|flex-end|center|baseline|stretch;： 定义项目在交叉轴上的对齐方式，可选值包括起点对齐、终点对齐、居中对齐、基线对齐和拉伸对齐。
4.	flex-grow: \<number>;： 定义弹性元素的放大比例，默认为0，表示不放大，可以根据需要设置一个数字来进行放大。
5.	flex-shrink: \<number>;： 定义弹性元素的缩小比例，默认为1，表示可以缩小，可以根据需要设置一个数字来进行缩小。
6.	flex-basis: \<length>|auto;： 定义弹性元素在主轴上的初始大小，默认为 auto，即由元素自身决定大小，也可以设置一个固定长度。
7.	flex-wrap: nowrap：不对 flex 项目换行（默认）

示例：

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
<title>Flexbox Layout Demo</title>
<style>
/*选择HTML中的nav元素，将 nav 元素转换为 Flex 容器，使得内部的子元素（项目）可以使用 Flexbox 布局。*/
.nav {
  display: flex; 
  justify-content: center; /* 设置 Flex 容器中的子元素（项目）在主轴上居中对齐，即水平方向上居中对齐。 */
  background-color: lightblue;
}
/*定义一个nav-item类，选择html中具有class=nav-item的元素，nav-item中的元素是 nav 内的子元素（项目），即导航菜单的各个项目。*/
.nav-item {
  margin: 0 10px; /* 设置项目之间的间距 */
  padding: 5px 10px; /* 设置项目的内边距 */
  background-color: lightgreen;
}
</style>
</head>
<body>

<div class="nav">
  <div class="nav-item">Home</div>
  <div class="nav-item">About</div>
  <div class="nav-item">Services</div>
  <div class="nav-item">Contact</div>
</div>

</body>
</html>
~~~

水平排列，从左到右：

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-direction: row;
  background-color: blue;
}

.flex-container > div {
  background-color: gray;
  width: 90px;
  margin: 5px;
  text-align: center; /*元素内的文本内容在元素内水平居中显示。*/
  line-height: 50px; /*元素的行高为 50 像素。*/
  font-size: 16px;/*元素内的字体为16像素。*/
}
</style>
</head>
<body>
<h1>flex-direction 属性</h1>

<p>"flex-direction: row;" 水平排列（从左到右）：</p>

<div class="flex-container">
  <div>第1个div块</div>
  <div>第2个div块</div>
  <div>第3个div块</div>  
</div>

</body>
</html>
~~~

垂直排列，从上到下：

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-direction: column;
  background-color: blue;
}

.flex-container > div {
  background-color: gray;
  width: 90px;
  margin: 5px;
  text-align: center; /*元素内的文本内容在元素内水平居中显示。*/
  line-height: 50px; /*元素的行高为 50 像素。*/
  font-size: 16px;/*元素内的字体为16像素。*/
}
</style>
</head>
<body>
<h1>flex-direction 属性</h1>

<p>"flex-direction: column;" 垂直排列（从上到下）：</p>

<div class="flex-container">
  <div>第1个div块</div>
  <div>第2个div块</div>
  <div>第3个div块</div>  
</div>

</body>
</html>
~~~

水平排列，从右到左：

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-direction: row-reverse;
  background-color: blue;
}

.flex-container > div {
  background-color: gray;
  width: 90px;
  margin: 5px;
  text-align: center; /*元素内的文本内容在元素内水平居中显示。*/
  line-height: 50px; /*元素的行高为 50 像素。*/
  font-size: 16px;/*元素内的字体为16像素。*/
}
</style>
</head>
<body>
<h1>flex-direction 属性</h1>

<p>"flex-direction: row-reverse;" 水平排列（从右到左）：</p>

<div class="flex-container">
  <div>第1个div块</div>
  <div>第2个div块</div>
  <div>第3个div块</div>  
</div>
</body>
~~~

垂直排列，从下到上：

~~~html
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-direction: column-reverse;
  background-color: blue;
}

.flex-container > div {
  background-color: gray;
  width: 90px;
  margin: 5px;
  text-align: center; /*元素内的文本内容在元素内水平居中显示。*/
  line-height: 50px; /*元素的行高为 50 像素。*/
  font-size: 16px;/*元素内的字体为16像素。*/
}
</style>
</head>
<body>
<h1>flex-direction 属性</h1>

<p>"flex-direction: column-reverse;" 垂直排列（从下到上）：</p>

<div class="flex-container">
  <div>第1个div块</div>
  <div>第2个div块</div>
  <div>第3个div块</div>  
</div>

</body>
</html>

wrap.html：
<!DOCTYPE html>
<html>
<head>
<style>
.flex-container {
  display: flex;
  flex-wrap: wrap;
  background-color: blue;
}

.flex-container > div {
  background-color: gray;
  width: 90px;
  margin: 5px;
  text-align: center; /*元素内的文本内容在元素内水平居中显示。*/
  line-height: 50px; /*元素的行高为 50 像素。*/
  font-size: 30px;/*元素内的字体为30像素。*/
}
</style>
</head>
<body>
<h1> flex-wrap 属性</h1>

<p>" flex-wrap: wrap;" 必要时换行：</p>

<div class="flex-container">
  <div>第1个div块</div>
  <div>第2个div块</div>
  <div>第3个div块</div>  
  <div>第4个div块</div>  
  <div>第5个div块</div>  
  <div>第6个div块</div>  
  <div>第7个div块</div>  
  <div>第8个div块</div>  
  <div>第9个div块</div>  
  <div>第10个div块</div>  
  <div>第101个div块</div>  
  <div>第12个div块</div>  
  <div>第13个div块</div>  
  <div>第14个div块</div>  
  <div>第15个div块</div>  
  <div>第16个div块</div>  
  <div>第17个div块</div>  
  <div>第18个div块</div>  
</div>

</body>
</html>
~~~

# CSS响应式网页设计RSD

响应式网页设计（Responsive Web Design，简称RWD）是一种使网站能够适应不同设备和屏幕尺寸的设计方法。它通过使用弹性网格布局、媒体查询和弹性图片等技术，使网页能够在桌面电脑、平板电脑和手机等各种设备上呈现出最佳的用户体验。

CSS RWD 的主要特点：
1.	弹性网格布局（Flexible Grid Layout）：使用相对单位（如百分比）来定义网格和布局，使得页面元素可以根据屏幕尺寸进行自适应调整。
2.	媒体查询（Media Queries）：使用媒体查询可以根据设备特性（如屏幕宽度、像素密度等）应用不同的CSS样式，从而使页面在不同设备上呈现出不同的布局和样式。
3.	弹性图片（Flexible Images）：通过设置图片的最大宽度为100%，可以确保图片在不同设备上不会超出其容器，保持图片的比例和清晰度。
4.	视口设置（Viewport Meta Tag）：使用视口标签可以控制页面在移动设备上的显示方式，确保页面内容按照预期在屏幕上显示。

RWD页面布局案例

1. 博客网站：在桌面设备上，博客网站可能以两栏或三栏的形式呈现，包含文章列表、侧边栏、相关链接等；而在移动设备上，博客文章会以单列的形式显示，同时侧边栏内容被移动到页面底部，以适应较小的屏幕宽度。通过使用弹性网格布局和媒体查询，可以轻松实现这种响应式设计。

2. 电子商务网站：在桌面设备上，电子商务网站的商品列表可能会以多列的形式展示，同时包含大量的商品图片、价格和描述信息；而在移动设备上，商品列表可能会以单列的形式呈现，同时图片尺寸和文本描述会相应调整，以适应较小的屏幕尺寸。通过使用弹性网格布局和媒体查询，可以使商品页面在不同设备上呈现出最佳的用户体验。

RWD基本语法：

- **语法**：通过 **@media** 声明，后跟条件，例如设备宽度、高度等。
- **作用**：根据不同设备属性应用不同的 CSS 样式。

 ~~~css
 @media only screen and (max-width: 600px) {
  /* CSS 样式 */
 }
 ~~~

- **@media**: 媒体查询的关键词，用于声明一个媒体查询块。
- **only screen**: 表示此媒体查询仅适用于屏幕媒体，不适用于打印等其他媒体类型。
- **and**: 用于组合多个媒体特性。

- **(max-width: 600px)**: 表示当视口宽度小于等于 600 像素时应用该媒体查询内的 CSS 样式。

## 媒体查询

案例：根据不同的屏幕宽度设置不同的元素大小和样式。

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Responsively Sized Design Example</title>
<style>
/* 默认样式 */
.box {
  height: 100px; 
  margin-bottom: 20px;
}

/* RSD 媒体查询 */
@media only screen and (max-width: 600px) {
  .box {
    width: 100%; /* 屏幕宽度<=600px时，元素宽度为父元素宽度的 100% */
    background-color: #ff9999; /* 红色 */
  }
}

@media only screen and (min-width: 601px) and (max-width: 1024px) {
  .box {
    width: 50%; /* 屏幕宽度在601px到1024px时，元素宽度为父元素宽度的 50% */
    background-color: #99ff99; /* 绿色 */
  }
}

@media only screen and (min-width: 1025px) {
  .box {
    width: 33.33%; /* 屏幕宽度大于1025px时，元素宽度为父元素宽度的 33.33% */
    background-color: #9999ff; /* 蓝色 */
  }
}
</style>
</head>
<body>

<div class="box"></div>
<div class="box"></div>
<div class="box"></div>

</body>
</html>
~~~

## 流式布局

语法：使用百分比或相对单位（如 em、rem）而不是固定像素设置元素的尺寸。

作用：使布局能够随着视口大小的改变而自适应。

案例：根据不同的屏幕宽度自动调整大小和布局。

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Responsively Sized Design Example</title>
<style>
/* 默认样式 */
.container {
  width: 90%; /* 设置容器宽度为页面宽度的 90% */
  margin: 0 auto; /* 居中 */
  overflow: hidden; /* 清除浮动 */
}

.box {
  width: 30%; /* 设置盒子宽度为容器宽度的 30% */
  height: 100px;
  margin: 0 1.5%; /* 设置盒子之间的间距 ，上下边距0，左右边距是容器宽度的1.5%*/
  float: left; /* 浮动，让元素向左浮动，并且尽可能地靠近其容器的左边缘，让其他元素在其右侧排列，类似横向排列效果 */
  background-color: #ff9999; /* 设置背景颜色 */
}

/* RSD 媒体查询 */
@media only screen and (max-width: 600px) {
  .box {
    width: 100%; /* 在较小的屏幕下，元素宽度为父元素宽度的 100% */
  }
}
</style>
</head>
<body>

<div class="container">
  <div class="box"></div>
  <div class="box"></div>
  <div class="box"></div>
</div>

</body>
</html>
~~~

## 响应式图片

以下是一些常用的 CSS 属性来实现响应式图片：

~~~css
max-width 和 height：
img {
  max-width: 100%; /* 图片最大宽度为父元素宽度 */
  height: auto; /* 自适应高度，保持宽高比 */
}
/*这会确保图片在其容器内按比例缩放，并且不会超出容器宽度。*/
~~~

~~~css
width 和 height：
img {
  width: 100%; /* 图片宽度为父元素宽度 */
  height: auto; /* 自适应高度，保持宽高比 */
}
/*这会让图片填满其容器的宽度，并自适应调整高度以保持宽高比。*/
~~~

~~~css
object-fit 和 object-position：
img {
  width: 100%; /* 图片宽度为父元素宽度 */
  height: 300px; /* 固定高度 */
  object-fit: cover; /* 图片填充容器并保持宽高比，可能会裁剪部分内容 */
  object-position: center; /* 图片在容器中居中显示 */
}
/*这会让图片以 cover 的方式填充容器，并在容器中居中显示，不会变形，并且可能会裁剪部分内容。*/
~~~

案例：希望图片在小屏幕设备上占据整个屏幕宽度，在大屏幕设备上宽度固定为50%。

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Responsive Image Example</title>
    <style>
        /* 全局样式 */
        body {
            font-family: Arial, sans-serif; 
/*字体族（font-family），它控制着页面上文本的显示字体，首选使用Arial字体来显示文本，如果用户设备上没有Arial字体，则使用系统默认的无衬线字体来显示文本。这样做是为了保证文本的可读性和一致性，因为不同的设备上可能会有不同的字体可用。*/

/*“无衬线字体”（sans-serif）是一种没有装饰性笔画的字体风格。在字体设计中，术语“衬线”指的是字母笔画的额外部分，通常出现在字母的末端、转角和交叉点。无衬线字体是指不具有这种额外笔画的字体，因此看起来更简洁和清晰。*/
            margin: 0;
            padding: 0;
        }

        header {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 20px 0;
        }

        /* 图片样式 */
        img {
            max-width: 100%;/*最大宽度为100%*/
            height: auto; /*高度自动调整以保持原始宽高比*/
            display: block; /*将元素显示为块级元素，其前后都会自动换行。*/
            margin: 0 auto; /* 水平居中显示，上下外边距为0，左右外边距为自动。 */
        }

        /* 内容区域样式 */
        .content {
            padding: 20px;
        }

/* 媒体查询：在小屏幕上，图片宽度为100%；在屏幕宽度大于等于768像素时，图片的宽度将被设置为其所在容器（父元素）宽度的50% */
        @media screen and (min-width: 768px) {
            img {
                width: 50%; 
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>响应式图片示例</h1>
    </header>
    <div class="content">
        <img src="https://via.placeholder.com/800x400" alt="描述">
        <p>这里是一段文本内容。</p>
    </div>
</body>
</html>
~~~

## 视口元标签

~~~html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
~~~

这段代码告诉浏览器如何在移动设备上显示网页：

1. \<meta> 标签用于在 HTML 中添加元数据（metadata），这些元数据提供了关于网页的信息。
2. 在这个 \<meta> 标签中，**name** 属性被设置为 **"viewport"**，这表示这个元数据是用来控制视口的。
3. **content** 属性的值是 **"width=device-width, initial-scale=1.0"**。这告诉浏览器：让网页的宽度和设备的宽度一样，并且初始缩放比例应该为1.0。

这段代码确保网页在移动设备上显示时，大小合适，并且不会自动进行缩放，以提供更好的用户体验。

## RSD视频设计

~~~html
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>

* {
  box-sizing: border-box;
}
/* *表示通用选择器，代表匹配所有元素，然后给它们应用了一个样式规则 box-sizing: border-box;。
详细解释这个样式规则：
box-sizing: 这是一个CSS属性，告诉浏览器使用边框盒模型来计算元素的宽度和高度
border-box：这是 box-sizing 的一个值，当你设置一个元素的宽度为100px时，这个宽度将包括元素的内容、内边距和边框，而不会在它之外增加额外的空间。*/

video {
  width: 100%;
  height: auto;
}
/* width: 100%; 让视频在其容器内占据整个宽度，而 height: auto; 则保证视频的高度按比例自动调整，以保持视频的原始宽高比。*/

[class*="col-"] {
  float: left;
  padding: 15px;
  width: 100%;
}
/*
[class*="col-"]：这是一个属性选择器，[class*="col-"] 表示选择所有类名中包含 col- 的元素。
例如，.col-1、.col-2、.col-abc 等类名都会被选中。

float: left;：这是 CSS 属性，用于指定元素的浮动方式。
在这里，设置为 left，表示元素将向左浮动，允许其他内容在其右侧显示。

padding: 15px;：这是 CSS 属性，用于指定元素的内边距大小。
在这里，设置为 15px，意味着元素的内边距为 15px，这会在元素的内容和边框之间添加 15px 的空白区域。

width: 100%;：这是 CSS 属性，用于指定元素的宽度。
在这里，设置为 100%，意味着元素的宽度将填满其父容器的宽度，即占据一行的全部空间。
*/
@media only screen and (min-width: 600px) {
  .col-small-1 {width: 50px;}
  .col-small-2 {width: 100px;}
  .col-small-3 {width: 150px;}
  .col-small-4 {width: 200px;}
  .col-small-5 {width: 250px;}
  .col-small-6 {width: 300px;}
  .col-small-7 {width: 350px;}
  .col-small-8 {width: 400px;}
  .col-small-9 {width: 450px;}
  .col-small-10 {width: 500px;}
  .col-small-11 {width: 550px;}
  .col-small-12 {width: 600px;}
}
/*这部分代码定义了一个媒体查询，屏幕宽度大于等于 600px 的情况下,
为具有类名 .col-small-1 到 .col-small-12 的元素设置了不同的宽度*/

@media only screen and (min-width: 768px) {
  .col-medium-1 {width: 100px;}
  .col-medium-2 {width: 200px;}
  .col-medium-3 {width: 300px;}
  .col-medium-4 {width: 400px;}
  .col-medium-5 {width: 500px;}
  .col-medium-6 {width: 600px;}
  .col-medium-7 {width: 700px;}
  .col-medium-8 {width: 800px;}
  .col-medium-9 {width: 900px;}
  .col-medium-10 {width: 1000px;}
  .col-medium-11 {width: 1100px;}
  .col-medium-12 {width: 1200px;}
}
/*这部分代码定义了一个媒体查询，屏幕宽度大于等于 768px 的情况下,
为具有类名 .col-medium-1 到 .col-medium-12 的元素设置了不同的宽度*/

html {
  font-family: Arial, sans-serif;
}
/*这段代码将整个 HTML 文档的字体设置为 Arial 字体，如果用户的设备不支持 Arial 字体，
则会使用默认的 sans-serif 字体作为备选。*/
.header {
  background-color: #FF5722;
  color: #ffffff;
  padding: 15px;
}
/*这段代码应用于具有类名 .header 的元素，它设置了该元素的背景颜色为 #FF5722（橙色），文本颜色为白色，
内边距为 15 像素。通常，.header 类用于定义网页的标题或页眉部分。*/

.menu ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
}
/*这段代码应用于.menu类中的 <ul> 元素内部的所有元素，它将无序列表的默认样式去除，
包括列表项前的标志（如圆点或数字），并且去除了列表的外边距和内边距，使得列表紧凑且内容靠近。*/
.menu li {
  padding: 8px;
  margin-bottom: 7px;
  background-color: #FF9800;
  color: #ffffff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
}
/*这段代码应用于具有类名 .menu 的列表项 <li> 元素，它设置了列表项的内边距、下边距、背景颜色、
文本颜色以及阴影效果。在鼠标悬停在列表项上时，背景颜色会变成 #F57C00。

background-color 属性用于设置元素的背景颜色。
在这里，设置背景颜色为 #FF9800，即橙色。

color 属性用于设置元素内文本的颜色。
在这里，设置文本颜色为 #ffffff，即白色。

box-shadow 属性用于在元素周围创建阴影效果。
这个属性由多个参数组成：
0 1px 3px rgba(0,0,0,0.12): 这是第一个阴影的设置。

0: 表示阴影的水平偏移量。在这里，水平偏移量设置为 0，表示阴影不在水平方向上偏移。
1px: 表示阴影的垂直偏移量。在这里，垂直偏移量设置为 1px，表示阴影向下偏移 1 像素。
3px: 表示阴影的模糊半径。在这里，模糊半径设置为 3px，表示阴影的边缘会呈现出一个模糊的效果，模糊半径越大，阴影越模糊。
rgba(0,0,0,0.12): 表示阴影的颜色和透明度。在这里，设置为黑色（RGB 值为 0,0,0）并且透明度为 0.12。这里使用了 RGBA 颜色表示法，其中最后一个参数表示透明度，数值范围从 0（完全透明）到 1（完全不透明）。
,: 用于分隔多个阴影效果。

0 1px 2px rgba(0,0,0,0.24): 这是第二个阴影的设置，与第一个阴影设置类似，只是参数略有不同。

0: 水平偏移量为 0。
1px: 垂直偏移量为 1px。
2px: 模糊半径为 2px。
rgba(0,0,0,0.24): 颜色为黑色，透明度为 0.24。
这两个阴影效果组合在一起，为元素创建了两层阴影，第一层阴影具有较大的模糊半径和较低的透明度，而第二层阴影具有较小的模糊半径和较高的透明度。这样的设置通常用于营造元素的立体感或突出元素在页面上的层次感。
*/
.menu li:hover {
  background-color: #F57C00;
}
/*
.menu li:hover: 这是一个选择器，它指定了当鼠标悬停在具有 .menu li 类的列表项上时应用的样式。

background-color: #F57C00;: 这是应用于鼠标悬停时背景颜色的样式规则。

background-color: 这是CSS属性，用于设置元素的背景颜色。
#F57C00: 这是十六进制颜色代码，表示橙色。在这里，当鼠标悬停在列表项上时，背景颜色将变为橙色。
因此，这段代码的作用是当鼠标悬停在具有 .menu li 类的列表项上时，改变背景颜色为橙色，从而提供一种视觉反馈，指示用户当前所选的列表项。
*/

.aside {
  background-color: #FF9800;
  padding: 15px;
  color: #ffffff;
  text-align: center;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
}
/*
background-color: #FF9800;: 这是设置侧边栏的背景颜色为橙色（#FF9800）的样式规则。
padding: 15px;: 这是设置侧边栏的内边距为 15 像素的样式规则。内边距是指元素内容与元素边框之间的空白区域。
color: #ffffff;: 这是设置侧边栏内文本颜色为白色的样式规则。
text-align: center;: 这是设置侧边栏内文本的水平居中对齐的样式规则。
font-size: 14px;: 这是设置侧边栏内文本的字体大小为 14 像素的样式规则。
box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);: 这是为侧边栏添加阴影效果的样式规则。
0 1px 3px rgba(0,0,0,0.12): 这是第一个阴影的设置，与之前解释的相同。
,: 用于分隔多个阴影效果。
0 1px 2px rgba(0,0,0,0.24): 这是第二个阴影的设置，与之前解释的相同。
综上所述，这段代码的作用是设置侧边栏的背景颜色为橙色，内边距为 15 像素，文本颜色为白色，文本水平居中对齐，字体大小为 14 像素，并为侧边栏添加了两层阴影效果，用于增强其视觉效果和立体感。
*/
.footer {
  background-color: #FF5722;
  color: #ffffff;
  text-align: center;
  font-size: 12px;
  padding: 15px;
}

</style>
    
</head>
<body>

<div class="header">
  <h1>北京</h1>
</div>

<div class="col-small-4 col-medium-3 menu">
    <ul>
      <li>地标</li>
      <li>文化</li>
      <li>美食</li>
      <li>购物</li>
    </ul>
  </div>

<!--这个 div 元素定义了菜单栏的部分。具有 col-small-4 和 col-medium-3 、menu类
    这表明它在小屏幕下占据页面宽度的四分之一，在中等屏幕下占据页面宽度的三分之一。
    菜单栏内包含一个无序列表 <ul>，其中有四个列表项 <li>，
        分别是 "地标"、"文化"、"美食" 和 "购物"。
-->
  <div class="col-small-6 col-medium-6">
    <h1>欢迎来到北京</h1>
    <p>北京，是中国的首都，也是中国的政治、文化和国际交往中心。拥有悠久的历史和丰富的文化底蕴，是中国最具代表性的城市之一。京市成功举办夏奥会与冬奥会，成为全世界第一个“双奥之城”。</p>
    <video width="400" controls>
      <source src="北京.mp4" type="video/mp4">
      Your browser does not support HTML5 video.
    </video>
  </div>
<!--
这个 div 元素定义了页面内容的部分。具有 col-small-6 和 col-medium-6 类，
这表明它在小屏幕下占据页面宽度的一半，在中等屏幕下占据页面宽度的一半。
它包含一个 <h1> 标题，显示着 "欢迎来到北京"，以及一段文字描述北京的信息。
    此外，还有一个 <video> 元素用于播放名为 "北京.mp4" 的视频文件。
    如果浏览器不支持HTML5视频，则显示 "Your browser does not support HTML5 video." 的提示信息。
-->
  <div class="col-small-2 col-medium-3">
    <div class="aside">
      <h2>历史</h2>
      <p>北京有着悠久的历史，作为中国古都之一

<!--
这个 div 元素定义了侧边栏的部分。
具有 col-small-2 和 col-medium-3 类，这表明它在小屏幕下占据页面宽度的 1/6，
在中等屏幕下占据页面宽度的 1/4。侧边栏内有一个标题 <h2> 显示着 "历史"，以及一段文字描述北京的历史信息。
-->
~~~

# JavaScript

JS：Javascript，是一种解释型语言，不需要编译，直接嵌入或外部引用。用于实现网页的动态行为和交互功能。

主要特点：

1）交互性：增强用户交互，动态更新内容，处理事件（如点击、悬停等），以及与服务器进行数据交互（如 AJAX）。

2）动态性：可以在网页加载后动态修改 HTML 和 CSS，响应用户操作。

3）丰富的API：提供对DOM（文档对象模型）的操作、事件处理、定时器、AJAX请求等功能。

在实际开发中，HTML、CSS 和 JavaScript 通常一起使用：
1.	HTML 用来定义网页的内容和结构。
2.	CSS 用来设计网页的样式和布局。
3.	JavaScript 用来实现网页的动态功能和用户交互。

学习 JavaScript对于学习和使用 Vue 及其他前端框架至关重要

vscode安装js自动补全插件：

1. JavaScript code snippets
2. Javascript and TypeScript Nightly
3. JS JSX Snippets

案例1：外部定义js，导入到html文档

~~~javascript
alert("你好，欢迎访问我的网站！");
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>外部 JavaScript 示例</title>
</head>
<body>
    <h1>欢迎学习 JavaScript!</h1>
    <p>页面加载时将显示一条消息。</p>

    <!-- 引入外部 JavaScript 文件 -->
    <script src="script.js"></script>
</body>
</html>
~~~

案例2（直接在html文档内部引入js语法）：

~~~html
<!DOCTYPE html>
<html>
    <head>
        <title>JavaScript入门案例</title>
    </head>>
    <body>
        <h1>欢迎学习Js</h1>
        <p>点击下面的按钮显示一条消息:</p>
        <button onclick="displayMessage()">点我</button>
    <script>
        //这是一个简单的js函数
        function displayMessage(){
            //使用alert函数线是一条消息
            alert("你好，世界！")
        }
    </script>
    </body>
</html>
~~~

## 变量

变量用于存储数据。在 JavaScript 中，变量可以使用 var、let 和 const 进行声明。

1）使用 var 声明的变量可以重新赋值和重新声明

~~~javascript
var x = 10;
x = 20;
var x = 30;
~~~

2）使用 let 声明的变量可以重新赋值但不能重新声明

~~~javascript
let y = 10;
y = 20;
let y = 30; // 会导致错误：SyntaxError: Identifier 'y' has already been declared
~~~

3）使用 const 声明的变量是常量，不能重新赋值和重新声明

~~~javascript
const z = 10;
z = 20; // 会导致错误：TypeError: Assignment to constant variable.
const z = 30; // 会导致错误：SyntaxError: Identifier 'z' has already been declared
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript 变量示例</title>
</head>
<body>
    <h1>JavaScript 变量示例</h1>
    <p id="varExample"></p>
    <p id="letExample"></p>
    <p id="constExample"></p>

    <!-- 内部引用 JavaScript -->
    <script>
        // 使用 var 声明变量
        var varVariable = "8";
        // 使用 let 声明变量
        let letVariable = "6";
        // 使用 const 声明变量
        const constVariable = "3.1415926";

        // 将变量值显示在网页上
        document.getElementById("varExample").textContent = varVariable;
        document.getElementById("letExample").textContent = letVariable;
        document.getElementById("constExample").textContent = constVariable;

        //可以在控制台输出内容
        console.log(document.getElementById("varExample").textContent)

    </script>
</body>
</html>
~~~

## 数据类型

1. 原始类型

  数字（Number）：整数和浮点数

  ~~~javascript
  let num = 42;
  let pi = 3.14;
  ~~~

  字符串（String）：文本数据

  ~~~javascript
  let str = "Hello, World!";
  ~~~

  布尔值（Boolean）：真（true）或假（false）

  ~~~javascript
  let isTrue = true;
  let isFalse = false;
  ~~~

  null：表示空值

  ~~~javascript
  let emptyValue = null;
  ~~~

  undefined：变量未赋值时的默认值

  ~~~javascript
  let notAssigned;
  ~~~

2. 引用类型

  对象（Object）：键值对的集合

  ~~~javascript
  let person = {
   name: "Alice",
   age: 25
  };
  ~~~

  数组（Array）：有序的元素集合

  ~~~javascript
  let numbers = [1, 2, 3, 4, 5];
  ~~~

  函数（Function）：可调用的代码块

  ~~~javascript
  function greet(name) {
   return "Hello, " + name + "!";
  }
  ~~~

案例：

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript 数据类型示例</title>
</head>
<body>
    <h1>JavaScript 数据类型示例</h1>
    <p id="numberExample"></p>
    <p id="stringExample"></p>
    <p id="booleanExample"></p>
    <p id="nullExample"></p>
    <p id="undefinedExample"></p>
    <p id="objectExample"></p>
    <p id="arrayExample"></p>
    <p id="functionExample"></p>

    <!-- 内部引用 JavaScript -->
    <script>
        // 数字
        let num = 42;
        console.log("Number:", num, typeof num);
        document.getElementById("numberExample").textContent = "Number: " + num;

        // 字符串
        let str = "Hello, World!";
        console.log("String:", str, typeof str);
        document.getElementById("stringExample").textContent = "String: " + str;

        // 布尔值
        let isTrue = true;
        console.log("Boolean:", isTrue, typeof isTrue);
        document.getElementById("booleanExample").textContent = "Boolean: " + isTrue;

        // null
        let emptyValue = null;
        console.log("Null:", emptyValue, typeof emptyValue);
        document.getElementById("nullExample").textContent = "Null: " + emptyValue;

        // undefined
        let notAssigned;
        console.log("Undefined:", notAssigned, typeof notAssigned);
        document.getElementById("undefinedExample").textContent = "Undefined: " + notAssigned;
        
        // 对象
        let person = {
            name: "Alice",
            age: 25
        };
        console.log("Object:", person, typeof person);
        document.getElementById("objectExample").textContent = "Object: " + JSON.stringify(person);

        // 数组
        let numbers = [1, 2, 3, 4, 5];
        console.log("Array:", numbers, typeof numbers);
        document.getElementById("arrayExample").textContent = "Array: " + numbers.join(", ");

        // 函数
        function greet(name) {
            return "Hello, " + name + "!";
        }
        console.log("Function:", greet("World"), typeof greet);
        document.getElementById("functionExample").textContent = "Function: " + greet("World");
    </script>
</body>
</html>
~~~

## 运算符

~~~javascript
let a = 10;
let b = 20;

let sum = a + b; // 算术运算
let isEqual = (a == b); // 比较运算
let andCondition = (a > 5 && b < 25); // 逻辑运算
~~~

~~~html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript 运算符示例</title>
</head>
<body>
    <h1>JavaScript 运算符示例</h1>
    <p id="result"></p>

    <script>
        // 数字运算示例
        let num1 = 11; // 定义一个数字变量 num1
        let num2 = 5;  // 定义一个数字变量 num2

        // 加法运算：将 num1 和 num2 相加，并将结果赋值给 additionResult 变量
        let additionResult = num1 + num2;
        console.log("num1 + num2:", additionResult, typeof additionResult);

        // 减法运算：将 num1 减去 num2，并将结果赋值给 subtractionResult 变量
        let subtractionResult = num1 - num2;
        console.log("num1 - num2:", subtractionResult, typeof subtractionResult);

        // 乘法运算：将 num1 乘以 num2，并将结果赋值给 multiplicationResult 变量
        let multiplicationResult = num1 * num2;
        console.log("num1 * num2:", multiplicationResult, typeof multiplicationResult);

        // 除法运算：将 num1 除以 num2，并将结果赋值给 divisionResult 变量
        let divisionResult = num1 / num2;
        console.log("num1 / num2:", divisionResult, typeof divisionResult);

        // 取余运算：获取 num1 除以 num2 的余数，并将结果赋值给 moduloResult 变量
        let moduloResult = num1 % num2;
        console.log("num1 % num2:", moduloResult, typeof moduloResult);

        // 幂运算：将 num1 的 num2 次幂，并将结果赋值给 exponentiationResult 变量
        let exponentiationResult = num1 ** num2;
        console.log("num1 ** num2:", exponentiationResult, typeof exponentiationResult);

        // 字符串运算示例
        let str1 = "Hello, "; // 定义一个字符串变量 str1
        let str2 = "World!";  // 定义一个字符串变量 str2

        // 字符串拼接：将 str1 和 str2 进行拼接，并将结果赋值给 concatenationResult 变量
        let concatenationResult = str1 + str2;
        console.log("str1 + str2:", concatenationResult, typeof concatenationResult);

        // 比较运算示例
        let a = 10; // 定义一个数字变量 a
        let b = 5;  // 定义一个数字变量 b

        // 大于运算：判断 a 是否大于 b，并将结果赋值给 greaterThanResult 变量
        let greaterThanResult = a > b;
        console.log("a > b:", greaterThanResult, typeof greaterThanResult);

        // 小于运算：判断 a 是否小于 b，并将结果赋值给 lessThanResult 变量
        let lessThanResult = a < b;
        console.log("a < b:", lessThanResult, typeof lessThanResult);

        // 大于等于运算：判断 a 是否大于等于 b，并将结果赋值给 greaterThanOrEqualResult 变量
        let greaterThanOrEqualResult = a >= b;
        console.log("a >= b:", greaterThanOrEqualResult, typeof greaterThanOrEqualResult);

        // 小于等于运算：判断 a 是否小于等于 b，并将结果赋值给 lessThanOrEqualResult 变量
        let lessThanOrEqualResult = a <= b;
        console.log("a <= b:", lessThanOrEqualResult, typeof lessThanOrEqualResult);

        // 等于运算：判断 a 是否等于 b，并将结果赋值给 equalityResult 变量
        let equalityResult = a === b;
        console.log("a === b:", equalityResult, typeof equalityResult);

        // 不等于运算：判断 a 是否不等于 b，并将结果赋值给 inequalityResult 变量
        let inequalityResult = a !== b;
        console.log("a !== b:", inequalityResult, typeof inequalityResult);

        // 逻辑运算示例
        let isTrue = true;  // 定义一个布尔值变量 isTrue，其值为 true
        let isFalse = false; // 定义一个布尔值变量 isFalse，其值为 false

        // 与运算：判断 isTrue 和 isFalse 是否同时为 true，并将结果赋值给 andResult 变量
        let andResult = isTrue && isFalse;
        console.log("isTrue && isFalse:", andResult, typeof andResult);

        // 或运算：判断 isTrue 和 isFalse 是否至少有一个为 true，并将结果赋值给 orResult 变量
        let orResult = isTrue || isFalse;
        console.log("isTrue || isFalse:", orResult, typeof orResult);

        // 非运算：判断 isTrue 是否为 false，并将结果赋值给 notResult 变量
        let notResult = !isTrue;
        console.log("!isTrue:", notResult, typeof notResult);

        // 自增自减运算示例
        let x = 5; // 定义一个数字变量 x，其值为 5

        // 自增运算：将 x 的值加 1，并将结果赋值给 x，然后打印结果
        console.log("x++:", x++, typeof x);
        console.log("++x:", ++x, typeof x);
        console.log("x--:", x--, typeof x);
        console.log("--x:", --x, typeof x);

        // 将结果显示在页面上
        let resultElement = document.getElementById("result");
        resultElement.textContent = `运算结果：
        ${additionResult}, 
        ${subtractionResult}, 
        ${multiplicationResult}, 
        ${divisionResult}, 
        ${moduloResult}, 
        ${exponentiationResult}, 
        ${concatenationResult}, 
        ${greaterThanResult}, 
        ${lessThanResult}, 
        ${greaterThanOrEqualResult}, 
        ${lessThanOrEqualResult},
         ${equalityResult}, 
         ${inequalityResult}, 
         ${andResult}, 
         ${orResult}, 
         ${notResult}, 
         ${x}`;
    </script>
</body>
</html>
~~~

## 控制结构

1. for循环：for循环用于重复执行一段代码，通常用于已知循环次数的情况。

   ~~~javascript
   // 使用 for 循环打印数字 1 到 5
   for (let i = 1; i <= 5; i++) {
       console.log(i);
   }
   ~~~

2. while循环：while循环用于在指定条件为真时重复执行一段代码，通常用于未知循环次数的情况。

  ~~~javascript
  // 使用 while 循环打印数字 1 到 5
  let j = 1;
  while (j <= 5) {
   console.log(j);
   j++;
  }
  ~~~

3. if..else条件语句：if...else用于根据指定条件执行不同的代码块。

   ~~~javascript
   // 使用 if...else 语句判断一个数的正负性
   let num = -5;
   if (num > 0) {
       console.log("数字是正数");
   } else if (num < 0) {
       console.log("数字是负数");
   } else {
       console.log("数字是零");
   }
   ~~~

4. switch语句：switch语句用于根据表达式的值执行不同的代码块。

   ~~~javascript
   // 使用 switch 语句根据星期几输出不同的提示信息
   let day = 7;
   switch (day) {
       case 1:
           console.log("星期一");
           break;
       case 2:
           console.log("星期二");
           break;
       case 3:
           console.log("星期三");
           break;
       case 4:
           console.log("星期四");
           break;
       case 5:
           console.log("星期五");
           break;
       case 6:
           console.log("星期六");
           break;
       case 7:
           console.log("星期日");
           break;
       default:
           console.log("无效的日期");
   }
   ~~~

案例：

~~~html
<!DOCTYPE html>

<html>
    <body>
        <script>
            for(let i=1; i<=5; i++){
                console.log(i)
            }
        </script>

        <script>
            let j=1
            while(j<=5){
                console.log("while,",j)
                j++
            }
        </script>

        <script>
            let num =-5
            if(num > 0){
                console.log("数字是正数:", num)
            }else if(num < 0){
                console.log("数字是负数:", num)
            }else{
                console.log("数字是0:", num)
            }
        </script>

        <script>
            let day =7 
            switch(day){
                case 1:
                    console.log("星期一")
                    break
                case 2:
                    console.log("星期二")
                    break
                case 3:
                    console.log("星期三")
                    break                    
                case 4:
                    console.log("星期四")
                    break    
                case 5:
                    console.log("星期五")
                    break       
                case 6:
                    console.log("星期六")
                    break     
                case 7:
                    console.log("星期日")
                    break                                     
            }
        </script>
    </body>
</html>
~~~

## 函数

~~~html
<!DOCTYPE html>
<html>
<body>
<script>
    
// 定义一个名为 greet 的函数，接受一个参数 name
function greet(name) {
    
// 在函数内部，使用传入的参数 name 构建一个问候语句，并返回该语句
    return "Hello, " + name + "!";
}

// 调用 greet 函数并传入参数 "World"
let greeting = greet("World");

// 在控制台打印函数返回的结果
console.log(greeting); // 输出: Hello, World!

// 定义一个名为 add 的函数，接受两个参数并返回它们的和
function add(a, b) {

    // 将传入的两个参数相加，并返回结果
    return a + b;
}

// 调用 add 函数并传入参数 5 和 3
let sum = add(5, 3);

// 在控制台打印函数返回的结果
console.log(sum); // 输出: 8

</script>
</body>
</html>
~~~

## 对象和数组

1. 对象：对象是键值对的集合，每个键值对称为对象的属性和值。对象的属性可以是任何数据类型，包括字符串、数字、布尔值、数组、甚至其他对象。

~~~javascript
// 定义一个名为 person 的对象，包含姓名、年龄和城市属性
let person = {
    name: "zhangsan",
    age: 30,
    city: "China"
};


// 访问对象的属性并打印输出
console.log(person.name); // 输出: zhangsan
console.log(person.age);  // 输出: 30
console.log(person.city); // 输出:China
~~~

2. 数组：数组是有序的数据集合，其中的每个元素都有一个对应的数字索引。数组可以包含任何数据类型的元素，包括数字、字符串、布尔值、对象、甚至其他数组。

~~~javascript
// 定义一个名为 numbers 的数组，包含一组数字元素
let numbers = [1, 2, 3, 4, 5];

// 访问数组的元素并打印输出
console.log(numbers[0]); // 输出: 1
console.log(numbers[2]); // 输出: 3
console.log(numbers.length); // 输出: 5，数组的长度为 5

// 使用循环遍历数组并打印每个元素
for (let i = 0; i < numbers.length; i++) {
    console.log(numbers[i]);
}
~~~
