# LeetCode题解——哈希表

### LC242 有效的字母异位词

```python
class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        dic1, dic2 = {},{}
        for c in s:
            dic1[c] = dic1.get(c, 0) + 1
        for c in t:
            dic2[c] = dic2.get(c, 0) + 1
        return dic1 == dic2  # 字典可以直接比较
```

### LC202 快乐数

编写一个算法来判断一个数 n 是不是快乐数。

对于一个正整数，每一次将该数替换为它每个位置上的数字的平方和。
然后重复这个过程直到这个数变为 1，也可能是 无限循环 但始终变不到 1。
如果 可以变为  1，那么这个数就是快乐数。
如果 n 是快乐数就返回 true ；不是，则返回 false 。

```python
class Solution:
	def ishappy(self, n):
        # 用一个set存储每次的平方和 一旦出现重复就返回False 出现1就返回true
        sumDigit = set()
        while 1:
            sumn = self.getSum(n)
            if sumn == 1:
                return True
            elif sumn in sumDigit:
                return False
            else:
                # 非0非1就把 当前平方数加到set里，把平方和赋值给n
                sumDigit.add(sumn)
                n = sumn
        # 求各个位的平方和
        def getSum(self, n):
            sumn = 0
            while n > 0:
                # %10取出来进行运算
                sumn += (n % 10) ** 2
                # 运算完 降位数
                n /= 10
            return sumn
```

### LC1 两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 target  的那 两个 整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

```python
class Solution:
    def twoSum(self, nums):
        # 遍历一遍数组，把元素和下标存入字典
        # 再遍历一遍数组，寻找targrt-nums[i] 是否在字典中出现
        dic = {}
        for idx, num in enumerate(nums):
            dic[num] = idx
        for idx,num in enumerate(nums):
            # 寻找差值是否在字典中出现
            j = dic.get(target - num)  # 字典get方法 不存在返回None 存在返回键值 这里的键值是下标
            if j is not None and idx != j: # 不能是自己
                return [idx, j]
```

### LC15 三数之和

给你一个包含 n 个整数的数组 nums，判断 nums 中是否存在三个元素 a，b，c ，使得 a + b + c = 0 ？请你找出所有和为 0 且不重复的三元组。

```python
class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        # 回溯可解 但是LC的题目会超时
        nums = sorted(nums)
        if len(nums) < 3: return []

        result = []
        path = []
        used = [0] * len(nums)
        def backtrack(nums, startIdx):
            if len(path) == 3:
                if sum(path) == 0:
                    result.append(path[:])
                return
            
            for i in range(startIdx, len(nums)):
                if i >= 1 and nums[i] == nums[i-1] and used[i-1] == 0:
                    continue
                path.append(nums[i])
                used[i] = 1
                backtrack(nums, i+1)
                path.pop()
                used[i] = 0
        backtrack(nums, 0)
        return result
```

贴一个不太好想的双指针法 把三重循环降为一重循环 关键在去重操作 

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

### LC454 四数相加2 

给定四个包含整数的数组列表 A , B , C , D ,计算有多少个元组 `(i, j, k, l)` ，使得 `A[i] + B[j] + C[k] + D[l] = 0`。

```python
class Solution(object):
    def fourSumCount(self, nums1, nums2, nums3, nums4):
        # 这题可以用哈希来做
        # 用字典存a+b的出现次数，遍历后两个，查找-c-d是否出现在字典中，出现就把相应的次数加上
        dic = {}
        for a in nums1:
            for b in nums2:  # 字典的键是两数之和 值是出现了多少次
                dic[a+b] = dic.get(a+b) + 1
        cnt = 0
        for c in nums3:
            for d in nums4:  # 这边的－两数之和在那边出现了多少次都加进去
                if -c-d in dic.keys():
                    cnt += dic[-c-d]
        return cnt
```

### LC1365 [有多少小于当前数字的数字](https://leetcode-cn.com/problems/how-many-numbers-are-smaller-than-the-current-number/)

给你一个数组 nums，对于其中每个元素 nums[i]，请你统计数组中比它小的所有数字的数目。

换而言之，对于每个 nums[i] 你必须计算出有效的 j 的数量，其中 j 满足 j != i 且 nums[j] < nums[i] 。

以数组形式返回答案。

```python
class Solution:
    def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
        # 用nlogn的方法来做 首先将数组排序 排序后的下标就是有几个数比他小
        # 存入字典 字典内键是数值 值是下标
        # 遍历数组，对每个数在字典内查找，返回下标即可
        # 考虑有重复数字的情况 排序之后相同的数堆在一起 下标应该是最前面的那个
        # 所以应该从后往前遍历 存入字典 这样能保证重复的数 记录最前面的那个的下标
        numsSort = sorted(nums)
        dic = {}
        for i in range(len(numsSort)-1,-1,-1):
            dic[numsSort[i]] = i
        res = []
        for num in nums:
            res.append(dic[num])
        return res
```

