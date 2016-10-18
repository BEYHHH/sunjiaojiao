#!/usr/bin/env python
# encoding: utf-8

"""
    This script is to run a backend service to
    handle http requests ( GET and POST ) from
    Gitlab server.
"""

import web
import os
import json
import threading as thd

urls = (
        '/', 'index'
        )

block = {}
lock = thd.RLock()

class index:
    def GET(self):
        return "This is LSEMS."
    def POST(self):
        global block
        data = json.loads(web.data())
        print data
        name = data['user_name']
        flag = False

        # if commit is no run, system do not run
        no_run = False
        for commit in data['commits']:
            if "no run" in commit['message']:
                no_run = True
        if no_run:
            return "Done."
        os.system("python exp.py -i '%s' &" %json.dumps(data))
        return "Done."

class MyApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    config = json.load(open(os.environ.get("HOME") + '/sandbox/config.json'))
    app.run(port = config['hook_port'])
