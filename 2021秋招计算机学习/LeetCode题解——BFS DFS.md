# LeetCode题解——BFS DFS

### LC[200. 岛屿数量](https://leetcode-cn.com/problems/number-of-islands/)

给你一个由 '1'（陆地）和 '0'（水）组成的的二维网格，请你计算网格中岛屿的数量。

岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。

此外，你可以假设该网格的四条边均被水包围。

```python
class Solution(object):
    def numIslands(self, grid):
        """
        :type grid: List[List[str]]
        :rtype: int
        """
        def bfs(grid, r, c):
            from collections import deque
            queue = deque([])
            queue.append([r, c])
            while queue:
                r, c = queue.popleft()
                # 排除边界和访问过的
                if not (0<=r<len(grid) and 0<=c<len(grid[0])): continue
                if grid[r][c] == 'x': continue
                # 符合条件的 标记为已经访问
                grid[r][c] = 'x'
                for x, y in ([r+1,c],[r-1,c],[r,c+1],[r,c-1]):
                    queue.append([x,y])
                    
            # 从网格里的陆地开始遍历，遍历一遍就把连着的变成x，统一算作一个岛屿
            cnt = 0
            for i in range(len(grid)):
                for j in range(len(grid[0])):
                    if grid[i][j] == '1':
                        bfs(grid, i, j)
                        cnt += 1
            return cnt
```

### LC[695. 岛屿的最大面积](https://leetcode-cn.com/problems/max-area-of-island/)

给你一个大小为 m x n 的二进制矩阵 grid 。

岛屿 是由一些相邻的 1 (代表土地) 构成的组合，这里的「相邻」要求两个 1 必须在 水平或者竖直的四个方向上 相邻。你可以假设 grid 的四个边缘都被 0（代表水）包围着。

岛屿的面积是岛上值为 1 的单元格的数目。

计算并返回 grid 中最大的岛屿面积。如果没有岛屿，则返回面积为 0 。

```python
class Solution:
    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
        # DFS 从岛屿出发 将每个节点压栈 遇到返回条件开始弹出 计算面积
        def dfs(grid, r, c):
            area = 0
            # 设置返回条件
            if not (0<= r < len(grid) and 0<= c < len(grid[0])):
                return 0
            if grid[r][c] == 2:
                return 0
            # 标记
            grid[r][c] = 2
            # 递归寻找连着的陆地 统计进这块岛屿
            area += 1 + dfs(grid,r+1,c) + dfs(grid,r-1,c) + dfs(grid,r,c+1) + dfs(grid,r,c-1)
            return area
        
        area = 0
		for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 1:
                    area = max(area, dfs(grid, i, j))
        return area
```

### [剑指 Offer 13. 机器人的运动范围](https://leetcode-cn.com/problems/ji-qi-ren-de-yun-dong-fan-wei-lcof/)

地上有一个m行n列的方格，从坐标 [0,0] 到坐标 [m-1,n-1] 。一个机器人从坐标 [0, 0] 的格子开始移动，它每次可以向左、右、上、下移动一格（不能移动到方格外），也不能进入行坐标和列坐标的数位之和大于k的格子。例如，当k为18时，机器人能够进入方格 [35, 37] ，因为3+5+3+7=18。但它不能进入方格 [35, 38]，因为3+5+3+8=19。请问该机器人能够到达多少个格子？

```python
class Solution:
    def movingCount(self, m: int, n: int, k: int) -> int:
		def getSum(x):
            ans = 0
            while x > 0:
                ans += x%10
                x //= 10
            return ans
        
        visited = [[0]*n for _ in range(m)]
        def dfs(m, n, k, x, y, visited):
            
            # 设置返回条件
            if not (0<= x <m and 0<= y <n):
                return 0
            if visited[x][y] == 1:
                return 0
            # 数位之和大于k了也要标记为已经访问
            if getSum(x) + getSum(y) > k:
                visited[x][y] = 1
                return 0
            
            # 能访问就标记为已访问
            visited[x][y] = 1
            # 递归寻找其他点
            return 1 + dfs(m,n,k,x+1,y,visited) + dfs(m,n,k,x-1,y,visited) + dfs(m,n,k,x,y+1,visited) + dfs(m,n,k,x,y-1,visited)
        
        # 直接从起点00开始，一遍深搜就能计算出结果
        return dfs(m,n,k,0,0,visited)
```

