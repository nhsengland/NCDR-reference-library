import os
import boto3
import subprocess
from datetime import datetime


def dump_database(db_name, backup_name):
    print('Dumping db_name: {}'.format(db_name))
    target = os.path.join(backup_name, '{}.dump'.format(db_name))
    command = 'pg_dump --format=custom {}'.format(db_name)
    print('Running: {}'.format(command))
    with open(target, 'wb') as out:
        subprocess.check_call(command, stdout=out, shell=True)

    if not os.path.exists(target):
        raise Exception('Database dump not saved for: {}'.format(db_name))


def upload(full_file_name, file_name, bucket_name):
    """
    Given a bucket nane, key_name and filename will upload the referenced file
    to the given bucket against the provided key_name.
    """
    s3 = boto3.client('s3')
    s3.Bucket(bucket_name).upload_file(full_file_name, file_name)


def main(db_name, backups_dir, bucket_name):
    today = datetime.now().strftime("%d-%m-%Y")
    backup_name = "{}-{}.dump".format(db_name, today)

    full_backup_name = os.path.joins(
        backups_dir,
        backup_name
    )
    dump_database(db_name, full_backup_name)
    upload(full_backup_name, backup_name, bucket_name)


if __name__ == '__main__':
    try:
        _, db_name, backups_dir, bucket_name = sys.argv
        main(db_name, backups_dir)
    except Exception as e:
        print('errored with {}'.format(str(e)))
