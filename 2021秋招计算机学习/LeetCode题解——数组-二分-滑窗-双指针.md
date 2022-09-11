# LeetCode题解

## 二分查找

### LC704 二分查找

- 题目：给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target  ，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left = 0
        right = len(nums)-1
        # 在[left,right]区间内查找
        while left <= right: # 定义了左闭右闭区间，这里就要等于，因为有意义
            mid = (left + right) // 2
            if nums[mid] == target:
                return mid
            elif nums[mid] > target:  # 中间值大，目标值在左边，mid已经验证不相等，取mid-1
                right = mid-1
            else:  # 中间值小，目标在右侧，取mid+1
                left = mid+1
        return -1
```

### LC35 搜索插入位置
- 题目：给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。如果目标值不存在于数组中，返回它将会被按顺序插入的位置。

  你可以假设数组中无重复元素。

  示例 1: 输入: [1,3,5,6], 5 输出: 2

  示例 2: 输入: [1,3,5,6], 2 输出: 1

  示例 3: 输入: [1,3,5,6], 7 输出: 4

  示例 4: 输入: [1,3,5,6], 0 输出: 0

```python
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        left = 0
        right = len(nums)-1
        while left <= right:
            middle = int((left+right) / 2)
            if nums[middle] > target:
                right = middle - 1
            elif nums[middle] < target:
                left = middle + 1
            else:
                return middle
        # 二分查找找到最后，如果没找到的话，一定是right在left左边一个格，right=left-1. 此时返回right+1或者left即可。
        return left
```

### LC[34. 在排序数组中查找元素的第一个和最后一个位置](https://leetcode-cn.com/problems/find-first-and-last-position-of-element-in-sorted-array/)

```python
class Solution(object):
    def searchRange(self, nums, target):
        # 用二分查找 找左右边界 讨论四种情况
        # 1 目标小于数组最小 2 元素大于数组最大 
        # 3 元素大小合适但是没出现在数组里  4 目标在数组里 
        # 用两个边界值记录位置 根据边界值的情况讨论以上四种情况
        def findR(nums, target):  # 二分法寻找右边界
        # 二分法核心要义就是 找到最后 left跑到right的右边去了 此时最后状态的left就是右边界
        # 所以要在 更新left的时候 更新右边界
            rborder = -2
            left, right = 0, len(nums)-1
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] > target:  # 偏大了 right往左走
                    right = mid -1
                else:  # nums[mid] <= target 
                # 与二分查找的区别是 不直接返回mid，而是一直找到while循环结束
                    left = mid + 1
                    rborder = left
            return rborder
        
        def findL(nums, target):  # 寻找左边界
            lborder = -2
            left, right = 0, len(nums)-1
            while left <= right:
                mid = (left+right) // 2
                if nums[mid] < target:
                    left = mid + 1
                else:  # nums[mid] >= tar 需要更新right 同时更新左边界
                    right = mid - 1
                    lborder = right
            return lborder
        
        # 写主函数
        lborder = findL(nums, target)
        rborder = findR(nums, target)
        # 1 2 两种情况 左右边界有一个不会更新
        if lborder == -2 or rborder == -2: return [-1, -1]
        # 3 二者相差肯定等于1（中间没有数了）
        if rborder - lborder == 1 : return [-1, -1]
        # 4 二者相差肯定大于1（中间肯定隔着数）
        if rborder - lborder > 1: return [lborder+1, rborder-1]
        # 最后回想为啥要给边界赋初值-2而不是-1，就是因为如果查找的元素刚好在第一个位置，lborder会变成-1
```



## 双指针

### LC27 移除数组元素

给你一个数组 nums 和一个值 val，你需要 原地 移除所有数值等于 val 的元素，并返回移除后数组的新长度。

不要使用额外的数组空间，你必须仅使用 O(1) 额外空间并 原地 修改输入数组。

元素的顺序可以改变。你不需要考虑数组中超出新长度后面的元素。

```python
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        # 双指针法
        # 然后从题目的「要求/保留逻辑」出发，来决定当遍历到任意元素 x 时，应该做何种决策：
		# 如果当前元素 num 与移除元素 val 相同，那么跳过该元素。
		# 如果当前元素 num 与移除元素 val 不同，那么我们将其放到下标 idx 的位置，并让 idx 自增右移。
		# 最终得到的 idx 即是答案。
        idx = 0
        for num in nums:
            if num != val:
                nums[idx] = num
                idx += 1
        return idx
```

### LC26 [删除有序数组中的重复项](https://leetcode-cn.com/problems/remove-duplicates-from-sorted-array/)

给你一个有序数组 nums ，请你 原地 删除重复出现的元素，使每个元素 只出现一次 ，返回删除后数组的新长度。

不要使用额外的数组空间，你必须在 原地 修改输入数组 并在使用 O(1) 额外空间的条件下完成。

```python
# 数组删除操作挺有意思的，只要没出现要删的元素，就一直是慢指针自己赋值给自己。出现要删的元素了，慢指针就不动了，下一次赋值就覆盖了
i = 0
for j in range(len(nums)-1):
    if nums[j] != nums[j+1]:
        i += 1
        nums[i] = nums[j+1]
    return i+1

