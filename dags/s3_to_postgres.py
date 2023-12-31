from datetime import datetime

from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_sql import S3ToSqlOperator


def json_parser(filepath):
    import json
    from datetime import datetime

    import pandas as pd

    with open(filepath) as f:
        json_data = json.load(f)
        df = pd.DataFrame(json_data['body'])
        df['ts'] = df['ts'].map(lambda ts: datetime.fromtimestamp(ts/1000))
        return df.values
    
with DAG(
    dag_id='s3_to_postgres',
    start_date=datetime(2022, 10, 1),
    schedule='@once',
    catchup=True
) as dag:
    
    s3_key_sensor = S3KeySensor(
        task_id='sensor_s3_key',
        aws_conn_id='aws_connection',
        bucket_name='eventsim',
        bucket_key='eventsim/10000.json',
        mode='poke',
        poke_interval=30,
    )

    transfer_s3_to_sql = S3ToSqlOperator(
        task_id='transfer_s3_to_postgres',
        s3_bucket='eventsim',
        s3_key='eventsim/10000.json',
        parser=json_parser,
        table='events',
        column_list=(
            'ts', 'userId', 'sessionId', 'page', 'auth', 'method', 
            'status', 'level', 'itemInSession', 'location', 'userAgent', 'lastName', 
            'firstName', 'registration', 'gender', 'artist', 'song', 'length'
        ),
        sql_conn_id='postgres_connection',
        aws_conn_id='aws_connection',
        dag=dag
    )

s3_key_sensor >> transfer_s3_to_sql