### LC[417. 太平洋大西洋水流问题](https://leetcode-cn.com/problems/pacific-atlantic-water-flow/)

给定一个 m x n 的非负整数矩阵来表示一片大陆上各个单元格的高度。“太平洋”处于大陆的左边界和上边界，而“大西洋”处于大陆的右边界和下边界。

规定水流只能按照上、下、左、右四个方向流动，且只能从高到低或者在同等高度上流动。

请找出那些水流既可以流动到“太平洋”，又能流动到“大西洋”的陆地单元的坐标。

```python
class Solution:
    def pacificAtlantic(self, heights: List[List[int]]) -> List[List[int]]:
        # 从内部的点出发遍历，计算量大会超时
        # 从太平洋边界出发，BFS遍历一遍，访问过的点，在stream数组上+1
        # 从大西洋边界出发，BFS遍历一遍，访问过的点，在stream数组上+1
        # 最后找到2的点就是坐标
        from collections import deque
        m, n = len(heights), len(heights[0])
        # 标记数组，0未被访问，1访问过
        visited = [[0] * n for _ in range(m)]
        stream = [[0] * n for _ in range(m)]
        
        def bfs(heights, x, y, visited):
            queue = deque([])
            queue.append([x, y])
            while queue:
                x, y = queue.popleft()

                if not(0<= x < len(heights) and 0<= y < len(heights[0])):
                    continue
                if visited[x][y] == 1:
                    continue
                
                # 到这里说明没问题
                visited[x][y] = 1
                stream[x][y] += 1

                for newx, newy in ([x+1, y],[x-1,y],[x,y+1],[x,y-1]):
                    # 后面要对比每个点的高度所以这里也要检查合法 否则数组会越界
                    if not (0<= newx < len(heights) and 0<= newy < len(heights[0])):
                        continue
                    if visited[newx][newy] == 1:
                        continue
                    # 逆流而上,高度大于等于的才加入队列，得把高度小的剔除掉
                    if heights[newx][newy] < heights[x][y]:
                        continue
                    queue.append([newx, newy])

        # 从太平洋边界出发遍历一遍
        for i in range(0, m):
            bfs(heights, i, 0, visited)
        for j in range(0, n):
            bfs(heights, 0, j, visited)

        # 重置visited，再从大西洋边界遍历一遍
        visited = [[0] * n for _ in range(m)]
        for i in range(0, m):
            bfs(heights, i, n-1, visited)
        for j in range(0, n):
            bfs(heights, m-1, j, visited)
            
        # 最后遍历一遍 找到数值为2的就是能流过去的
        ans = []
        for i in range(m):
            for j in range(n):
                if stream[i][j] == 2:
                    ans.append([i, j])
        return ans
```

### LC[547. 省份数量](https://leetcode-cn.com/problems/number-of-provinces/)

有 n 个城市，其中一些彼此相连，另一些没有相连。如果城市 a 与城市 b 直接相连，且城市 b 与城市 c 直接相连，那么城市 a 与城市 c 间接相连。省份 是一组直接或间接相连的城市，组内不含其他没有相连的城市。

给你一个 n x n 的矩阵 isConnected ，其中 isConnected[i][j] = 1 表示第 i 个城市和第 j 个城市直接相连，而 isConnected[i][j] = 0 表示二者不直接相连。返回矩阵中 省份 的数量。

```python
class Solution:
    def findCircleNum(self, isConnected: List[List[int]]) -> int:
        # bfs 
        # 遍历每个节点 如果该节点未被访问过 标记为访问过 入队 省份数量+1
        # 出队 遍历 与该节点连着 且未访问过 的节点 标记为访问过 入队
        # 都遍历完 返回省份数量

        from collections import deque
        queue = deque([])

        n = len(isConnected)
        visited = [0] * n

        count = 0
        for i in range(n):
            # 未被访问过，省份+1，标记，入队
            if visited[i] == 0:
                count += 1
                visited[i] = 1
                queue.append(i)

            # 队列里放的是与i联通的所有节点
            # 挨个弹出来，从头开始再遍历一遍，找到下一级的联通节点
            while queue:
                j = queue.pop()
                # 弹出一个 就从头开始找与他连着 并且没访问过的 
                for k in range(0, n):
                    if isConnected[j][k] == 1 and visited[k] == 0:
                        # 找到就标记为访问过，并且入队
                        visited[k] = 1
                        queue.append(k)

        return count
```

