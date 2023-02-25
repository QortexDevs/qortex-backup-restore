import shutil
from datetime import datetime
import gzip
import subprocess
import os
import tempfile


def gzip_command_output(command: str, output_filename: str) -> None:
    with gzip.open(output_filename, 'wb') as f:
        popen = subprocess.Popen(
            command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

        for stdout_line in iter(popen.stdout.readline, ''):
            line = str(stdout_line).replace("\r", '').encode('utf-8')
            f.write(line)

        popen.stdout.close()
        popen.wait()


def backup_mysql_db_to_gz(container_name: str, db_name: str, db_username: str, db_password: str, output_filename: str) -> None:
    gzip_command_output(
        f'docker exec -t {container_name} sh -c \'MYSQL_PWD=\"{db_password}\" exec mysqldump -u\"{db_username}\" {db_name}\'', output_filename)


def backup_postgres_db_to_gz(container_name: str, db_name: str, db_username: str, db_password: str, output_filename: str) -> None:
    gzip_command_output(
        f'docker exec -t {container_name} pg_dump -c -U {db_username} {db_name}', output_filename)


def get_current_backup_folder_name():
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


def prepare_file_path(directory: str, project_name: str, file_name) -> str:
    temp_dir = tempfile.gettempdir()
    full_directory_path = os.path.join(temp_dir, project_name, directory)
    if not os.path.exists(full_directory_path):
        os.makedirs(full_directory_path, mode=0o777)
    full_directory_path = os.path.join(full_directory_path, file_name)
    return full_directory_path


def restore_postgres_db_from_gz(db_container_name: str, db_name: str, db_username: str, db_password: str, gz_sql_backup_file_path: str, raw_sql_backup_file_path: str) -> None:
    with gzip.open(gz_sql_backup_file_path, 'rb') as f_in:
        with open(raw_sql_backup_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    if os.name == 'nt':
        command = f'type {raw_sql_backup_file_path} | docker exec -i {db_container_name} psql -U {db_username}'
    else:
        command = f'cat {raw_sql_backup_file_path} | docker exec -i {db_container_name} psql -U {db_username}'
    popen = subprocess.check_output(
        command, universal_newlines=True, shell=True)


def restore_mysql_db_from_gz(db_container_name: str, db_name: str, db_username: str, db_password: str, gz_sql_backup_file_path: str, raw_sql_backup_file_path: str) -> None:
    with gzip.open(gz_sql_backup_file_path, 'rb') as f_in:
        with open(raw_sql_backup_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    command = f'cat {raw_sql_backup_file_path} | docker exec -i {db_container_name} sh -c \'MYSQL_PWD=\"{db_password}\" mysql -u\"{db_username}\" --database={db_name}\''
    popen = subprocess.Popen(
        command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)


def restore_network_mysql_db_from_gz(db_host: str, db_name: str, db_username: str, db_password: str, gz_sql_backup_file_path: str, raw_sql_backup_file_path: str) -> None:
    with gzip.open(gz_sql_backup_file_path, 'rb') as f_in:
        with open(raw_sql_backup_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    command = f'cat {raw_sql_backup_file_path} | mysql --host={db_host} --user=\"{db_username}\" --database={db_name}'
    subprocess.check_output(command, shell=True, universal_newlines=True)


def restore_network_postgres_db_from_gz(db_host: str, db_name: str, db_username: str, db_password: str, gz_sql_backup_file_path: str, raw_sql_backup_file_path: str) -> None:
    with gzip.open(gz_sql_backup_file_path, 'rb') as f_in:
        with open(raw_sql_backup_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    command = f'cat {raw_sql_backup_file_path} | psql -h {db_host} -U {db_username}'
    subprocess.check_output(command, shell=True, universal_newlines=True)
