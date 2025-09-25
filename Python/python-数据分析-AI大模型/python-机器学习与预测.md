# 机器学习

## 简介

机器学习（Machine Learning，简称 ML）是一种让计算机从数据中自动学习并进行预测或决策的技术，目的是让计算机具备一定的“智慧”。它有三种主要类型：

- **监督学习（Supervised Learning）**：在已知标签（结果）的数据上训练模型，让计算机根据输入预测输出。
- **无监督学习（Unsupervised Learning）**：在没有标签的数据上找出数据之间的结构或模式，比如聚类。
- **强化学习（Reinforcement Learning）**：通过与环境的交互，试图获得最大奖励的学习方式。

## 工作流程

1. **数据收集**：首先，我们需要从各个渠道获取数据。数据可能来自互联网、公司数据库、设备传感器等。
2. **数据预处理**：由于现实中的数据可能包含缺失值、重复值等问题，预处理是非常重要的步骤。常见操作包括：
   - 填补缺失值
   - 删除重复数据
   - 标准化（将数据缩放到相同范围）
3. **模型选择**：根据任务的不同，选择不同的机器学习算法，比如回归（预测连续值）或分类（预测离散类别）。
4. **训练模型**：使用训练数据来“教会”计算机模型，从而让模型能够预测。
5. **评估模型**：通过测试数据评估模型的准确性。
6. **模型优化**：根据评估结果调整模型参数或选择新的算法以提高预测效果。

## 常用算法

### 线性回归（Linear Regression）

线性回归是一种用来**预测连续数值的算法**。它通过找出一个最佳的“线性”关系来拟合数据。

### 决策树（Decision Tree）

**决策树是一种监督学习算法**，它通过将数据划分成多个子集，最终生成树状结构，用来做分类或回归预测。每一个节点代表一个特征，每一条分支代表特征的取值，叶子节点代表分类结果或回归结果。决策树通过计算信息增益或基尼指数来选择最佳特征进行划分。

**信息增益**： 信息增益是通过计算划分前后数据的不确定性减少量来选择特征。信息增益越大，表示这个特征的划分效果越好。

## 模型评估

对于回归问题，常用的评估指标有：

- **均方误差（MSE）**：评估预测值与真实值之间的差异。
- **平均绝对误差（MAE）**：衡量预测值与真实值的平均绝对差异。

对于分类问题：

- **准确率**：模型正确预测的样本数与总样本数之比。
- **精确率（Precision）**：预测为正的样本中，真实为正的比例。
- **召回率（Recall）**：真实为正的样本中，预测为正的比例。

**混淆矩阵**： 混淆矩阵展示了分类模型预测结果的详细情况，包含真正例、假正例、真反例和假反例。

## 机器学习常用模块

### scikit-learn模块

scikit-learn 是一个用于机器学习的 Python 库，它为用户提供了很多现成的工具和算法，帮助你进行数据分析、建模、预测和评估等操作。简单来说，scikit-learn 就是一个让机器学习变得更简单的工具包。

scikit-learn做什么：

1. 数据预处理：机器学习通常需要清洗和整理数据，scikit-learn提供了很多方法来处理缺失的值、标准化数据、数据变换等。
2. 训练模型：scikit-learn提供了很多常见的机器学习算法，比如回归分析（预测数值）、分类（判断类别）、聚类（分组相似数据等）。可以用它来训练模型
3. 评估模型：训练完模型后，验证是否表现良好，scikit-learn提供多种评估模型的方法，比如准确率、精确率、召回率等。
4. 模型选择：不同的机器学习任务适合使用不同的算法。sciki-learn提供了多种算法选择。

常用功能：

1. 分类：比如判断邮件是否是垃圾邮件，或者识别图片中的动物（猫狗等）
2. 回归：预测房价、股票价格等连续数值
3. 聚类：把数据分成不同的组
4. 降维：把高维数据压缩到低维空间，方便可视化分析 
5. 评估：评估模型的好坏

### numpy模块

Numpy用于处理和分析数据。全名是Numerical Python，专门进行数字运算、数组操作和矩阵计算等工作。

在Python中，默认的列表可以存储各种数据类型，但并不擅长处理大量数字数据，尤其是进行数学运算时速度较慢。而Numpy提供了高效的数组和矩阵操作。

核心概念：

1. 数组（Array）是Numpy的核心，类似于Python的列表，不同之处在于Numpy数组中的所有元素必须是同种类型的数据（通常是数字），运算速度远远高于Python原生的列表。

