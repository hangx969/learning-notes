# 创建指定大小的单个测试文件

```sh
dd if=/dev/zero of=testfile bs=1G count=200
```

# 创建多个指定大小的测试文件

```sh
#!/bin/bash

for i in {1..100}
do
   dd if=/dev/zero of=testfile$i bs=1M count=1
done
```

