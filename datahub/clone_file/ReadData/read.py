#!/usr/bin/env python
# encoding: utf-8

__author__ = 'beyhhhh'
import csv
import os
import json

def read_data_set(username,repo,data_name):
    clone_name = repo
    
    target_path = "/home/ubuntu/sunjiaojiao/datahub/clone_file/json/" + clone_name + ".json"
    print target_path
    if os.path.isfile(target_path):
        f = open(target_path)
        dic = json.load(f)
        print dic
        if dic["date_set"].has_key(data_name):
            path = dic["date_set"][data_name]["path"]
            with open(path,'rb') as f:
                reader = list(csv.reader(f))
                f.close()
                return reader
    
    
    
def get_data_set_path(username,repo,data_name):
    clone_name = repo
    
    target_path = "/home/ubuntu/sunjiaojiao/datahub/clone_file/json/" + clone_name + ".json"
    
    if os.path.isfile(target_path):
        f = open(target_path)
        dic = json.load(f)
        
        if dic["date_set"].has_key(data_name):
            return dic["date_set"][data]["path"]
            
    