# 深度学习

深度学习（Deep Learning）是机器学习的一个分支，基于人工神经网络的模型，通过大量数据的训练，自动从数据中提取特征，实现自我学习。深度学习在图像识别、语音处理、自然语言处理等领域取得了突破性的进展。

**深度学习与传统机器学习的区别**

- **机器学习**：依赖于人工特征提取和选择，模型较为简单。
- **深度学习**：自动从原始数据中提取特征，模型较为复杂，尤其适合处理大规模数据。

**深度学习的核心概念**

- **神经网络**：模拟人脑神经元工作原理的计算模型。最常见的是多层感知机（MLP）。
- **激活函数**：决定神经元是否被激活，常用的激活函数有ReLU、Sigmoid、Tanh等。
- **损失函数**：衡量模型预测值与真实值之间的差距，常用的损失函数有均方误差（MSE）和交叉熵（Cross Entropy）。
- **梯度下降法**：一种优化方法，用来更新神经网络中的权重，使得损失函数最小化。

## 框架

### TensorFlow

TensorFlow是由Google开发的开源深度学习框架，具有高效、灵活的特性。它支持深度神经网络的构建、训练、评估和部署。

- **安装TensorFlow**：pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple tensorflow

**TensorFlow的基本结构**：

- **模型**：由多个层（如Dense层、Conv2D层等）组成。
- **优化器**：例如Adam优化器，用于更新网络权重。
- **损失函数**：如均方误差（MSE）和交叉熵损失。

### PyTorch

PyTorch是由Facebook开发的深度学习框架，以动态图（Dynamic Computation Graph）著称，适合快速实验和研究。

- **安装PyTorch**：pip3 install pytorch 

**PyTorch的基本结构**：

- **模型**：通过继承nn.Module定义网络结构。
- **优化器**：如SGD、Adam等。

**损失函数**：例如CrossEntropyLoss用于分类问题。

## 常用模型

**多层感知机（MLP）**

多层感知机是一种最简单的神经网络模型，通常包含输入层、若干隐藏层和输出层。它可以用来做回归和分类任务。

**卷积神经网络（CNN）**

卷积神经网络（CNN）广泛应用于图像处理领域，通过卷积层提取局部特征，池化层减少计算复杂度。

**循环神经网络（RNN）**

循环神经网络（RNN）适用于处理时序数据，如文本生成、语音识别等。

# AI在运维中的应用场景

**智能监控**

通过AI模型分析系统性能数据（如CPU使用率、内存占用、网络流量等），预测潜在的资源瓶颈，并触发自动化调整策略，保证系统的稳定运行。

**自动化故障排查**

结合机器学习模型对系统日志进行分类和异常检测，快速识别问题根因，减少人工分析的时间和错误率。

**资源使用优化**

基于AI模型对历史数据的学习，自动调度云服务器资源，实现高效分配和稳定运行，提升整体资源利用率。

**日志分析与自动化运维**

运用自然语言处理（NLP）技术对日志数据进行分析，提取关键问题并生成对应的运维脚本，实现问题解决的全流程自动化。

# 项目实战

## 预测linux机器cpu使用率

需求：连接到linux机器，获取CPU使用率，然后使用机器学习模型（线性回归）来预测未来的CPU使用率，并将结果可视化。

~~~sh
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple paramiko psutil scikit-learn numpy matplotlib
~~~

~~~python
import sys
import io
# 将stdout的编码设置为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import paramiko
import psutil
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 连接远程Linux机器的函数
def get_cpu_usage(ip, username, password):
    # 使用 paramiko 库连接到远程 Linux 机器
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(ip, username=username, password=password)

    # 执行命令获取CPU使用率
    stdin, stdout, stderr = ssh_client.exec_command("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'")
    cpu_usage = float(stdout.read().decode('utf-8').strip())

    ssh_client.close()
    return cpu_usage

