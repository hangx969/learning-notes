# LeetCode题解——栈与队列

### LC[925. 长按键入](https://leetcode-cn.com/problems/long-pressed-name/)

你的朋友正在使用键盘输入他的名字 name。偶尔，在键入字符 c 时，按键可能会被长按，而字符可能被输入 1 次或多次。

你将会检查键盘输入的字符 typed。如果它对应的可能是你的朋友的名字（其中一些字符可能被长按），那么就返回 True。

```python
class Solution(object):
    def isLongPressedName(self, name, typed):
        # 用栈来匹配 每次比较栈顶元素 输入表为空或不相等直接返回False 相等则看name下一个词
        name = list(name)
        typed = list(typed)
        while name:
            c = name.pop()
            # typed空了 或者 不空但栈顶元素不匹配
            if len(typed) == 0 or typed.pop() != c:
                return False
            # name如果空了 或者 下一个字母不重复 就把typed里面的弹干净
            if len(name) == 0 or name[-1] != c:
                while typed and typed[-1] == c:
                    typed.pop()
        # 如果弹完了之后typed还剩下了 说明 有错误字母
        return len(typed) == 0
    # 注意 判断列表/栈/队列是否为空，要用 if name 不能用 if is None
    # 假设列表已经空了，用if is None；来判断的话，并不会进循环，[] 和 None不是一回事
```

