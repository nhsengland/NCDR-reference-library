"""
Restores the database from an S3 backup.
If 3 arguments are passed in the backup it looks for has todays
date.

If 4 arguments are passed in it runs in dev mode and picks up
the most recent backup from the last 4 days.
"""
import datetime
import os
import subprocess
import sys

import boto3
import botocore


def get_backup_name(some_datetime, db_name):
    dt_str = some_datetime.strftime("%Y-%m-%d")
    return f"{dt_str}-{db_name}.dump"


def get_backup(bucket_name, db_name, look_back=False):
    s3 = boto3.resource("s3")
    if look_back:
        date_times = [datetime.datetime.now() - datetime.timedelta(i) for i in range(5)]
    else:
        date_times = [datetime.datetime.now()]
    file_names = [get_backup_name(dt, db_name) for dt in date_times]
    success = False
    for file_name in file_names:
        try:
            temp_file = f"/tmp/{file_name}"
            s3.Bucket(bucket_name).download_file(f"backups/{file_name}", temp_file)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("unable to find {}".format(file_name))
        else:
            success = True
            break
    if not success:
        raise ValueError("Unable to restore the database!")
    return temp_file


def load_file(db_name, db_user, file_name):
    command = "psql -d {} -U {} -f {}".format(db_name, db_user, file_name)
    subprocess.check_call(command, shell=True)


def main(db_name, db_user, bucket_name, dev=False):
    file_name = get_backup(bucket_name, db_name, look_back=dev)
    load_file(db_name, db_user, file_name)
    os.remove(file_name)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 4:
            _, db_name, db_user, bucket_name = sys.argv
            dev = False
        else:
            _, db_name, db_user, bucket_name, dev = sys.argv
        main(db_name, db_user, bucket_name, dev)
    except Exception as e:
        print("errored with {}".format(str(e)))
        raise