# 获取一定时间间隔的CPU使用率数据
def collect_cpu_data(ip, username, password, duration=120, interval=6):
    cpu_data = []
    for _ in range(duration // interval):
        cpu_usage = get_cpu_usage(ip, username, password)
        cpu_data.append(cpu_usage)
        time.sleep(interval)
    return cpu_data

# 训练模型预测CPU使用率
def train_model(cpu_data):
    # 创建特征数据集（时间步长，CPU使用率）
    X = np.array(range(len(cpu_data))).reshape(-1, 1)
    # 时间步长，假设cpu_data有十个数据，那range(10)会返回列表[0,1,2,3,...9]
    #X(n,1)的二维数组，n是数据点的数量
    y = np.array(cpu_data)  # CPU使用率，[10%,16%,18%，...88%]

    # 分割训练集和测试集，20%测试，80%训练
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=100)

    # 创建并训练线性回归模型
    model = LinearRegression()
    model.fit(X_train, y_train)

    # 预测并评估模型
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"模型的均方误差 (MSE): {mse:.2f}")

    return model

# 预测未来CPU使用率
def predict_cpu_usage(model, steps=10):
    last_time = model.coef_[0] * (len(cpu_data) - 1) + model.intercept_
    future_steps = np.array(range(len(cpu_data), len(cpu_data) + steps)).reshape(-1, 1)
    predictions = model.predict(future_steps)
    return predictions

# 配置远程Linux机器的连接信息
ip = '192.168.40.183'
username = 'root'
password = 'root'


# 收集数据并训练模型
cpu_data = collect_cpu_data(ip, username, password)
model = train_model(cpu_data)

# 预测未来10个时间步的CPU使用率
future_predictions = predict_cpu_usage(model, steps=10)

# 用实际的时间（秒）作为 X 轴
time_steps = np.arange(0, len(cpu_data) * 5, 5)  # 每个时间步是5秒，所以对应 0, 5, 10, ..., 45
future_time_steps = np.arange(len(cpu_data) * 5, (len(cpu_data) + 10) * 5, 5)  # 预测的时间步

plt.rcParams['font.family'] = ['Microsoft YaHei']  # 使用微软雅黑字体以支持中文显示

# 可视化数据和预测结果
plt.plot(time_steps, cpu_data, label='历史CPU使用率')
plt.plot(future_time_steps, future_predictions, label='预测的CPU使用率', linestyle='--')
plt.xlabel('时间（秒）')
plt.ylabel('CPU使用率 (%)')
plt.legend()
plt.show()
~~~

### 如何让预测更准确

1. 增加数据量：采集更多的历史数据

   ~~~python
   def collect_cpu_data(ip, username, password, duration=300, interval=5):  # 延长采集时间到 300 秒
       cpu_data = []
       for _ in range(duration // interval):
           cpu_usage = get_cpu_usage(ip, username, password)
           cpu_data.append(cpu_usage)
           time.sleep(interval)
   return cpu_data
   ~~~

2. 减少噪声：对采集的数据进行平滑处理（如移动平均嚯指数平滑）

3. 模型选择与优化：

   - 线性回归可能无法捕捉复杂的非线性关系，可以尝试更高级的模型，如：
     - ARIMA：适合时间序列数据
     - LSTM：适合长期依赖的时间序列数据
     - 随机森林回归：适合非线性数据
   - 特征工程：增加更多特征

   ~~~python
   from sklearn.ensemble import RandomForestRegressor
   
   def train_model(cpu_data):
       X = np.array(range(len(cpu_data))).reshape(-1, 1)
       y = np.array(cpu_data)
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   
       # 使用随机森林回归模型
       model = RandomForestRegressor(n_estimators=100, random_state=42)
       model.fit(X_train, y_train)
   
       y_pred = model.predict(X_test)
       mse = mean_squared_error(y_test, y_pred)
       print(f"模型的均方误差 (MSE): {mse:.2f}")
       return model
   ~~~

4. 超参数调优：

   - 调整模型参数：例如随机森林的n_estimators或线性回归的正则化参数
   - 交叉验证：使用交叉验证选择最佳参数

   ~~~python
   from sklearn.model_selection import GridSearchCV
   
   def train_model(cpu_data):
       X = np.array(range(len(cpu_data))).reshape(-1, 1)
       y = np.array(cpu_data)
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   
       # 使用网格搜索调优随机森林参数
       param_grid = {
           'n_estimators': [50, 100, 200],
           'max_depth': [None, 10, 20]
       }
       model = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=5)
       model.fit(X_train, y_train)
   
       print(f"最佳参数: {model.best_params_}")
       y_pred = model.predict(X_test)
       mse = mean_squared_error(y_test, y_pred)
       print(f"模型的均方误差 (MSE): {mse:.2f}")
       return model
   ~~~

