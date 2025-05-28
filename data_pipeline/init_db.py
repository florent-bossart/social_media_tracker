from sqlalchemy import create_engine, MetaData
from load_json_to_postgres import metadata, engine, ensure_raw_schema


def main():
    ensure_raw_schema(engine)
    metadata.create_all(engine)
    print("All tables created (if not already present).")

if __name__ == "__main__":
    main()
