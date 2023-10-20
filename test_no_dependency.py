from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType


def my_tripple(input):
    return input * input * input

def main(spark):
    spark = SparkSession\
        .builder\
        .getOrCreate()
    
    df = spark.createDataFrame(
        [(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)],
        ("id", "v"))

    tripple_udf = udf(lambda x: my_tripple(x), LongType())

    df.withColumn("tripple_id", tripple_udf("id")).show()

    spark.stop()


if __name__ == "__main__":
    main()