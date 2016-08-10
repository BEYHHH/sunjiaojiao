#!/usr/bin/env python
# encoding: utf-8

import json
import os
import pymongo
import pandas as pd

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

def get_history_records(user_name, repo_name):
    try:
        config = json.load(open(os.environ.get('HOME') + "/sandbox/config.json"))
        try:
            client = pymongo.MongoClient(config["mongodb_url"])
        except Exception as e:
            raise Exception("fail to connect to given MongoDB")

        user = verifyUser(client, user_name)
        exp = user.find_one({"exp_name": repo_name})
        records = exp["exp_records"]
        df = pd.DataFrame(records)
        return df
    except Exception as e:
        print e
        print "Aborting"

if __name__ == "__main__":
    df = get_history_records("Administrator", "titanic")
    df.to_csv("hist.csv")
