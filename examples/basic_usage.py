from oradb_extractor import extract_sync

if __name__ == "__main__":
    df = extract_sync(
        "SELECT * FROM dual",
        dsn="localhost/orclpdb",
        user="system",
        password="oracle",
    )
    print(df.head())
