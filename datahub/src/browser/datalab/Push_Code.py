#-*- coding:utf-8 -*-
import json
import os
from optparse import OptionParser
import pymongo
import re
import run
import shutil
from time import asctime
import csv

target = "/home/ubuntu/workspace/Push_exp"
clone_path = "/home/ubuntu/workspace/clone_file"
hook_config_path = "/home/ubuntu/sandbox/config.json"


def verifyUser(client, name):
    """
        verify or create user for the record
    """

    users = client['users']
    if name not in users.collection_names():
        print("creat new user \""+name+"\"? [y/n]")
        if raw_input() != 'y':
            print("exiting...")
            sys.exit(0)
    return users[name]

def __Push__(username,repo,data,branch,message = "push the code to run"):
    
    repo_url = data["http_url_to_repo"]
    repo_name = data["name"]
    print "current dir: "+ os.getcwd()
    if os.path.isdir(target):
        if os.path.isdir(target + "/" + branch["commit"]["id"]):
            shutil.rmtree(target + "/" + branch["commit"]["id"])
        os.mkdir(target + "/" + branch["commit"]["id"])
    
    if not os.path.isdir(target + "/" + branch["commit"]["id"]):
        return
    print target + "/" + branch["commit"]["id"]
    os.chdir(target + "/" + branch["commit"]["id"])
    os.system("git clone -b " + branch["name"] + " " + repo_url)
    
    
    
    List =  os.listdir(target + "/" + branch["commit"]["id"] + "/" + repo_name)
    os.chdir(target + "/" + branch["commit"]["id"] + "/" + repo_name)
    
    
    for a in List:
        if a[a.rfind('.'):] == ".ipynb":
            os.system("ipython nbconvert --to python " + a)
    
    
    Code_list = []
    List =  os.listdir(target + "/" + branch["commit"]["id"] + "/" + repo_name)
    for a in List:
        if a[a.rfind('.'):] == ".py":
            Code_list.append(a)
        if a[a.rfind('.'):] == ".java":
            Code_list.append(a)
            
            
    try:
        config = json.load(open(hook_config_path))
    except Exception as e:
        print e
        print "can't get the configs to connect the mongodb"
        
    try:
        print "set the params"
        branch['time'] = asctime()
        repo_name = data['name']
        branch['branch_name'] = branch['name']
        branch['name'] = data['owner']['name']
        branch['commit']['short_id'] = branch['commit']['id'][:11]
        branch['username'] = username
        branch['repo_name'] = repo_name
        branch['is_run'] = False
        branch['has_run'] = False
        branch['codes'] = Code_list
        branch['note'] = message
        
        
        
        
    except Exception as e:
        print e
        print "lost some key in the dic"
        if os.path.isdir(target + "/" + branch["commit"]["id"]):
            shutil.rmtree(target + "/" + branch["commit"]["id"])
            return "the connect with the mongdb isn't ok"
        
        
        
    
    try:
        print "connect the mongodb and make some changes"
        try:
            client = pymongo.MongoClient(config["mongodb_url"])
        except Exception as e:
            raise Exception("fail to connect to given MongoDB")
            
        user = verifyUser(client, data['owner']['name'])
        
        exp = user.find_one({'exp_name': repo_name})
        if not exp:
            print 'adding new experiment '+repo_name+'...'
            user.insert({'exp_name': repo_name, 'exp_records':[]})
            
            
        old_records = user.find_one({'exp_name': repo_name})['exp_records']
        user.update({'exp_name': repo_name}, {'$set': {'exp_records': old_records + [branch]}})
        client.close()
        print "successfully"

        
    except Exception as e:
        if os.path.isdir(target + "/" + branch["commit"]["id"]):
            shutil.rmtree(target + "/" + branch["commit"]["id"])
        print e
        print e.args
        print "Aborting..." 
