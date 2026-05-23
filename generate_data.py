import pandas as pd
import numpy as np


def generate_data():

    print("Generating datasets...")

    num_users = 500000
    num_transactions = 1000000

    users = pd.DataFrame({
        'user_id': np.arange(1, num_users + 1),
        'name': ['User_' + str(i) for i in range(num_users)],
        'signup_date': pd.date_range(
            start='2020-01-01',
            periods=num_users,
            freq='min'
        )
    })
    users.to_csv('users.csv', index=False)

    transactions = pd.DataFrame({
        'transaction_id': np.arange(1, num_transactions + 1),
        'user_id': np.random.randint(
            1,
            num_users + 1,
            size=num_transactions
        ),
        'amount': np.random.uniform(
            5.0,
            500.0,
            size=num_transactions
        ).round(2)
    })
    transactions.to_csv('transactions.csv', index=False)

    print("Files created")


if __name__ == "__main__":
    generate_data()