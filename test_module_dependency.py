from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType

from my_utils.math_util import my_tripple

def main():
    spark = SparkSession\
        .builder\
        .getOrCreate()
    
    df = spark.createDataFrame(
        [(1, 1.0), (2, 2.0), (3, 3.0)],
        ("id", "v"))

    tripple_udf = udf(lambda x: my_tripple(x), LongType())

    df.withColumn("tripple_id", tripple_udf("id")).show()

    spark.stop()


if __name__ == "__main__":
    main()