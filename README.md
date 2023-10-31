# pyspark_submit_sample
- pyspark提交任务时，由于外部依赖情况比较多，因此制作了几个sample文件，分别测试spark-submt来提交pyspark任务.

## 测试不同依赖条件的任务提交
1. 无依赖情况。 例如 spark安装目录下examples的pi.py文件，计算pi值。
2. 依赖自己源码的单个或多个文件（pyton file）
3. 依赖自己源码的单个或多个模块（module），这种情况比较普遍，一般线上工程都是一个python工程，多个文件打包成zip。 
4. （隔离环境）依赖第三方模块，且需要隔离环境的情况。 如果仅仅依赖pandas、pyarrow，不需要隔离环境，那么让集群管理员直接在所有excutor上安装统一的环境即可。如果需要隔离的环境，则需要参考这种情况的解法。这种情况，比较类似于uber-jar/fat-jar的java工程的情况，把所有依赖打包在一起。
5. 融合3和4，既需要第三方依赖的隔离环境，又有自己工程的zip包。

### 1. 无依赖情况
- 示例文件： 使用spark安装目录下examples的pi.py文件，拷贝到本工程目录下了。 
- 运行成功，输出结果类似于
```text
Pi is roughly 3.1411124
```

- local
```bash
cd pyspark_submit_sample

$SPARK_HOME/bin/spark-submit \
--master local \
pi.py 10
```

- yarn cluster
```bash
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
pi.py 10
```


### 2. 依赖自己源码的单个或多个文件（python file）
- 使用目录下 test_file_dependency.py, 依赖 math_util.py 中定义的函数
- 运行成功，输出结果类似于
```text
+---+---+----------+
| id|  v|tripple_id|
+---+---+----------+
|  1|1.0|         1|
|  2|2.0|         8|
|  3|3.0|        27|
+---+---+----------+
```

- 使用 --py-files 上传 一个或多个依赖的py文件
- local
```bash
$SPARK_HOME/bin/spark-submit \
--master local \
--py-files math_util.py \
test_file_dependency.py
```

- yarn cluster
```bash
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--py-files math_util.py \
test_file_dependency.py
```

### 3. 依赖自己源码的单个或多个模块（module）
- 使用目录下 test_module_dependency.py, 依赖 moudle my_utils
- 运行成功，输出结果类似于
```text
+---+---+----------+
| id|  v|tripple_id|
+---+---+----------+
|  1|1.0|         1|
|  2|2.0|         8|
|  3|3.0|        27|
+---+---+----------+
```
- 先 zip 打包模块
```bash
cd pyspark_submit_sample
zip -r ../module_dependency.zip .
mv ../module_dependency.zip ./
```
- local
```bash
# 提交任务
spark-submit --master local \
--py-files ../pyspark_submit_sample.zip \
test_module_dependency.py
```
- yarn cluster
```bash
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--py-files ../pyspark_submit_sample.zip \
test_module_dependency.py
```
- yarn cluster + HDFS: 另外一种更好的方式，是将PySpark任务的相关依赖及主文件，全部上传hdfs。
```bash
# 先上传 HDFS
hdfs dfs -put ../pyspark_submit_sample.zip /tmp/upload
hdfs dfs -put test_module_dependency.py /tmp/upload

# 再提交
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--py-files hdfs:/tmp/upload/pyspark_submit_sample.zip \
hdfs:/tmp/upload/test_module_dependency.py

```

### 4. 依赖第三方模块，且需要隔离环境的情况
- 参照官方文档 [Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html) 进行多个第三方依赖包的管理。
- 依赖pandas、pyarrow的例子。 使用 官网 [Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html) 的例子 app.py， 命名为 test_pandas_udf.py
- 仅能在yarn cluster 模式测试通过, 运行成功，输出结果类似于
```text
[Row(id=1, mean_udf(v)=1.5), Row(id=2, mean_udf(v)=6.0)]
```

