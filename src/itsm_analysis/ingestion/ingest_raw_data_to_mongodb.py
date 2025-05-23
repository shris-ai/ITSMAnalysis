import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_ENDPOINT")
print(MONGO_DB_URL)

import certifi
# certificate authorities
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo

from itsm_analysis.exception.exception import ITSMAnalysisException
from itsm_analysis.logging_config.logger import logging

class ITSMDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise ITSMAnalysisException(e, sys)
        
    def csv_to_json_converter(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise ITSMAnalysisException(e, sys)
        
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)

            return(len(self.records))
        
        except Exception as e:
            raise ITSMAnalysisException(e, sys)
        
import ssl
if __name__ == '__main__':
    FILE_PATH = "data/ITSM_data.csv"
    DATABASE="ITSM"
    COLLECTION = "ITSMData"
    itsm_obj = ITSMDataExtract()
    records=itsm_obj.csv_to_json_converter(file_path=FILE_PATH)
    no_of_records=itsm_obj.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(no_of_records)