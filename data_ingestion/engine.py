# data_ingestion/engine.py
# Executes data_ingestion.main whether run as a module or script.

import runpy

if __name__ == "__main__":
    runpy.run_module("data_ingestion.main", run_name="__main__")