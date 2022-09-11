# MySQL入门

![MySQL面试导图](F:\KEEP-WORKING\就业\校招材料\每日总结\MySQL面试导图.png)

## 数据库概念

1. 关系型数据库：MySQL、Oracle、SQL server等

   - 采用二维表格存储数据。数据和数据之间，和字段之间有关联，数据高度一致。

   - 具有**`ACID`特性：`Atomic`原子性，`Consistency`一致性，`Isolation`隔离性，`Durability`持久性**。

     （*事务、以及ACID特性的详细解释待补充*）

   - 优点：易于理解，使用方便，易于维护。

   - 缺点:海量数据查询效率较低；高并发读写下，受到硬件输入输出的限制。

2. 非关系型数据库：Redis、MongoDB等

   - 数据存储格式可以是键值对、文档、图片等，结构不固定。

   - 优点：无需经过SQL解析，读写性能高；基于键值对，易于扩展

   - 缺点：不提供SQL支持，学习成本高；无事务处理。

3. 数据库构成

   - 表：字段 (列)、记录（行）
   - 主键：primary key，唯一标识每条记录，可定义一列或多列，不能有重复或空值

## 操作数据库和数据表

1. 创建数据库

   ```mysql
   CREATE DATABASE test_db;
   ```
   
2. 选定某个数据库

   ```mysql
   USE test_db  # 选定之后才能进行增删改查操作
   ```
   
3. 创建数据表

   ```mysql
   mysql> CREATE TABLE FRUITS(  # 注意每句之后的逗号和最后的分号
       -> f_id char(10) NOT NULL,
       -> s_id INT NOT NULL,
       -> f_name char(255) NOT NULL,
       -> f_price decimal(8,2) NOT NULL,
       -> PRIMARY KEY(f_id)
       -> );
   ```

4. 插入数据

   ```mysql
   mysql> INSERT INTO fruits (f_id, s_id, f_name, f_price)
       -> VALUES ('a1', 101, 'apple', 5.2);
   ```

   ## 查询数据

- 单表查询

  - 查询所有字段

    ```mysql
    # 用通配符查询所有列
    mysql> SELECT * from fruits;
    # 用字段名查询指定的列
    mysql> SELECT f_name, s_id FROM fruits;
    ```

  - 按某种条件查询 （WHERE的关键字）

    ```mysql
        # 可以使用比较符号 = != < <=，查某个区间用BETWEEN AND
    	> SELECT f_name, f_price
        -> FROM fruits
        -> WHERE f_price BETWEEN 2.0 AND 10.0;  # BETWEEN AND 可以用NOT修饰
        
        # 可以使用IN查询指定范围内的记录
    	> SELECT *
        -> FROM fruits
        -> WHERE s_id IN (101, 102) # IN 括号内的条件满足一个即可, 也可以用NOT IN
        -> ORDER BY f_price;
        
        # 可以使用like % _ 来匹配，某种字母模式。
    	> SELECT * FROM fruits
        -> WHERE f_name LIKE 'b%y'; # %匹配多个字符, _ 匹配一个字符。
        
        # 查询空值
    	> SELECT c_id, c_name, c_email FROM customers
        -> WHERE c_email is NULL;
        
        # AND OR 多条件查询，and 优先级高于OR
    	> SELECT f_name, f_price FROM fruits
        -> WHERE s_id = '101' AND f_price >= 5 AND f_name = 'apple';
        
        # 使查询结果去重。DISTINCT
    	> SELECT DISTINCT s_id FROM fruits
    ```

  - 对查询结果进行排序

    ```mysql
    mysql> SELECT s_id FROM fruits
        -> ORDER BY s_id;  # 默认升序
    mysql> SELECT s_id FROM fruits
        -> ORDER BY s_id DESC; # 降序
        
    mysql> SELECT f_name, f_id FROM fruits
        -> ORDER BY f_name, f_id; # 多列排序的时候，第一列值相同时，才会按照第二列的要求排序。
    ```

  - 聚集函数（不返回实际数据，而是对数据进行某种总结）

    ```mysql
    # COUNT(*) 计算总的行数；COUNT(字段) 计算指定列下总行数，将忽略空值。
    	# 查询一共有多少个客户
    	> SELECT COUNT(*) AS cusr_nums FROM customers;
    	# 统计不同订单号中订购的水果种类
    	SELECT o_num, COUNT(f_id) FROM orderitems GROUP BY o_num
    # 还有MAX MIN AVG SUM函数 不举例了
    # 聚合函数一般伴随分组功能来使用
    ```

  - 分组查询

    ```mysql
    # 创建分组
    	# 统计每个s_id 各有几行
    	> SELECT s_id, COUNT(*) AS Total FROM fruits GROUP BY s_id；
    	# GROUP_CONCAT 也是聚合函数，可以将某个分组下的具体字段显示出来
    	> SELECT s_id, GROUP_CONCAT(f_name) AS Names FROM fruits GROUP BY s_id; # 把每个s_id各自对应的水果数显示出来
    # 用HAVING进行过滤，只显示符合条件的分组
    	# 把s_id根据f_name进行分组，并且把f_name多于2的显示出来。
    	> SELECT s_id, GROUP_CONCAT(f_name) FROM fruits GROUP BY s_id HAVING COUNT(*)>2;
    # HAVING 和 WHERE 的区别是：WHERE在分组之前用来过滤记录，HAVING在分组之后选择记录。WHERE排除的记录不再出现在分组中。
    	
    ```

    

