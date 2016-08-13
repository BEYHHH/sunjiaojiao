#!/usr/bin/env python
# encoding: utf-8

import os
import pexpect
import json

import shutil

source_path = "/home/ubuntu/sunjiaojiao/data_set_public/data_set"
target_path = "/home/ubuntu/sunjiaojiao/data_set_public/public_data"
json_path =  "/home/ubuntu/sunjiaojiao/data_set_public/json"

if os.path.isdir(target_path):
    file_list = os.listdir(target_path)
    print file_list
    for a in file_list:
        if not a[a.rfind('.'):] == ".csv":
            continue
        dic = {}
        dic["name"] = a
        dic["id"] = a
        dic["commit_id"] = a
        dic["short_commit_id"] = dic
        dic["path"] = target_path + "/" + a
        dic["class"] = "edu"
        dic["repo"] = None
        dic["user"] = "public"
        dic["type"] = "csv"
        dic["public"] = True
        print json_path +"/"+ a +".json"
        with open(json_path +"/"+ a +".json", "w") as f:
            f.write(json.dumps(dic,indent=2))
            
            
            