#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pymongo
from time import asctime
import json
import os
import re
import csv



def creat_connect():
    config = json.load(open("/home/ubuntu/sandbox/config.json"))
    try:
        client = pymongo.MongoClient(config["mongodb_url"])
    except Exception as e:
        print e
        raise Exception("fail to connect to given MongoDB")
    return client




def get_poject_exp_list(username,project_name):
    if True:
        connect = creat_connect().users
        exper_coll = connect.Administrator
        print "OK",project_name
        result = exper_coll.find_one({"exp_name":project_name})
    else:
        print "fail to get the project list in the mongodb"
        raise Exception("fail to connect to given MongoDB")
    return result


def delect_project_record(username,project_name):
    connect = creat_connect().users
    exper_coll = connect.Administrator
    try:
        exper_coll.remove({"exp_name":project_name})
    except Exception as e:
        raise Exception("fail to delect the recode of " + project_name)

        
        
        
def update_exp(username,project_name,data):
    connect = creat_connect().users
    exper_coll = connect.Administrator
    if True:
        exper_coll.update({'exp_name': project_name}, {'$set': {'exp_records': data}})
        return True
    else:
        print "gg fail to update the data"
        return False
        raise Exception("fail to update the recode of " + project_name)
        
    
    
### for test
if __name__ == "__main__":
    print delect_project_record("asdfasdf","test2")

