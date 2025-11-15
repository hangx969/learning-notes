# 两地三中心架构

![image-20251115095329861](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202511150953992.png)

- A是生产中心。A和B是同城双中心。A的数据会实时同步到B同城灾备中心，专线连接速度会很快。
- B的配置可能和A一样，准备随时接收流量进来。B也可能是双活，接收20%流量。
- C是灾备中心。配置较低，平常闲置。不会接收生产流量进来。
两地三中心是一种主备模式，有一个同城灾备中心和一个异地灾备中心，但是这两个中心大部分情况下不会接受不了生产流量，造成资源浪费。

# 异地多活

![image-20251115095652754](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202511150956881.png)

异地多活

# 智能DNS工作原理

![image-20251115095829129](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202511150958186.png)



# 单集群异地多活架构

![image-20251115095952081](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202511150959153.png)



![image-20251115100112497](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202511151001603.png)
