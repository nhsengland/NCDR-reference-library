import os
import sys
import boto3
import subprocess
from datetime import datetime


def dump_database(db_name, db_user, backup_name):
    print('Dumping db_name: {}'.format(db_name))
    command = 'pg_dump {} -U {}'.format(db_name, db_user)
    print('Running: {}'.format(command))
    with open(backup_name, 'wb') as out:
        subprocess.check_call(command, stdout=out, shell=True)

    if not os.path.exists(backup_name):
        raise Exception('Database dump not saved for: {}'.format(db_name))


def upload(full_file_name, file_name, bucket_name):
    """
    Given a bucket nane, key_name and filename will upload the referenced file
    to the given bucket against the provided key_name.
    """
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).upload_file(full_file_name, file_name)


def main(db_name, db_user, backups_dir, bucket_name):
    today = datetime.now().strftime("%d-%m-%Y")
    backup_name = "{}-{}.dump".format(db_name, today)

    full_backup_name = os.path.join(
        backups_dir,
        backup_name
    )
    dump_database(db_name, db_user, full_backup_name)
    upload(full_backup_name, backup_name, bucket_name)


if __name__ == '__main__':
    try:
        _, db_name, db_user, backups_dir, bucket_name = sys.argv
        main(db_name, db_user, backups_dir, bucket_name)
    except Exception as e:
        print('errored with {}'.format(str(e)))
