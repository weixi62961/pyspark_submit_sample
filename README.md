# pyspark_submit_sample
- pyspark提交任务时，由于外部依赖情况比较多，因此制作了几个sample文件，分别测试spark-submt来提交pyspark任务

## 测试不同依赖条件的任务提交
### 1. 无依赖情况
- 使用spark安装目录下examples的pi.py文件
```bash
spark-submit --master local \
pi.py 10
```

### 2. 依赖自己源码的单个或多个文件（file）
- 使用目录下 test_file_dependency.py, 依赖 math_util.py 中定义的函数
- 使用 --py-files 上传 一个或多个依赖的py文件
```bash
spark-submit --master local \
--py-files math_util.py \
test_file_dependency.py
```
### 3. 依赖自己源码的单个或多个模块（module）
- 使用目录下 test_module_dependency.py, 依赖 moudle my_utils
```bash
# 先 zip 打包模块
zip -r my_module.zip my_utils

# 在提交任务
spark-submit --master local \
--py-files my_module.zip \
test_module_dependency.py

```

### 4. 依赖第三方模块
- 参照官方文档 [Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html) 进行多个第三方依赖包的管理。
- 依赖pandas、pyarrow的例子。 使用 官网 [Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html) 的例子 app.py， 命名为 test_pandas_udf.py

```bash
# TODO 

```


## 参考资料
- [spark offical site: Python Package Management](https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html)
- [databricks blog: How to Manage Python Dependencies in PySpark](https://www.databricks.com/blog/2020/12/22/how-to-manage-python-dependencies-in-pyspark.html)
- [在spark上运行Python脚本遇到“ImportError: No module name xxxx”](https://blog.csdn.net/wangxiao7474/article/details/81391300)
- [A Case for Isolated Virtual Environments with PySpark](https://www.inovex.de/de/blog/isolated-virtual-environments-pyspark/)
- [Best Practices for PySpark ETL Projects](https://alexioannides.com/2019/07/28/best-practices-for-pyspark-etl-projects/)