from sqlalchemy import create_engine, MetaData
from load_json_to_postgres import metadata, engine

def main():
    metadata.create_all(engine)
    print("All tables created (if not already present).")

if __name__ == "__main__":
    main()
