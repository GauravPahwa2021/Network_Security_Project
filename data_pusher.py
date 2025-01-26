import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

import certifi
ca = certifi.where()

import pymongo
import pandas as pd
from networksecuritysystem.exception.exception import NetworkSecuritySystemException
from networksecuritysystem.logging.logger import logging


class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecuritySystemException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            return NetworkSecuritySystemException(e,sys)
        
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGODB_URL)
            self.db = self.mongo_client[self.database]
            self.collection = self.db[self.collection]
            self.collection.insert_many(records)
            return (len(self.records))
        except Exception as e:
            return NetworkSecuritySystemException(e,sys)
        

if __name__=='__main__':
    FILE_PATH = "Network_Data\phisingData.csv"
    DATABASE = "PhishingDatabase"
    COLLECTION = "NetworkData"

    network_obj = NetworkDataExtract()
    records = network_obj.csv_to_json_convertor(file_path=FILE_PATH)
    print(records)

    no_of_records_inserted = network_obj.insert_data_mongodb(records=records,database=DATABASE,collection=COLLECTION)
    print(f"Number of records inserted in MongoDB: {no_of_records_inserted}")