- yarn cluster
```bash
# 首先打包 conda_env
conda create -n pyspark_conda_env python=3.9.5
conda activate pyspark_conda_env
conda install -c conda-forge conda-pack
pip install pyarrow pandas
# -f --force Overwrite any existing archive at the output path.
conda pack -n pyspark_conda_env -f -o pyspark_conda_env.tar.gz
conda deactivate

# 再进行提交
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--conf "spark.pyspark.driver.python=./conda_env/bin/python3" \
--conf "spark.pyspark.python=./conda_env/bin/python3" \
--archives ../pyspark_conda_env.tar.gz#conda_env \
test_pandas_udf.py

```

### 5. 融合3和4，既需要第三方依赖的隔离，又有自己工程的zip包。
- 把3和4的参数，合并在一起就可以了。下面使用hdfs上的文件进行演示。
- yarn cluster
```bash
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--conf "spark.pyspark.driver.python=./conda_env/bin/python3" \
--conf "spark.pyspark.python=./conda_env/bin/python3" \
--archives hdfs:/tmp/upload/pyspark_conda_env.tar.gz#conda_env \
--py-files hdfs:/tmp/upload/pyspark_submit_sample.zip \
hdfs:/tmp/upload/test_module_dependency_and_pandas_udf.py
```


## 备注
### 1. spark-submit提交的命令行参数，与spark-default.conf中配置对应关系
- spark-submit的命令行参数，最终都转换为conf配置。例如 --master yarn 等价于 --conf "spark.master=yarn". 对应关系如下表： 

| spark-submit参数  | spark-defaults.conf 属性 | 示例值                             |
| ----------------- | ---------------------------- | ---------------------------------- |
| --master          | spark.master                 | yarn                               |
| --deploy-mode     | spark.submit.deployMode      | cluster                            |
| --name            | spark.app.name               | Spark PI                           |
| --driver-cores    | spark.driver.cores           | 1                                  |
| --driver-memory   | spark.driver.memory          | 1g                                 |
| --num-executors   | spark.executor.instances     | 1                                  |
| --executor-cores  | spark.executor.cores         | 1                                  |
| --executor-memory | spark.executor.memory        | 1g                                 |
| --queue           | spark.yarn.queue             | root.hive                          |
| --py-files        | spark.submit.pyFiles         | my_module.zip                      |
| --archives        | spark.yarn.dist.archives     | pyspark_conda_env.tar.gz#conda_env |


- 示例, 全部使用conf格式
```bash
# 等价于
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--conf "spark.master=yarn" \
--conf "spark.submit.deployMode=cluster" \
--conf "spark.pyspark.driver.python=./conda_env/bin/python3" \
--conf "spark.pyspark.python=./conda_env/bin/python3" \
--conf "spark.yarn.dist.archives=hdfs:/tmp/upload/pyspark_conda_env.tar.gz#conda_env" \
--conf "spark.submit.pyFiles=hdfs:/tmp/upload/pyspark_submit_sample.zip" \
hdfs:/tmp/upload/test_module_dependency_and_pandas_udf.py
```


## 参考资料
- [Spark: Submitting Applications](https://spark.apache.org/docs/latest/submitting-applications.html)	
- [Spark Configuration](https://spark.apache.org/docs/latest/configuration.html)
- [Spark: Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html)
- [databricks blog: How to Manage Python Dependencies in PySpark](https://www.databricks.com/blog/2020/12/22/how-to-manage-python-dependencies-in-pyspark.html)
- [在spark上运行Python脚本遇到“ImportError: No module name xxxx”](https://blog.csdn.net/wangxiao7474/article/details/81391300)
- [A Case for Isolated Virtual Environments with PySpark](https://www.inovex.de/de/blog/isolated-virtual-environments-pyspark/)
- [Best Practices for PySpark ETL Projects](https://alexioannides.com/2019/07/28/best-practices-for-pyspark-etl-projects/)
- [pyspark经验小结](https://zekizz.github.io/da-shu-ju/pyspark-notes/)