#-*- coding:utf-8 -*-
#!/usr/bin/env python
# encoding: utf-8

"""
    This script is to run a new process
    for one run of experiment.
"""

import json
import os
from optparse import OptionParser
import re
import run

def exp(data):
    print data
    repo_url = data['repository']['url'].split('/')[-1]
    print repo_url
    repo_url = "http://10.1.0.192/root/" + repo_url
    repo_name = re.split('/', data['repository']['homepage'])[-1:][0]
    print "current dir: "+os.getcwd()
    os.chdir('repos')
    if repo_name in os.listdir('.'):
        print("found repo existing.")
        os.system("rm -r -f "+ repo_name)
        print("deleted.")
    print(repo_url)
    os.system("git clone "+ repo_url)
    os.chdir(repo_name)
    file_names = os.listdir('.')
    try:
        if 'exp.json' not in file_names:
            raise Exception("Cannot find file exp.json!\nAborting...")
        run.read('exp.json',
                {"commit_id": data['commits'][0]['id'],
                'repo_name': data['repository']['name'],
                'name': data['user_name'] },)
    except Exception as e:
        print e.message
        os.chdir('../..')

def parse_args():
    
    """
    to get the commit information from the command line
    """
    parser = OptionParser(usage="test usage", add_help_option=False)
    parser.add_option("-h", "--help", action="help",
                      help="Show this help message and exit")
    parser.add_option("-i", "--input", help="input string")

    (opts, args) = parser.parse_args()
    return opts


def main():

    print '\033[1;32m'
    print "start"
    print '\033[0m'

    opts = parse_args()
    data = json.loads(opts.input)
    exp(data)

    print '\033[1;31m'
    print "end"
    print '\033[0m'

if __name__ == "__main__":
    main()