5. 时间序列特性

   - 滑动窗口特征：将历史数据作为特征输入模型
   - 差分处理：对数据进行差分以消除趋势和季节性

   ~~~python
   def create_sliding_window_features(cpu_data, window_size=5):
       X = []
       y = []
       for i in range(len(cpu_data) - window_size):
           X.append(cpu_data[i:i + window_size])
           y.append(cpu_data[i + window_size])
       return np.array(X), np.array(y)
   
   def train_model(cpu_data):
       X, y = create_sliding_window_features(cpu_data, window_size=5)
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   
       model = RandomForestRegressor(n_estimators=100, random_state=42)
       model.fit(X_train, y_train)
   
       y_pred = model.predict(X_test)
       mse = mean_squared_error(y_test, y_pred)
       print(f"模型的均方误差 (MSE): {mse:.2f}")
       return model
   ~~~

6. 模型评估与验证

   - 增加评估指标：除了均方误差MSE，还可以使用平均绝对误差MAE或R方分数
   - 验证集：使用验证集评估模型的泛化能力

   ~~~python
   from sklearn.metrics import mean_absolute_error, r2_score
   
   def train_model(cpu_data):
       X = np.array(range(len(cpu_data))).reshape(-1, 1)
       y = np.array(cpu_data)
       X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   
       model = RandomForestRegressor(n_estimators=100, random_state=42)
       model.fit(X_train, y_train)
   
       y_pred = model.predict(X_test)
       mse = mean_squared_error(y_test, y_pred)
       mae = mean_absolute_error(y_test, y_pred)
       r2 = r2_score(y_test, y_pred)
       print(f"模型的均方误差 (MSE): {mse:.2f}")
       print(f"模型的平均绝对误差 (MAE): {mae:.2f}")
       print(f"模型的 R² 分数: {r2:.2f}")
       return model
   ~~~

7. 可视化优化

   - 增加预测区间
   - 动态更新图表

   ~~~python
   def plot_results(time_steps, cpu_data, future_time_steps, future_predictions):
       plt.figure(figsize=(10, 6))
       plt.plot(time_steps, cpu_data, label='历史CPU使用率', marker='o')
       plt.plot(future_time_steps, future_predictions, label='预测的CPU使用率', linestyle='--', marker='x')
       plt.fill_between(future_time_steps, future_predictions - 5, future_predictions + 5, alpha=0.2, label='预测区间')
       plt.xlabel('时间（秒）')
       plt.ylabel('CPU使用率 (%)')
       plt.title('CPU使用率预测')
       plt.legend()
       plt.grid(True)
       plt.show()
   ~~~

## 垃圾邮件分类

假设我们要构建一个垃圾邮件分类器，目标是根据邮件内容的特征（如单词出现频率、字符数等）来预测邮件是否是垃圾邮件。

**问题描述：**

已经有了一组邮件数据，每封邮件都标记为“垃圾邮件”或“非垃圾邮件”。你想通过决策树来分类，决定新邮件是否是垃圾邮件。

数据集：

![image-20250924200709592](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202509242007684.png)

**目标**：使用决策树模型，根据邮件的特征来预测邮件是否为垃圾邮件。

代码实现：

~~~python
from sklearn.tree import DecisionTreeClassifier

# 准备数据
X = [[1, 0], [0, 1], [2, 1], [0, 0], [1, 2]]  # 邮件特征（“免费”和“优惠”出现次数）
y = [1, 0, 1, 0, 1]  # 标签（1表示垃圾邮件，0表示非垃圾邮件）

# 创建决策树分类器
model = DecisionTreeClassifier()

# 训练模型
model.fit(X, y)

# 输出决策树的规则
print("决策树的规则：", model.tree_)

# 使用模型预测新邮件的类别
new_email = [[1, 1]]  # 新邮件的特征（“免费”出现1次，“优惠”出现1次）
prediction = model.predict(new_email)
print("预测结果：", "垃圾邮件" if prediction[0] == 1 else "非垃圾邮件")
~~~

## 开发图片分类模型

需求：训练一个CNN（卷积神经网络）模型来识别CIFAR-10数据集中的图像类别，并且可以对用户提供的自定义图像进行预测。具体步骤如下：

