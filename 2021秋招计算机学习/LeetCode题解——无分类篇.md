# LeetCode题解——无分类篇

### LC292 Nim游戏

你和你的朋友，两个人一起玩 Nim 游戏：

桌子上有一堆石头。
你们轮流进行自己的回合，你作为先手。
每一回合，轮到的人拿掉 1 - 3 块石头。
拿掉最后一块石头的人就是获胜者。
假设你们每一步都是最优解。请编写一个函数，来判断你是否可以在给定石头数量为 n 的情况下赢得游戏。如果可以赢，返回 true；否则，返回 false 。

```python
class Solution(object):
    def canWinNim(self, n):
        """
        :type n: int
        :rtype: bool
        """
        """
        面对4的整数倍的人永远无法翻身，你拿N根对手就会拿4-N根，
        保证每回合共减4根，你永远对面4倍数，直到4. 
        相反，如果最开始不是4倍数，你可以拿掉刚好剩下4倍数根，让他永远面对4倍数。
        """
        return not n%4 == 0
```

### [剑指 Offer 58 - II. 左旋转字符串](https://leetcode-cn.com/problems/zuo-xuan-zhuan-zi-fu-chuan-lcof/)

字符串的左旋转操作是把字符串前面的若干个字符转移到字符串的尾部。请定义一个函数实现字符串左旋转操作的功能。比如，输入字符串"abcdefg"和数字2，该函数将返回左旋转两位得到的结果"cdefgab"。

```python
class Solution:
    def reverseLeftWords(self, s: str, n: int) -> str:
		# 翻转前n个 翻转后面的 然后再整体反转
        s = list(s)  # 反转之前得先转成列表再去翻转 
        s[0:n] = reversed(s[0:n])
        s[n:] = reversed(s[n:])
        return ''.join(reversed(s))
```

### LC470 [470. 用 Rand7() 实现 Rand10()](https://leetcode-cn.com/problems/implement-rand10-using-rand7/)

已有方法 `rand7` 可生成 1 到 7 范围内的均匀随机整数，试写一个方法 `rand10` 生成 1 到 10 范围内的均匀随机整数。

```python
# The rand7() API is already defined for you.
# def rand7():
# @return a random integer in the range 1 to 7

class Solution:
    def rand10(self):
        """
        :rtype: int
        """
        # rand10 = rand2 * rand5
        # 用rand7生成小于7的很容易 拒绝几个数 或者 分奇数偶数 就行了
        # 用rand7采样两次，第一次是rand2：拒绝7 生成1-6 奇数概率0.5 偶数概率0.5
        # 第二次是rand5，拒绝6、7即可。
        first = rand7()
        second = rand7()
        # first 是 1-6 分奇数偶数代表rand2
        while first > 6: first = rand7()
        # second 是 1-5 代表rand5
        while second > 5: second = rand7()
        # first是偶数 输出second；first奇数 输出second+5
        return second if first%2==0 else second+5
```

```python
# 由大到小易 由小到大难
# 再举个例子，如果用rand5生成rand7
# 构造 5*(rand5() - 1) + rand5(),
# rand5-1生成0-4，5*(rand5()-1)生成 0 5 10 15 20 ； 再加上1-5，就可以等概率生成1-25
# 再用rand25() 构造rand7()
class Solution:
    def rand7():
        x = 5 * (rand5() - 1) + rand5()
        while x > 7:
            x = 5 * (rand5() - 1) + rand5()
        return x
# 以上的方法有个缺点就是 大部分数都被舍弃掉了 只有小于7的数才能保留
# 我们可以取距离25最近的7的倍数 即21 让x取样范围1-21 然后取模映射到1-7即可
class Solution:
    def rand7():
        x = 5 * (rand5() - 1) + rand5()
        while x > 21:
            x = 5 * (rand5() - 1) + rand5()  # x生成1-21 
        return x%7 + 1  # 按7取模 生成0-6 +1 生成1-7 
    
"""
更通用的，如果用randa生成randb （a<b），思路就是先生成randa**2，再往下拒绝采样，生成randb
x = a * (randa - 1) + randa
while x > 小于a**2 的b的倍数
	x = a * (randa - 1) + randa
return x%b + 1
"""
```

