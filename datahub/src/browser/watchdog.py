import os
import datetime
import pyinotify
import logging
import pexpect
import time

class MyEventHandler(pyinotify.ProcessEvent):
    logging.basicConfig(level=logging.INFO,filename='/var/log/monitor.log')
    logging.info("Starting monitor...")
    repo_path = ""
    
    def set_target(self,repo_path):
        self.repo_path = repo_path
        
    def process_IN_ACCESS(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        print "ACCESS event:", event.pathname
        logging.info("ACCESS event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_ATTRIB(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        print "ATTRIB event:", event.pathname
        logging.info("IN_ATTRIB event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CLOSE_NOWRITE(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        print "CLOSE_NOWRITE event:", event.pathname
        logging.info("CLOSE_NOWRITE event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CLOSE_WRITE(self, event):
        
        target_path = self.repo_path
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        if "~" in a[a.rfind('/'):] and a[a.rfind('/'):][1] == ".":
            return
        
        
        time.sleep(0.1)
        if os.path.isdir(target_path):
            os.chdir(target_path)
            if True:
                os.system("git add .")
                print "process_IN_CLOSE_WRITE commit something"    
                b = pexpect.spawn("git commit -a -m \"update the time\"")
                index = b.expect(['nothing to commit','update','file changed','files changed','deletion','Your branch is ahead of \'origin/master\' by',pexpect.TIMEOUT])
                print "the change in the ",index
                if index == 1 or index == 2 or index == 3 or index == 4 or index == 5:
                    branch_name = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
                    os.system("git branch  " +  branch_name)
                    c = pexpect.spawn("git push origin " + branch_name)  
                    c.expect(".*Username for")
                    c.sendline("root")
                    c.expect(".*Password for ")
                    c.sendline("git123456")
                    c.interact()
                
                    d = pexpect.spawn("git push ")
                    d.expect(".*Username for")
                    d.sendline("root")
                    d.expect(".*Password for ")
                    d.sendline("git123456")
                    d.interact()
                
                    print "push successfully"
            #except Exception,ex:  
                #return "the file over"
        
        print "CLOSE_WRITE event:", event.pathname
        logging.info("CLOSE_WRITE event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_CREATE(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        if "~" in a[a.rfind('/'):] and a[a.rfind('/'):][1] == ".":
            return
        
        print "CREATE event:", event.pathname
        logging.info("CREATE event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
        
        
        time.sleep(0.1)
        target_path = self.repo_path
        if os.path.isdir(target_path):
            os.chdir(target_path)
            if True:
                os.system("git add .")
                print "process_IN_CREATE commit something"    
                b = pexpect.spawn("git commit -a -m \"update the time\"")
                index = b.expect(['nothing to commit','update','file changed','files changed','deletion','Your branch is ahead of \'origin/master\' by',pexpect.TIMEOUT])
                print "the change in the ",index
                if index == 1 or index == 2 or index == 3 or index == 4 or index == 5:
                    branch_name = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
                    os.system("git branch  " +  branch_name)
                    
                    c = pexpect.spawn("git push origin " + branch_name)
                    c.expect(".*Username for")
                    c.sendline("root")
                    c.expect(".*Password for ")
                    c.sendline("git123456")
                    c.interact()
                    
                    d = pexpect.spawn("git push ")
                    d.expect(".*Username for")
                    d.sendline("root")
                    d.expect(".*Password for ")
                    d.sendline("git123456")
                    d.interact()
                    print "push successfully"
            else: 
                return "the file over"
        
        
     
    def process_IN_DELETE(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        if "~" in a[a.rfind('/'):] and a[a.rfind('/'):][1] == ".":
            return
        
        
        time.sleep(0.1)
        target_path = self.repo_path
        if os.path.isdir(target_path):
            os.chdir(target_path)
            if True:
                os.system("git add .")
                b = pexpect.spawn("git commit -a -m \"update the time\"")
                index = b.expect(['nothing to commit','update','file changed','files changed','deletion','Your branch is ahead of \'origin/master\' by',pexpect.TIMEOUT])
                print "the change in the ",index
                if index == 1 or index == 2 or index == 3 or index == 4 or index == 5:
                    branch_name = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
                    os.system("git branch  " +  branch_name)
                    
                    c = pexpect.spawn("git push origin " + branch_name)
                    
                    c.expect(".*Username for")
                    c.sendline("root")
                    c.expect(".*Password for ")
                    c.sendline("git123456")
                    c.interact()
                    
                    
                    d = pexpect.spawn("git push ")
                    d.expect(".*Username for")
                    d.sendline("root")
                    d.expect(".*Password for ")
                    d.sendline("git123456")
                    d.interact()
                    
                    print "push successfully"
            else: 
                return "the file over"
            
        print "DELETE event:", event.pathname
        logging.info("DELETE event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_MODIFY(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        print "MODIFY event:", event.pathname
        logging.info("MODIFY event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
     
    def process_IN_OPEN(self, event):
        a = event.pathname
        if not a[a.rfind('.'):] == ".py" and not a[a.rfind('.'):] == ".ipynb" and not a[a.rfind('.'):] ==".json":
            return
        
        print "OPEN event:", event.pathname
        logging.info("OPEN event : %s  %s" % (os.path.join(event.path,event.name),datetime.datetime.now()))
        
        
def update_every(username,repo):
    clone_name = get_clone_name(username,repo)
    target_path = "/home/ubuntu/workspace/clone_file/" + clone_name
    
    wm = pyinotify.WatchManager()
    wm.add_watch(target_path, pyinotify.ALL_EVENTS, rec=True)
    eh = MyEventHandler()
    eh.set_target(target_path)
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()    
        
def get_clone_name(username,repo):
    return repo        


def get_current_branch(username,repo):
    name = get_branch(username,repo)
    return name["name"]
    
    
def get_branch(username,repo):
    
    """
    to get the present branch infromation of a project
    """
    clone_name = get_clone_name(username,repo)
    
    target_path = "/home/ubuntu/workspace/clone_file/" + clone_name
    
    if os.path.isdir(target_path):
        os.chdir(target_path)
        ID = get_project_id(username,repo)
        Post_shell = commal_url + "projects/" + str(ID) + "/repository/branches\""
        a = pexpect.run(Post_shell)
        branch_list = json.loads(a)
        c = pexpect.run("git status")
        #print branch_list
        N = None
        for commit in branch_list:
            if "On branch " + commit["name"] in c:
                for a in commit:
                    print a, " : ",commit[a]
                return commit
        raise Exception("can not get the present branch in the project")
        
        
        
        
def get_project_id(username,repo):
    """
    to get the id of a project in the datalab
    """
    clone_name = get_clone_name(username,repo)
    shell ="curl --header  \"PRIVATE-TOKEN:1oji-cDx8Yi5yyPxFjzk\"  -u \"root:git123456\"  \"http://10.2.1.128:8888/api/v3/projects\""
    
    shell = commal_url + "projects\""
    print shell
    
    a = pexpect.run(shell)
    s = json.loads(a)
    
    for detial in s:
        if detial["name"] == clone_name:
            return detial["id"]         
    raise Exception("can't get the id")

if __name__ == '__main__':
    """
    for the test 
    """
    update_every("","")

