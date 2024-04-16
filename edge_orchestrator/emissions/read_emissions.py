import pandas as pd


def read_csv_file(file_path):
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    print(df.head())


if __name__ == "__main__":
    import sys

    read_csv_file(sys.argv[1])
