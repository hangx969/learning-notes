## 链表

### LC203 移除链表元素

```python
# 虚拟头结点方法
class ListNode():
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution():
    def removeElements(self, head: ListNode, val: int):
        # 设置虚拟头结点的目的是避免单独写一段逻辑来处理头结点
        # 虚拟头结点的定义：next是给定的头结点
        dummyHead = ListNode(next=head)
        cur = dummyHead  # 链表一般都要定义一个cur，遍历整个链表。cur从虚拟头结点开始
        # 判断链表终止的条件是当前节点的next不是空
        while cur.next is not None:
            if cur.next.val == val:
                cur.next = cur.next.next
            else:
                cur = cur.next
        # 返回的是虚拟节点的下一个，代表新的头结点。
        return dummyHead.next
```

### LC206 反转链表

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        # 双指针迭代法 pre cur
        pre, cur = None, head
        while cur is not None:
            # 这里是反转的逻辑
            tmp = cur.next
            cur.next = pre
            # 这里是双指针往后走的逻辑 遍历到最后一个节点，cur变成next也就是空，pre移动到尾部节点
            pre = cur
            cur = tmp
        # 遍历到最后，cur出界，pre指向最后的节点，返回pre即可
        return pre
```

### LC24 两两交换链表中的元素

```python
# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution(object):
    def swapPairs(self, head):
        # 直接模拟 画图注明步骤，三步走cur指向2 2指向1 1指向3 用临时变量记录即将不被指向的节点
        # cur设置为虚拟头结点，免得对头结点单独处理
        dummyhead = ListNode(next=head)  # 定义虚拟头节点的时候要写next=head，关键字参数
        cur = dummyhead
        # cur指向的后面俩数要交换 所以他俩不能为空
        while cur.next is not None and cur.next.next is not None:
            tmp = cur.next
            cur.next = cur.next.next

            tmp1 = cur.next.next
            cur.next.next = tmp
            cur.next.next.next = tmp1

            cur = cur.next.next
        return dummyhead.next
```

### LC19 删除链表倒数第n个节点

```python
# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution(object):
    def removeNthFromEnd(self, head, n):
        # 删除倒数第n个节点，只用一趟扫描
        # 双指针，间隔为n，fast走到头，slow的位置就是倒数第n个
        # 先让fast走n步就行了
        # 还是要设置虚拟头结点，避免单独写删除头结点的逻辑
        dummyhead = ListNode(next=head)
        fast, slow = dummyhead, dummyhead
        # 这里让fast先走n步，这样fast走到头，slow就是要删除的前一个结点
        for _ in range(n):
            fast = fast.next
        
        while fast.next is not None:
            fast = fast.next
            slow = slow.next
        slow.next = slow.next.next
        return dummyhead.next
```

### 面试题02.07 链表相交  神奇解法

```python
# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution(object):
    def getIntersectionNode(self, headA, headB):
        """根据快慢法则，走的快的一定会追上走得慢的。
        在这道题里，有的链表短，他走完了就去走另一条链表，我们可以理解为走的快的指针。
        那么，只要其中一个链表走完了，就去走另一条链表的路。如果有交点，他们最终一定会在同一个
        位置相遇"""
        curA = headA
        curB = headB
        while curA != curB:
            curA = curA.next if curA else headB
            curB = curB.next if curB else headA
        return curA
```

### LC142 环形链表

```python
# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, x):
        self.val = x
        self.next = None

class Solution(object):
    def detectCycle(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        # 环形链表还是双指针 fast每次走两格 slow每次走一格 相遇则有环
        # 如果有环，再定义双指针，一个节点从头出发，一个节点从相遇点出发，相遇点就是入环点
        fast, slow = head, head
        while fast and fast.next:
            fast = fast.next.next
            slow = slow.next

            if fast == slow:
                p = head
                q = fast
                while p != q:
                    p = p.next
                    q = q.next
                return q
        return None
```

### LC[234. 回文链表](https://leetcode-cn.com/problems/palindrome-linked-list/)

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def isPalindrome(self, head: ListNode) -> bool:
        # 数组法 把链表搞到数组里 再判断是不是
        cur = head
        nums = []
        while cur is not None:
            nums.append(cur.val)
            cur = cur.next
        return nums == nums[::-1]
```

### LC[143. 重排链表](https://leetcode-cn.com/problems/reorder-list/)

给定一个单链表 L 的头节点 head ，单链表 L 表示为：

 L0 → L1 → … → Ln-1 → Ln 
请将其重新排列后变为：

L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → …

不能只是单纯的改变节点内部的值，而是需要实际的进行节点交换

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
class Solution:
    def reorderList(self, head: ListNode) -> None:
        """
        Do not return anything, modify head in-place instead.
        """
        # 用一个双端队列 一前一后取出来重建链表
        from collections import deque
        queue = deque([])
        cur = head
        # 把除了头结点之外的 放入队列
        # 头结点不放进去 所以放的是curnext 所以要判断curnext
        while cur.next:
            queue.append(cur.next)
            cur = cur.next

        # 一前一后重构链表
        cur = head
        while queue:
            # 把队尾的加进去
            cur.next = queue.pop()
            cur = cur.next
            # 把队首的加进去 加进去之前也要判断一下
            if len(queue):
                cur.next = queue.popleft()
                cur = cur.next
        # 因为循环到最后，最后一个节点后可能还连着和原来的节点 最后要把尾部置空
        cur.next = None
```