# 如果是删除重复，只保留k个，删除逻辑就是
# 1、如果 idx<k 肯定都保留
# 2、如果这个数与前面第k项不相同，就保留； 言外之意跟前面第k个相等就跳过，等下一次赋值把他覆盖
def solve(k):
    idx = 0
    for n in nums:
        if idx < k or nums[u-k] != n:
            nums[idx] = n
            idx += 1
    return idx
return solve(2)
```

### LC844 比较退格的字符串

用栈来实现比较方便，自己写的，详见LC

```python
class Solution:
    def backspaceCompare(self, s: str, t: str) -> bool:
        # 用一个栈保存字符
        # 遇到字母就入栈，遇到#就从栈里弹出，栈为空时跳过
        def calString(text):
            stack = []
            for c in text:
                if c != '#':
                    stack.append(c)
                else:
                    if len(stack) == 0:
                        continue
                    else:
                        stack.pop()
            return stack
        return calString(s) == calString(t)
    
```

### LC11 盛水最多的容器

```python
class Solution(object):
    def maxArea(self, height):
        """
        :type height: List[int]
        :rtype: int
        """
        # 双指针 左右指针分别在两头 每次计算面积，更新最大面积
        # 移动逻辑是 两个指针 高度小的那个移动，才能保证下一次的面积比这次的大
        left, right = 0, len(height) - 1
        area = 0
        maxarea = 0
        while left < right:
            area = min(height[left], height[right]) * (right - left)
            maxarea = max(maxarea, area)
            if height[left] <= height[right]:
                left += 1
            else:
                right -= 1
        return maxarea
```

### LC15 三数之和

```python
class Solution(object):
    def threeSum(self, nums):
        """
        :type nums: List[int]
        :rtype: List[List[int]]
        """
        # 三指针！先对数组排序。i从头出发，left从i+1出发，right从尽头往回。（i每走一格，重新生成leftright）
        # 看他们三个的和，和要是大于0，说明大的太大了，right--；小于0，说明小的太小了，left++
        # 和如果==0，就输出。
        # 题目规定不能重复，所以中间要加入去重的操作（i和i+1数值相等了，i就++；left right也一样）
        # 去重的位置有讲究
        n = len(nums)
        nums = sorted(nums)
        ans = []
        for i in range(n):
            left = i+1
            right = n-1
            if nums[i] > 0:  # 最小的都大于0 直接返回结果
                break
            if i >= 1 and nums[i] == nums[i-1]:  # i的去重
                continue
            
            while left < right:
                sum = nums[i] + nums[left] + nums[right]
                if sum > 0:
                    right -= 1
                elif sum < 0:
                    left += 1
                else:  # 等于0的情况，先输出，再去重
                    ans.append([nums[i], nums[left], nums[right]])
                    # 把答案输出完了之后，看一下left后面的是不是跟已经输出的相等，是就往后走一个
                    while left != right and nums[left]==nums[left+1]: left += 1
                    while left != right and nums[right]==nums[right-1]: right-=1
                    left += 1
                    right -= 1
        return ans
```

### LC[941. 有效的山脉数组](https://leetcode-cn.com/problems/valid-mountain-array/)

给定一个整数数组 `arr`，如果它是有效的山脉数组就返回 `true`，否则返回 `false`。

```python
class Solution:
    def validMountainArray(self, arr: List[int]) -> bool:
        # 双指针 从两头出发 左边指针往右 往高处走；右边指针往左 往高处走
        # 最后两个指针如果不在首尾处相遇，就是山脉
        n = len(arr)
        if n < 3: return False

        left, right = 0, n-1
        # 指针移动过程
        while left < n-1 and arr[left] < arr[left+1]: left += 1
        while right > 0 and arr[right] < arr[right-1]: right -= 1
        # 移动完进行判断
        if left == right and left != 0 and right != n-1: return True
        return False
```

### LC[283. 移动零](https://leetcode-cn.com/problems/move-zeroes/)

给定一个数组 `nums`，编写一个函数将所有 `0` 移动到数组的末尾，同时保持非零元素的相对顺序。

```python
class Solution(object):
    def moveZeroes(self, nums):
        # 双指针 和前面的数组删除思路一样 先把前面的0都删了 后后面补上0
        # fast遍历数组 所有不是0的元素都从头开始挨着放到一起 由slow控制 每放一个slow往后走一个
        slow = 0
        for fast in range(len(nums)):
            if nums[fast] != 0:
                nums[slow] = nums[fast]
                slow += 1
        for i in range(slow, len(nums)):
            nums[i] = 0
        return nums
```



## 滑动窗口

### LC209 长度最小的子数组

```python
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        # 维护滑动窗口和 sum minlen
        add = 0
        minlen = len(nums) + 1
        # 这里的终止条件要加上数组的和小于tar的情况，这种情况minlen不会更新。
        if len(nums) == 0: return 0
        if sum(nums) < target: return 0
        
        start = 0
        for end in range(len(nums)):
            # 这里把数字加进去
            add += nums[end]
            # start往前走 窗口收缩的逻辑就是大于，只要大于就记录最小值，不断调整。
            while add >= target:
                minlen = min(minlen, end-start+1)
                add -= nums[start]
                start += 1
        return minlen
