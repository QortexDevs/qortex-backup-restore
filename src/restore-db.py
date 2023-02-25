import boto3
import os

from helpers.helpers import prepare_file_path, restore_postgres_db_from_gz

db_container_name = os.environ.get('DB_CONTAINER_NAME')
project_name = os.environ.get('PROJECT_NAME')

db_name = os.environ.get('DB_NAME')
db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')

storage_directory = 'db'

gz_sql_backup_file_path = prepare_file_path(
    storage_directory, project_name, 'latest.sql.gz')
raw_sql_backup_file_path = prepare_file_path(
    storage_directory, project_name, 'latest.sql')

session = boto3.session.Session()

s3_client = session.client(
    service_name='s3',
    aws_access_key_id=os.environ.get('S3_AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('S3_AWS_SECRET_ACCESS_KEY'),
    endpoint_url=os.environ.get('S3_ENDPOINT_URL'),
)

s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
s3_backup_root = 'backups/'

s3_client.download_file(
    s3_bucket_name,
    f'{s3_backup_root}{storage_directory}/latest.sql.gz', gz_sql_backup_file_path)
restore_postgres_db_from_gz(
    db_container_name,
    db_name,
    db_username,
    db_password,
    gz_sql_backup_file_path,
    raw_sql_backup_file_path)
