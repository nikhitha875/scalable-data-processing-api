import pandas as pd
import os
import csv

NUM_BUCKETS = 20

USERS_FILE = "users.csv"
TRANSACTIONS_FILE = "transactions.csv"
RESULT_FILE = "result.csv"

USERS_BUCKET_DIR = "users_buckets"
TRANSACTIONS_BUCKET_DIR = "transactions_buckets"

os.makedirs(USERS_BUCKET_DIR, exist_ok=True)
os.makedirs(TRANSACTIONS_BUCKET_DIR, exist_ok=True)


def bucket_file(directory, bucket_num):
    return os.path.join(directory, f"bucket_{bucket_num}.csv")


# -----------------------------------------
# PARTITION USERS
# -----------------------------------------

def partition_users():

    print("Partitioning users")

    writers = {}
    files = {}

    for i in range(NUM_BUCKETS):

        path = bucket_file(USERS_BUCKET_DIR, i)

        f = open(path, "w", newline="")

        files[i] = f

        writer = csv.writer(f)

        writer.writerow([
            "user_id",
            "name",
            "signup_date"
        ])

        writers[i] = writer

    for chunk in pd.read_csv(
        USERS_FILE,
        chunksize=50000
    ):

        for row in chunk.itertuples(index=False):

            bucket = row.user_id % NUM_BUCKETS

            writers[bucket].writerow(row)

    for f in files.values():
        f.close()

    print("Users partitioned")


# -----------------------------------------
# PARTITION TRANSACTIONS
# -----------------------------------------

def partition_transactions():

    print("Partitioning transactions")

    writers = {}
    files = {}

    for i in range(NUM_BUCKETS):

        path = bucket_file(
            TRANSACTIONS_BUCKET_DIR,
            i
        )

        f = open(path, "w", newline="")

        files[i] = f

        writer = csv.writer(f)

        writer.writerow([
            "transaction_id",
            "user_id",
            "amount"
        ])

        writers[i] = writer

    for chunk in pd.read_csv(
        TRANSACTIONS_FILE,
        chunksize=50000
    ):

        for row in chunk.itertuples(index=False):

            bucket = row.user_id % NUM_BUCKETS

            writers[bucket].writerow(row)

    for f in files.values():
        f.close()

    print("Transactions partitioned")


# -----------------------------------------
# JOIN BUCKETS
# -----------------------------------------

def join_buckets():

    print("Joining buckets")

    with open(
        RESULT_FILE,
        "w",
        newline=""
    ) as result_file:

        writer = csv.writer(result_file)

        writer.writerow([
            "transaction_id",
            "user_id",
            "amount",
            "name",
            "signup_date"
        ])

        for i in range(NUM_BUCKETS):

            users_path = bucket_file(
                USERS_BUCKET_DIR,
                i
            )

            transactions_path = bucket_file(
                TRANSACTIONS_BUCKET_DIR,
                i
            )

            users_map = {}

            for chunk in pd.read_csv(
                users_path,
                chunksize=50000
            ):

                for row in chunk.itertuples(index=False):

                    users_map[row.user_id] = {
                        "name": row.name,
                        "signup_date": row.signup_date
                    }

            for chunk in pd.read_csv(
                transactions_path,
                chunksize=50000
            ):

                for row in chunk.itertuples(index=False):

                    if row.user_id in users_map:

                        user = users_map[row.user_id]

                        writer.writerow([
                            row.transaction_id,
                            row.user_id,
                            row.amount,
                            user["name"],
                            user["signup_date"]
                        ])

            print(f"Bucket {i} joined")

    print("Join complete")


if __name__ == "__main__":

    partition_users()

    partition_transactions()

    join_buckets()