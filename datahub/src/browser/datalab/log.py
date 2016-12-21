#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymongo
from time import asctime
import json
import os
import re
import csv
import db_connect


public_data = "/home/ubuntu/workspace/data_set_public"

def get_clone_name(username,repo):
    if username == "likeqiang":
        return repo
    if username == "zjsxzyuser":
        return repo
    clone_name = "%s_%s" % (repo.lower(),username.lower())
    return clone_name

def get_project_list(user_name):
    project_list = []
    List = os.listdir("/home/%s"%(user_name))
    for a in List:
        if '.' in a:
            continue
        project_list.append(a)
    return project_list
        

def get_dict(username,projec_namet,exp):
    data_dic = {}
    data_dic["time"] = exp["time"]
    data_dic["commit"] = exp["commit"]["id"]
    data_dic["accuracy"] = exp["accuracy"]
    data_dic["project"] = projec_namet
    data_dic["user_name"] = username
    return data_dic


def creat_csv(username,repo_name,data):
    FIELDS = ['user_name','time', 'commit', 'accuracy', 'project']    
    csv_file = open("/home/ubuntu/result/%s/%s.csv"%(username,repo_name),'wb')  
    writer = csv.DictWriter(csv_file, fieldnames = FIELDS)
    #writer.writerow(dict(zip(FIELDS, FIELDS)))
    writer.writerows(data)
    csv_file.close()

def updata_record_result():
    file_path = public_data + "/titanic_leader_board.csv"
    with open(file_path,'rb') as f:
        reader = list(csv.reader(f))
        f.close()
        
    reader.pop(0)
    print reader
    for a in reader:
        username = a[1]
        print "repo: ",a
        repos = get_project_list(username)
        for repo_name in repos:
            print username,repo_name,a[2],"accuracy",a[3]
            if db_connect.update_exp_feature(username,repo_name,a[2],"accuracy",a[3]):
                if not os.path.isdir("/home/ubuntu/result"):
                    os.mkdir("/home/ubuntu/result")
                if not os.path.isdir("/home/ubuntu/result/%s"%(username)):
                    os.mkdir("/home/ubuntu/result/%s"%(username))
                        
                data = db_connect.get_poject_exp_list(username,repo_name)
                
                data_list = []
                for exp in data["exp_records"]:
                    if exp.has_key("accuracy"):
                        data_list.append(get_dict(username,repo_name,exp))
                creat_csv(username,repo_name,data_list)


if __name__ == "__main__":
    print updata_record_result()