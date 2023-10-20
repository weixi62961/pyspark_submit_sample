# refer to: https://spark.apache.org/docs/latest/api/python/user_guide/python_packaging.html app.py
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql import SparkSession

def main():
    spark = SparkSession\
        .builder\
        .getOrCreate()

    df = spark.createDataFrame(
        [(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)],
        ("id", "v"))

    @pandas_udf("double")
    def mean_udf(v: pd.Series) -> float:
        return v.mean()

    print(df.groupby("id").agg(mean_udf(df['v'])).collect())

    spark.stop()


if __name__ == "__main__":
    main()