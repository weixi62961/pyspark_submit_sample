# 针对 kyuubi 的 Batch api，提交 PySpark 任务的情况的说明

- [Create PySpark batch jobs tests for RESTful API #5380](https://github.com/apache/kyuubi/issues/5380)

## 结论
针对PySpark任务， 建议通过 post batches existing resource的方式提交job，而不是 uploading resource 的方式。


## 问题
- up to Kyuubi 1.8.0，Rest API for creating batches in two ways：
	- https://kyuubi.readthedocs.io/en/master/client/rest/rest_api.html#post-batches
	- https://kyuubi.readthedocs.io/en/master/client/rest/rest_api.html#post-batches-with-uploading-resource
- 目前，uploading-resource仅能上传一种resource，这对于通常PySpark job是不够用的。
- PySpark任务 与 JarSpark 任务不同， JarSpark任务通常是一个uber-jar/fat-jar，所有的依赖都打包在一起。复杂一些的PySpark任务，不仅需要resource，而且还需要依赖的模块zip包。
因为Kyuubi背后也是基于spark-submit来进行实现的。因此示例如下：
```bash
# JarSpark job
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
fat-jar-with-dependencies.jar

# PySpark job
$SPARK_HOME/bin/spark-submit \
--master yarn \
--deploy-mode cluster \
--py-files dependency.zip \
main.py
```

## 解决方案
- 针对上述情况的解决方案，是使用 existing resource的方式提交。 先将资源和依赖zip包都上传至HDFS或者NFS等均能访问的位置。再通过post-batches接口提交任务。
- 下面是一个示例， 使用HDFS。

- json parameter
```json
{
	"batchType": "PYSPARK",
	"resource": "hdfs:/tmp/upload/main.py",
	"conf": {
		"spark.master": "yarn",
		"spark.submit.deployMode": "cluster",
		"spark.submit.pyFiles": "hdfs:/tmp/upload/dependency.zip"
	}
}
```

- curl command
```bash
curl -H "Content-Type: application/json" \
-X POST \
-d '{"batchType":"PYSPARK","resource":"hdfs:/tmp/upload/main.py","conf":{"spark.master":"yarn","spark.submit.deployMode":"cluster","spark.submit.pyFiles":"hdfs:/tmp/upload/dependency.zip"}}' \
http://localhost:10099/api/v1/batches
```