1. **数据加载和预处理**：

   1. 从TensorFlow库中加载CIFAR-10数据集。在CIFAR-10数据集中，这个数据集包含10个不同的图像类别，每个类别都有6000张图像。这10个类是飞机、汽车、鸟、船、狗、青蛙、猫、马、卡车、鹿等。

   2. 对图像进行归一化处理：图像的像素值通常在0到255之间。为了提高模型的训练效果，我们将这些值归一化到0到1之间，具体方法是将像素值除以255。这种处理有助于加快模型收敛速度并提高预测准确性。

   3. One-Hot编码：One-hot编码是一种将类别标签转换为向量的方式。例如，对于类别0（飞机），我们可以用一个长度为10的向量表示：[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]，这表示这是一个飞机的图像。其他类别的编码方式也是类似的。这样做的好处是，模型可以将类别作为数字处理，而不是直接使用标签，这样能更好地理解和学习不同类别之间的关系。

2. **模型构建**：

使用Keras的Sequential模型构建一个CNN，包含多个卷积层（用于提取图像特征）、池化层（用于降低特征维度）和全连接层（用于最终分类）。

3. **模型编译**：

编译模型，指定使用Adam优化器来更新模型权重，并使用分类交叉熵作为损失函数来评估模型预测的准确性。

4. **模型训练**：

在训练数据上训练模型，这意味着用数据来教模型识别不同类别的图像。模型会通过反复学习，逐渐提高自己的预测能力。在训练的过程中，我们还会用一些不见过的数据（测试数据）来测试模型，看它在未见数据上的表现，确保模型能在实际情况中准确分类。

5. **模型保存**：

将训练好的模型保存为名为cifar10_model.h5的文件，以便以后可以直接加载和使用。

6. **结果可视化**：

使用训练好的模型对测试集和自定义图像进行预测，展示预测结果，并通过Matplotlib库绘制图像，以便更直观地比较预测标签和实际标签

代码实现：

mnist_classification.py

~~~python
import sys
import io
# 将stdout的编码设置为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import tensorflow as tf
# 导入TensorFlow库
from tensorflow.keras.models import Sequential
# 导入Sequential模型
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout
# 导入Dense、Flatten、Conv2D、MaxPooling2D、Dropout层
from tensorflow.keras.utils import to_categorical
# 导入to_categorical函数，用于将标签转换为one-hot编码
import numpy as np
# 导入numpy库，用于处理数据
import matplotlib.pyplot as plt
# 导入matplotlib.pyplot库，用于绘制图像
import matplotlib.font_manager as fm  # 用于加载中文字体
# 导入matplotlib.font_manager库，用于加载中文字体
import random  # 用于随机选择图片

"""
导入相关的库：
   - tensorflow：用于构建和训练神经网络。
   - keras：这是 TensorFlow 的高级接口，提供更简便的 API 来定义和训练神经网络模型。
   - numpy：用于处理数据和数组操作。
   - matplotlib：用于绘制图像和显示图片。
   - random：用于随机选择测试集中的一张图片。
"""

# 1. 加载 CIFAR-10 数据集
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

"""
加载 CIFAR-10 数据集：
   CIFAR-10 是一个包含 10 类图像的数据集。每类有 60000 张 32x32 彩色图像。数据集分为训练集和测试集。
   - x_train：训练集图像数据，是训练集中的图像数据，包含 50,000 张 32x32 像素的彩色图像（每张图像有 3 个颜色通道：红色、绿色、蓝色）。
   - y_train：训练集标签数据，形状是 (50000, 1)，是训练集的标签，表示每张图像的类别（0 到 9，代表不同的物体类别）。
   - x_test：测试集图像数据，形状是 (10000, 32, 32, 3)。
   - y_test：测试集标签数据，形状是 (10000, 1)。是测试集的标签，表示每张图像的真实类别（0 到 9，表示不同的物体类别）。
"""

# 2. 数据预处理
x_train, x_test = x_train / 255.0, x_test / 255.0  # 归一化到 0-1 范围
y_train, y_test = to_categorical(y_train), to_categorical(y_test)  # one-hot 编码

"""
 数据预处理：
   - 图像数据归一化：图像的像素值范围从 [0, 255]，我们将其归一化到 [0, 1]。这样做可以加速模型的训练，使其更稳定。
   - one-hot 编码：标签数据是整数型（0-9），代表类别。为了适应神经网络的输出，我们将它们转换为 one-hot 编码形式。
   例如，类别“0”会变成 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]，类别“1”会变成 [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]。
"""

# 3. 构建卷积神经网络模型
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    Flatten(),
    Dense(64, activation='relu'),
    Dropout(0.5),  # 添加 Dropout 层，防止过拟合
    Dense(10, activation='softmax')
])