```

### LC904 水果成篮

求只包含两种元素的最长子数组的长度，滑动窗口+字典

```python
class Solution:
    def totalFruit(self, fruits: List[int]) -> int:
        # 只包含两个数字的最长子串的长度
        # 滑动窗口 字典匹配
        dic = {}
        maxLen = 0
        start = 0
        for end in range(len(fruits)):
            # 不断保存end遇到的新数字到字典中
            tail = fruits[end]
            dic[tail] = dic.get(tail, 0) + 1
            # 水果种类小于等于2，符合要求，更新最大长度
            if len(dic) <= 2:
                maxLen = max(maxLen, end-start+1)
            # 水果种类大于2，不断调整start位置直到满足要求
            while len(dic) > 2:
                head = fruits[start]
                dic[head] -= 1
                if dic[head] == 0:
                    del dic[head]
                start += 1
        return maxLen
```

## 数组其他

### 1 二维查找：

给定一个二维数组，其每一行从左到右递增排序，从上到下也是递增排序。给定一个数，判断这个数是否在该二维数组中。

```python
class Solution:
	def find(self, array, target):
        # 利用从左到右从上到下递增的特性 从矩阵右上角开始找 一层一层往左下缩小范围 
        m, n = len(array), len(array[0])
        if m == 0: return False
        row, col = 0, n-1
        while 0<= row <= m-1 and 0 <=  col <= n-1:
            if array[row][col] > target:  # 大于target，得往小里找 左
                col -= 1
            elif array[row][col] < target:  # 小于target，得往大里找 下
                row += 1
            else:
                return True
        return False
```

### LC[189. 旋转数组](https://leetcode-cn.com/problems/rotate-array/)

给定一个数组，将数组中的元素向右移动 `k` 个位置，其中 `k` 是非负数。

```python
class Solution(object):
    def rotate(self, nums, k):
        # 这里是右旋转 先整体后局部；之前出现过左旋转，是先局部后整体
        # 先整体反转 再局部翻转
        # 注意想到k>len时，其实就是移动k%len
        n = k % len(nums)
        def reverseNum(arr):
            i, j = 0, len(arr)-1
            while i < j:
                arr[i], arr[j] = arr[j], arr[i]
                i += 1
                j -= 1
            return arr
        nums = reverseNum(nums)
        nums[0:n] = reverseNum(nums[0:n])
        nums[n:] = reverseNum(nums[n:])
        return nums
```

### LC[724. 寻找数组的中心下标](https://leetcode-cn.com/problems/find-pivot-index/)

```python
class Solution(object):
    def pivotIndex(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        # 先求出总和再遍历一次求出左右和 比较 
        sumt = sum(nums)
        suml, sumr = 0, 0
        for idx, num in enumerate(nums):
            suml += num 
            sumr = sumt - suml
            # 注意左右侧的和都不能包括中心下标自己，所以左侧的和要减去num
            if suml - num == sumr:
                return idx
        return -1
```

### LC[905. 按奇偶排序数组](https://leetcode-cn.com/problems/sort-array-by-parity/)

给定一个非负整数数组 `A`，返回一个数组，在该数组中， `A` 的所有偶数元素之后跟着所有奇数元素。

```python
class Solution:  # lambda函数和列表推导式 yyds
	def sortArrayByParity(self, nums: List[int]) -> List[int]:
        # 排序的lambda函数 数组中每一个数都进行一次该运算 按照运算结果的由大到小来排序
		return sorted(nums, key=lambda x: x % 2)
    	# return ([x for x in nums if x%2 == 0] + [x for x in nums if x%2 != 0])
```



### LC[922. 按奇偶排序数组 II](https://leetcode-cn.com/problems/sort-array-by-parity-ii/)

给定一个非负整数数组 A， A 中一半整数是奇数，一半整数是偶数。

对数组进行排序，以便当 A[i] 为奇数时，i 也是奇数；当 A[i] 为偶数时， i 也是偶数。

你可以返回任何满足上述条件的数组作为答案。

```python
# 方法1就是拆数组再组合
class Solution(object):
    def sortArrayByParityII(self, nums):
        evenNums = []
        oddNums = []
        for num in nums:
            if num % 2 == 0:
                evenNums.append(num)
            else:
                oddNums.append(num)
        for i in range(0, len(nums)):
            if i % 2 == 0:
                nums[i] = evenNums.pop()
            else:
                nums[i] = oddNums.pop()
        return nums
```

```python
# 方法2 原地修改数组
class Solution(object):
    def sortArrayByParityII(self, nums):
        oddIdx = 1
        for i in range(0, len(nums), 2):
            # 在偶数下标遇见一个奇数元素
            if nums[i] % 2 != 0:
                # 找一个奇数下标的偶数元素
                while nums[oddIdx] % 2 != 0:
                    oddIdx += 2
                nums[i], nums[oddIdx] = nums[oddIdx], nums[i]
        return nums
```