- 连接查询 两个或多个表中存放相同意义的字段时，进行连接查询

  - 连接的意义 将一个表的主键 存放到另一个表 作为另一个表的外键 增强可伸缩性
  - 内连接查询：利用比较运算符对表之间某几列数据进行比较，列出与连接条件匹配的数据行 基于相等匹配。
  
  ```mysql
  # 两个表都有s_id,查找两个表里面都有的s_id 对应的一些内容
  # 这是普通的查询语句
  mysql> SELECT fruits.s_id, s_name, f_name, f_price
      -> FROM fruits, suppliers 
      -> WHERE fruits.s_id = suppliers.s_id;
  #这是内连接的语句 限定条件用ON  基于相等测试
  mysql> SELECT fruits.s_id s_name, f_name, f_price
      -> FROM fruits INNER JOIN suppliers
      -> ON fruits.s_id = suppliers.s_id;
  # 自连接 把自己跟自己连成一个表 用别名区分
  ```
  
  - 外连接查询 不光查找符合连接条件的 还会显示出某些一个表有一个表没有的
  
    左连接 左表为主表，所有行都会显示 不匹配的行显示空值；右连接同理。
  
  ```mysql
  # 想找左边表有但是右边表没有的
  mysql> SELECT customers.c_id, orders.o_num
      -> FROM customers LEFT OUTER JOIN orders
      -> ON customers.c_id = orders.c_id;
  ```
  
  - 内连接（inner join）：取出两张表中匹配到的数据，匹配不到的不保留
  - 外连接（outer join）：取出连接表中匹配到的数据，匹配不到的也会保留，其值为NULL
  
- 子查询 一个查询嵌套在另一个查询里面 先执行子查询 再以子查询的结果作为外部查询的范围

  ANY SOME ALL IN EXISTS 关键字

  ```mysql
  # ANY 表示只要num1中符合 这个数大于 num2中随便一个数 （num2中存在比num1小的就行）
  SELECT num1 FROM tbl1 WHERE num1 > ANY (SELECT num2 FROM tbl2);
  # ALL 表示num1中符合 这个数大于 num2中全部数 
  SELECT num1 FROM tbl1 WHERE num1 > ALL (SELECT num2 FROM tbl2);
  # EXISTS 只要是后面的子查询为TRUE 就执行父查询；也可以用NOT EXISTS
  # EXISTS 只取决于是否返回行 不取决于行的内容 所以子查询返回啥内容都行
  SELECT * FROM fruits
  WHERE f_price > 10.7 
  AND EXISTS (SELECT * FROM suppliers WHERE s_id=107);
  # IN 返回给外层一个数据列 以供比较
  SELECT s_id, f_name FROM fruits
  WHERE s_id IN 
  (SELECT s1.s_id FROM suppliers AS s1 WHERE s1.s_city='Tianjin');
  ```

- 合并查询结果 UNION / UNION ALL 将多条查询结果合并成一个表，他们的列数和数据类型必须一样。

  ```mysql
  # 全连接UNION 将两条SELECT语句返回的结果拼成一个表 并且可以去掉重复行，返回结果所有行都是唯一的；如果不想去掉重复行，用UNION ALL
  SELECT * FROM fruits WHERE f_price < 9;
  UNION ALL
  SELECT * FROM fruits WHERE s_id IN (101,103);
  ```

  

# LC题目

## LC176 第二高的薪水

- 思路 先排序 去重 （DISTINCT） 跳过第一个找第二个（limit m,n 跳过前m个，读取前n个）

  如果是空值就返回NULL ifNULL(a,b) a是NULL就返回b，a不是NULL就返回a。

```mysql
SELECT ifNULL(
DISTINCT(salary) FROM Employee ORDER BY salary DESC limit 1,1 
, NULL)
```

## LC197 上升的温度

DATEDIFF（a，b）是对两个日期格式的数据，求出a日期和b日期的差值。