"""
构建卷积神经网络（CNN）模型：
   - Sequential：表示模型是一个层的线性堆叠。
   - Conv2D：卷积层，用于从图像中提取特征。
     - 第一个卷积层使用 32 个 3x3 的卷积核，输入的图像形状是 (32, 32, 3)。
     - 第二、第三个卷积层使用 64 个 3x3 的卷积核。
   - MaxPooling2D：池化层，用于减少数据的尺寸，从而减少计算量和防止过拟合。我们使用 2x2 的池化窗口。
   - Flatten：将多维的输入一维化，通常用于连接到全连接层。
   - Dense：全连接层。第一个全连接层有 64 个神经元，第二个（输出层）有 10 个神经元，分别对应 10 个类别。
   - Dropout：为了防止过拟合，在全连接层后加入 Dropout 层，丢弃 50% 的神经元。
"""
# 4. 编译模型
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

"""
编译模型：
   - optimizer='adam'：使用 Adam 优化器，它是常用的自适应学习率优化算法。
   - loss='categorical_crossentropy'：选择类别交叉熵损失函数，用于多分类问题。
   - metrics=['accuracy']：在训练和评估过程中我们关注的指标是分类准确率（accuracy）。
"""

# 5. 训练模型
model.fit(x_train, y_train, epochs=10, batch_size=64, validation_data=(x_test, y_test))  # 增加训练轮数，批量大小设置为64

"""
训练模型：
   - x_train 和 y_train：训练数据和标签。
   - epochs=2：训练的轮数（每次使用整个训练集训练一次）。通常需要多个轮次来优化模型，但本例中使用 2 轮以减少计算量。
   - batch_size=10：每次更新模型参数时使用 10 张图片。较大的批量大小可能会提高训练速度，但也需要更多内存。
   - validation_data=(x_test, y_test)：使用测试集进行验证，以便跟踪模型在训练过程中的表现。
"""
# 保存模型
model.save("cifar10_model.h5")


# CIFAR-10 标签名称（中文）
labels = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']

# 6. 设置中文字体
font_path = "C:/Windows/Fonts/simhei.ttf"  # 适用于Windows的字体路径
my_font = fm.FontProperties(fname=font_path)

# 7. 随机选择测试集中的一张图片进行预测
random_index = random.randint(0, len(x_test) - 1)  # 随机选择一个索引
test_image = x_test[random_index]
test_label = np.argmax(y_test[random_index])  # 真实标签

# 使用模型进行预测
prediction = model.predict(np.expand_dims(test_image, axis=0))
predicted_label = np.argmax(prediction)  # 预测结果

# 显示图片和预测结果
plt.imshow(test_image)
plt.title(f"预测: {labels[predicted_label]}, 实际: {labels[test_label]}", fontproperties=my_font)
plt.axis('off')
# 显示图形
plt.show()
"""
随机选择测试集中的一张图片进行预测：
   - random.randint(0, len(x_test) - 1)：生成一个随机整数，作为测试集图片的索引。
   - test_image：获取随机选中的测试图像。
   - test_label：获取该图像的真实标签，使用 `np.argmax` 获取 one-hot 编码的索引值。
   - 使用训练好的模型进行预测，`model.predict` 返回的是一个 10 维的概率分布，我们通过 `np.argmax` 获取最大概率对应的类别。
   - 显示预测结果：使用 Matplotlib 显示图片，并在标题中显示模型的预测类别和真实类别。
"""
~~~

mnist_classification_tkinter.py

~~~python
#通过加载训练好的 CIFAR-10 分类模型，对上传的图片进行分类，并显示预测结果

import tkinter as tk
from tkinter import filedialog, Label, Button, Canvas
from PIL import Image, ImageTk, ImageOps
import numpy as np
import tensorflow as tf
import matplotlib.font_manager as fm

# 加载已训练的模型
model = tf.keras.models.load_model("C:/代码/图片分类大模型开发/cifar10_model.h5")

# CIFAR-10 标签名称（中文）
labels = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']

# 设置字体
font_path = "C:/Windows/Fonts/simhei.ttf"  # 适用于Windows的字体路径
my_font = fm.FontProperties(fname=font_path)

# 创建主窗口
window = tk.Tk()
window.title("CIFAR-10 图像分类器")
window.geometry("700x700")

# 图片显示 Canvas
canvas = Canvas(window, width=500, height=500)
canvas.pack(pady=10)

