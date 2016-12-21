#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    This script is to record matadata of user's experiment info including
    parameters and scripts in order to run experiment.
"""

import pymongo
from time import asctime
import json
import os
import re
import csv
import db_connect
import multiprocessing
import time
import pexpect


target = "/home/ubuntu/workspace/Push_exp"
clone_path = "/home/ubuntu/workspace/clone_file"

def run(username,clone_repo,commit_id,src):

    print username,clone_repo,commit_id,src
    print "the exp begin to run"
    try:
        List = db_connect.get_poject_exp_list(username,clone_repo)
    except:
        print "there is something wrong with the connect mangodb"
    for a in List["exp_records"]:
        if a["commit"]["id"] == commit_id:
            exp = a
            a["has_run"] = True
    try:
        print "src",src
        OK = db_connect.update_exp(username,clone_repo,List["exp_records"])
        print OK
        p = multiprocessing.Process(target = run_the_code,args = (username,commit_id,clone_repo,src,))
        p.start()
        return True
    except:
        print e
        print "Aborting...,there is something wrong with catch the correct code. the multiprocess can not run correctly"
        return False,{}


def run_the_code(username,commit_id,clone_repo,src_code):
    target = "/home/ubuntu/workspace/Push_exp/" + commit_id + "/" +clone_repo
    print target
    
    
    
    
    if os.path.isdir(target):
        print "enter successfully"
        os.chdir(target)
        if  src_code[src_code.rfind('.'):] == ".java":
            cmd = "javac %s"%(src_code)
            os.system(cmd)
            
            cmd = "java %s"%(src_code[:src_code.rfind('.')])
            c = pexpect.run(cmd)
        else:
            c = pexpect.run("python  " + src_code)
        print "result :",c
        List = db_connect.get_poject_exp_list(username,clone_repo)
        for a in List["exp_records"]:
            if a["commit"]["id"] == commit_id:
                exp = a
                a["is_run"] = True
                a["return"] = c
        OK = db_connect.update_exp(username,clone_repo,List["exp_records"])
        print "succefully end"
        shell = "python  /home/ubuntu/workspace/data_set_public/autograder.py    --commit  %s  --repo  %s  " % (commit_id,clone_repo)
        os.system(shell)
        return True
        raise Exception("can not run the exp code successfully")

    else:
        return False



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

def checkKeys(dict, ks):
    missing = []
    for k in ks:
        if k not in dict.keys():
            missing += [k]
    return missing

def random_commit_id():
    from random import randint
    r = randint(0,56**10)
    rtn = ""
    for i in range(0,10):
        ri = r % 56
        r /= 56
        if ri+48>57: ri+=7
        if ri+48>90: ri+=6
        rtn += chr(ri+48)
    return rtn

def record(params, git_info = {}):
    """
        this functions takes in a dictionary as parameters
        and record it in the MongoDB before run it.
    """
    print "recording..."

    try:
        # connect to MongoDB
        config = json.load(open(os.environ.get('HOME') + "/sandbox/config.json"))
        try:
            client = pymongo.MongoClient(config["mongodb_url"])
        except Exception as e:
            raise Exception("fail to connect to given MongoDB")

        # check and run the thing
        missing = checkKeys(params, ['data_set', 'src', 'type'])
        if len(missing) != 0:
            raise Exception("missing attribute"+('s' if len(missing)!=1 else '')+": "+str(missing))

        params['time'] = asctime()
        params['commit_id'] = git_info['commit_id']
        params['name'] = git_info['name']
        repo_name = git_info['repo_name']
        params['repo_name'] = repo_name
        user = verifyUser(client, git_info['name'])

        exp = user.find_one({'exp_name': repo_name})
        if not exp:
            print 'adding new experiment '+repo_name+'...'
            user.insert({'exp_name': repo_name, 'exp_records':[]})
        old_records = user.find_one({'exp_name': repo_name})['exp_records']
        user.update({'exp_name': repo_name}, {'$set': {'exp_records': old_records + [params]}})

        #user.insert(params)
        client.close()
        return True, params
    except Exception as e:
        print e
        print "Aborting..."
        return False,{}
"""
def run(params):
    print "running"
    try:
        old_dir = os.getcwd()
        tmp = re.split('/', old_dir)
        if params['name'].lower() not in os.listdir('/user_data'):
            raise Exception("user not in Datahub.")
        sb_dir = "/user_data/%s/%s" %(params['name'].lower(), params['repo_name'].lower())
        src = params['src']
        code_files = os.listdir('src')
        if src not in code_files:
            raise Exception("fail to find source file " + src)
        os.system("cp src/* %s" % sb_dir)
        os.chdir(sb_dir)
        command = ""
        if params['type'] == "python":
            command += "python " + src
        print command
        os.system(command)
        print "deleting code files..."
        for ele in code_files:
            os.system("rm %s" % (ele))
        record_name = "record_%s_%s.csv" % (asctime().replace(' ', '-').replace(':', '-'), params["commit_id"])
        f = csv.writer(open(record_name, 'wb+'))
        f.writerow(["parameters", "value"])
        for key, value in params.items():
            f.writerow([str(key), str(value)])
    except Exception as e:
        print e
        print e.args
        print "Aborting..."
    print "finished!"
    os.chdir(old_dir)
"""

def read(file_name, git_info):
    print "current dir: "+os.getcwd()
    fp = open(file_name)
    params = json.load(fp)
    flag, p = record(params, git_info)
    if flag:
        run(p)

def main():
    print("json file as input: ")
    file_name = raw_input()
    read(file_name, {'commit_id':random_commit_id()+random_commit_id()})

if __name__ == "__main__":
    main()
