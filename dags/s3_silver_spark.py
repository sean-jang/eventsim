from datetime import datetime

from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

with DAG (
    dag_id='bronze_to_silver',
    schedule='@once',
    start_date=datetime(2023, 12, 9),
    catchup=False
) as dag:
    spark_submit = SparkSubmitOperator(
        task_id='spark_submit',
        application='/home/ec2-user/airflow/dags/eventsim/dags/supports/spark_operator.py',
        conn_id='spark_connection',
        conf={
            "spark.hadoop.fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
            "spark.jars.packages": "org.apache.hadoop:hadoop-aws:3.3.2"
        }
    )

spark_submit