result_label = Label(window, text="", font=("Arial", 14))
result_label.pack(pady=10)

def preprocess_image(image_path):
    """加载和预处理图像，使其符合模型输入格式"""
    image = Image.open(image_path)
    image = ImageOps.fit(image, (32, 32), Image.LANCZOS)  # 使用 LANCZOS 缩放图像
    image = np.array(image) / 255.0  # 归一化
    return image.reshape((1, 32, 32, 3))  # 添加批次维度

def classify_image():
    """选择图片并进行分类"""
    file_path = filedialog.askopenfilename()
    if file_path:
        # 预处理图像
        img_array = preprocess_image(file_path)
        
        # 使用模型进行预测
        prediction = model.predict(img_array)
        predicted_label = np.argmax(prediction)  # 获取预测类别
        
        # 显示预测结果
        result_label.config(text=f"预测结果: {labels[predicted_label]}", font=my_font)
        
        # 在界面显示选择的图片
        display_image = Image.open(file_path)
        display_image.thumbnail((600, 600))  # 初始缩放图片的最大尺寸
        img = ImageTk.PhotoImage(display_image)
        
        # 清除旧图像并显示新图像
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.image = img  # 需要保存引用

# 上传按钮
upload_btn = Button(window, text="上传图片并预测", command=classify_image)
upload_btn.pack(pady=20)

# 运行主循环
window.mainloop()
~~~

## 异常日志检测

**背景**：运维系统需要对海量日志进行实时分析，快速定位异常。

**解决方案**：

1. 使用Scikit-learn构建分类模型，将日志分为正常和异常两类。
2. 通过特征提取技术（如TF-IDF）提取日志文本中的关键特征。
3. 利用训练好的模型实时检测异常日志，并触发报警。

~~~python
import sys
import io
# 将stdout的编码设置为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os  # 用于操作文件和目录
import pandas as pd  # 用于数据处理和分析
from sklearn.feature_extraction.text import TfidfVectorizer  # 用于文本特征提取，将文本转换为TF-IDF特征
from sklearn.model_selection import train_test_split  # 用于将数据集划分为训练集和测试集
from sklearn.ensemble import RandomForestClassifier  # 随机森林分类器，用于构建分类模型
from sklearn.metrics import classification_report  # 用于评估分类模型的性能，包括精确率、召回率等指标

# Step 1: 数据预处理与加载日志文件
def load_logs(log_file_path):
    if not os.path.exists(log_file_path):
        raise FileNotFoundError(f"Log file '{log_file_path}' not found.")

    # 假设每行是一条日志
    with open(log_file_path, 'r', encoding='utf-8') as file:
        logs = file.readlines()
    return logs

# Step 2: 构建示例数据集并标记数据（真实场景需根据具体情况标注）
def create_dataset():
    data = {
        'log': [
            'User login successful',
            'Disk space running low',
            'Error: Unable to connect to database',
            'Backup completed successfully',
            'Warning: High memory usage detected',
            'User logout',
            'Critical: System crash',
            'Service restarted',
        ],
        'label': [0, 1, 1, 0, 1, 0, 1, 0]  # 0: 正常, 1: 异常
    }
    return pd.DataFrame(data)

# Step 3: TF-IDF 特征提取与模型训练
def train_model(dataset):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(dataset['log'])
    y = dataset['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, y_pred))

    return model, vectorizer

# Step 4: 实时检测日志
def detect_anomalies(logs, model, vectorizer):
    features = vectorizer.transform(logs)
    predictions = model.predict(features)
    for log, label in zip(logs, predictions):
        status = "异常" if label == 1 else "正常"
        print(f"日志: {log.strip()} -> 检测结果: {status}")

# 示例用法
def main():
    # 创建训练数据
    dataset = create_dataset()

    # 训练模型
    model, vectorizer = train_model(dataset)

    # 加载实际日志文件（替换为自己的日志文件路径）
    log_file_path = r'F:\\1-Python 全栈运维开发：从基础到企业级实战\\班级直播主题内容\\第5场直播：Python赋能AI：在DevOps领域的应用与实践\\path_to_your_log_file.log'  # 修改为实际路径
    try:
        logs = load_logs(log_file_path)
    except FileNotFoundError as e:
        print(e)
        return

    # 实时检测
    detect_anomalies(logs, model, vectorizer)

if __name__ == "__main__":
    main()
~~~
