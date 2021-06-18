import os
import datetime
import random
import pandas as pd
import pymongo as pm
import json
import numpy as np
from bson import json_util

HOST = 'mongodb://localhost:27017/'
DATABASE = 'inter_test'
COLLECTION = 'booking_duration'

class DatabaseHandler:
    
    def __init__(self,host=HOST,database=DATABASE) -> None:
        self.client = pm.MongoClient(host)
        self.db = self.client[database]
        return

    def upload(self,document,collection):
        if self.check_unicity(document,collection):
            id_object = self.db[collection].insert_one(json.loads(json_util.dumps(document)))
        else:
            print("Already existing document for those date")
            id_object=None
        return id_object

    def query(self,query):
        return list(self.col.aggregate(query))
    
    def check_unicity(self,document,collection):
        #Control that there is not already the item in the db
        c =self.db[collection].count_documents({"city":document["city"],"year":document["year"],"month":document["month"],"day":document["day"]}, limit= 1)
        if c==0:
            return True
        return False