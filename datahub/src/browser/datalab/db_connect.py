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
    try:
        connect = creat_connect().users
        exper_coll = connect.Administrator
        result = exper_coll.find_one({"exp_name":project_name})
    except Exception as e:
        print "fail to get the project list in the mongodb"
        raise Exception("fail to connect to given MongoDB")
    return result


def get_push_record(username,clone_name,commit_id):
    try:
        record = get_poject_exp_list(username,clone_name)
        for a in record["exp_records"]:
            if commit_id == a["commit"]["short_id"]:
                return a
            if commit_id == a["commit"]["id"]:
                return a
    except Exception as e:
        print "fail to get the certen commit id project list in the mongodb"

            

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
    try:
        exper_coll.update({'exp_name': project_name}, {'$set': {'exp_records': data}})
        
    except Exception as e:
        print "gg fail to update the data"
        
        raise Exception("fail to update the recode of " + project_name)
        
        
def update_exp_feature(username,project_name,commit_id,data_name,data_feature):
    if True:
        data = get_poject_exp_list(username,project_name)
        if data == None:
            return False
        for a in data["exp_records"]:
            if a["commit"]["id"] == commit_id:
                a[data_name] = data_feature
        update_exp(username,project_name,data["exp_records"])
        return True
    else:
        print e
        raise Exception("fail to updata the %s recode of %s"%(data_name,project_name))
    return False

    
### for test
if __name__ == "__main__":
    print delect_project_record("asdfasdf","test2")

