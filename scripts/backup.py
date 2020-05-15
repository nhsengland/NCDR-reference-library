import os
import subprocess
import sys
from datetime import datetime

import boto3


def dump_database(db_name, db_user, backup_name):
    print(f"Dumping db_name: {db_name}")
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


def main(branch, db_name, db_user, backups_dir, bucket_name):
    today = datetime.now().strftime("%Y-%m-%d")
    backup_name = f"{today}-{db_name}-{branch}.dump"

    full_backup_name = os.path.join(backups_dir, backup_name)
    dump_database(db_name, db_user, full_backup_name)
    upload(bucket_name, full_backup_name, backup_name)


if __name__ == "__main__":
    try:
        _, branch, db_name, db_user, backups_dir, bucket_name = sys.argv
        main(branch, db_name, db_user, backups_dir, bucket_name)
    except Exception as e:
        print(f"errored with {e}")
