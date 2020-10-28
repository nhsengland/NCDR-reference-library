import os
import subprocess
import sys
from datetime import datetime, timedelta

import boto3


def dump_database(db_name, db_user, backup_name):
    print(f"Dumping db name: {db_name}")
    command = f"pg_dump {db_name} -U {db_user}"
    print(f"Running: {command}")
    with open(backup_name, "wb") as out:
        subprocess.check_call(command, stdout=out, shell=True)

    if not os.path.exists(backup_name):
        raise Exception(f"Database dump not saved for: {db_name}")


def upload(bucket_name, local_path, key):
    """
    Given a bucket name, key_name and filename will upload the referenced file
    to the given bucket against the provided key_name.
    """
    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).upload_file(local_path, f"backups/{key}")


def get_backup_name(some_datetime, db_name):
    dt_str = some_datetime.strftime("%Y-%m-%d")
    return f"{dt_str}-{db_name}.dump"


def main(db_name, db_user, backups_dir, bucket_name):
    backup_name = get_backup_name(datetime.now(), db_name)
    full_backup_name = os.path.join(backups_dir, backup_name)
    dump_database(db_name, db_user, full_backup_name)
    upload(bucket_name, full_backup_name, backup_name)
    delete_old_backups(backups_dir, db_name)


def delete_old_backups(backups_dir, db_name):
    now = datetime.now()
    to_keep = set()
    for i in range(30):
        some_dt = now - timedelta(i)
        to_keep.add(get_backup_name(some_dt, db_name))

    for file_name in os.listdir(backups_dir):
        if file_name not in to_keep:
            full_file = os.path.join(backups_dir, file_name)
            print("deleting {}".format(full_file))
            os.remove(full_file)


if __name__ == "__main__":
    try:
        _, db_name, db_user, backups_dir, bucket_name = sys.argv
        main(db_name, db_user, backups_dir, bucket_name)
    except Exception as e:
        print(f"errored with {e}")
