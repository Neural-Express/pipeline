# data_ingestion/engine.py
try:
    # works when run as module: python -m data_ingestion.engine
    from .main import run
except ImportError:
    # works when run as script: python data_ingestion/engine.py
    from data_ingestion.main import run

if __name__ == "__main__":
    run()
