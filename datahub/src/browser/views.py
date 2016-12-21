# -*- coding: utf-8 -*-
import json
import urllib
import uuid
import hashlib
import pexpect
import os
import shutil
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import time
import multiprocessing
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core import serializers
import random
from django.http import HttpResponse, \
    HttpResponseRedirect, \
    HttpResponseForbidden, \
    HttpResponseNotAllowed
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from thrift.protocol import TBinaryProtocol
from thrift.protocol import TJSONProtocol
from thrift.transport.TTransport import TMemoryBuffer


from config import settings
from oauth2_provider.models import get_application_model
from oauth2_provider.views import ApplicationUpdate
from inventory.models import App, Annotation
from account.utils import grant_app_permission
from core.db.manager import DataHubManager
from core.db.rlsmanager import RowLevelSecurityManager
from core.db.rls_permissions import RLSPermissionsParser
from datahub import DataHub
from datahub.account import AccountService
from service.handler import DataHubHandler
from utils import post_or_get
from django.views.decorators.csrf import csrf_protect
from watchdog import update_every
import watchdog

from datalab import *
'''
Datahub Web Handler
'''
###add by beyhhhh
import csv


handler = DataHubHandler()
core_processor = DataHub.Processor(handler)
account_processor = AccountService.Processor(handler)



#gitlab_url = "10.2.0.112"
gitlab_url = "172.20.2.17"
hearder = "--header \"PRIVATE-TOKEN:L4414iPPE3zknxmk7xQ8\" "
user_id_pass = " -u \"root:git123456\" "
api_url = " \"http://" + gitlab_url + "/api/v3/"

hook_shell = " -d \"url=http://10.1.0.195:1234\""
commal_url = "curl " + hearder + user_id_pass + api_url

git_url = "http://" + gitlab_url + "/root/"



clone_file_path = "/home/ubuntu/workspace/clone_file"
public_code = "/home/ubuntu/workspace/code_public"
public_data = "/home/ubuntu/workspace/data_set_public"

def get_clone_name(username,repo):
    if username == "likeqiang":
        return repo
    if username == "zjsxzyuser":
        return repo
    clone_name = "%s_%s" % (repo.lower(),username.lower())
    return clone_name

def get_projec_path(username,clone_name):
    return "/home/%s/%s" % (username,clone_name)


def get_user_path(username):
    return "/home/%s" % (username)


thread_list = {}
####add by beyhhhh>>>
def get_project_config(username,clone_name):
    return  "%s/%s" % (get_projec_path(username,clone_name),"config")

def get_project_param(username,clone_name):
    return "%s/%s" % (get_projec_path(username,clone_name),"parem")


def get_the_json(target_path):
    f = open(target_path)
    dic = json.load(f)

def write_the_json(target_path,dic):
    with open(target_path,'w') as f:
        f.write(json.dumps(dic, indent=2, ensure_ascii=False))

"""
>>>git project section  begine<<<

the def in this section is
to do some action about the repo
get the project  id, commit, branch and so on



def get_present_commit(username,clone_name):
    target_path = get_projec_path(username,clone_name)
    if os.path.isdir(target_path):
        os.chdir(target_path)

        ID = get_project_id(username,clone_name)

        c = pexpect.run("git status")

        Post_shell = commal_url + "projects/" + str(ID) + "/repository/branches\""
        a = pexpect.run(Post_shell)
        branch_list = json.loads(a)
        N = None
        print "find the commit id"
        for commit in branch_list:
            if "On branch " + commit["name"] in c:
                N = commit["name"]
                commit["position"] = True
                return commit["commit"]["id"]
            else:
                commit["position"] = False

        return branch_list[0]["commit"]["id"]


"""

def get_project_id(username,clone_name):
    '''
    to get the id of a project in the datalab
    '''
    project_dic = get_project(username,clone_name)
    return(project_dic["id"])
    raise Exception("can't get the id")


def get_project(username,clone_name):
    '''
    to get the project by the dic
    '''
    shell = commal_url + "projects/search/" + clone_name + " \""
    print 'get_project ,return a project json    ',shell

    a = pexpect.run(shell)
    s = json.loads(a)

    for detial in s:
        if detial["name"] == clone_name:
            return detial
    raise Exception("can't get the project")

def get_branch(username,clone_name):

    '''
    to get the present branch infromation of a project
    '''
    print "get_branch function "
    target_path = get_projec_path(username,clone_name)
    '''
    shut_down_watchdog_system(user_name,clone_name)
    '''
    if os.path.isdir(target_path):
        os.chdir(target_path)
        ID = get_project_id(username,clone_name)
        Post_shell = commal_url + "projects/" + str(ID) + "/repository/branches\""
        a = pexpect.run(Post_shell)
        branch_list = json.loads(a)
        c = pexpect.run("git status")
        '''
        res_start_watchdog_system(user_name,clone_name)
        '''
        N = None
        for commit in branch_list:
            if "On branch " + commit["name"] in c:
                return commit
        raise Exception("can not get the present branch in the project")

def get_commit(username,clone_name):
    branch = get_branch(username,clone_name)

    commit_list = get_commit_list(username,clone_name)
    for commit in commit_list:
        if commit["id"] == branch["commit"]["id"]:
            return commit

    ID = get_project_id(username,clone_name)
    Post_shell = commal_url + "projects/" + str(ID) + "/repository/commits/" + branch["commit"]["id"]+ "\""
    a = pexpect.run(Post_shell)
    commit = json.loads(a)
    return commit
    raise Exception("fail to get the present commit in the project")



def get_commit_list(username,clone_name):
    '''
    to list the commit of a certain project
    '''

    ID = get_project_id(username,clone_name)

    Post_shell = commal_url + "projects/" + str(ID) + "/repository/commits\""
    a = pexpect.run(Post_shell)

    commit_list = json.loads(a)
    print "get the commit id list successfully"
    return commit_list



"""
watch dog a system to get the every changes by user


def shut_down_watchdog_system(username,clone_name):
    if thread_list.has_key(clone_name):
        print "the Key is exits"
        if thread_list[clone_name] and thread_list[clone_name].is_alive():
            thread_list[clone_name].terminate()
    return True

def res_start_watchdog_system(username,clone_name):
    if not thread_list.has_key(clone_name) or not thread_list[clone_name].is_alive():
        thread_list[clone_name] = multiprocessing.Process(target = update_every,args = (username,repo,))
        thread_list[clone_name].daemon = True
        thread_list[clone_name].start()
    return True

"""



def action_record(username,clone_name,action):
    #return

    TIME = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
    data = [(username,clone_name,TIME,action)]
    csvfile  = open("%s/record.csv"% (clone_file_path),"a+")
    writer = csv.writer(csvfile)
    writer.writerows(data)
    csvfile.close()

####<<<add by beyhhhh

def home(request):
    username = request.user.get_username()
    if username:
        return HttpResponseRedirect(reverse('browser-user', args=(username,)))
    else:
        return HttpResponseRedirect(reverse('www:index'))


def about(request):
    return HttpResponseRedirect(reverse('www:index'))



@csrf_exempt
def service_core_binary(request):
        # Catch CORS preflight requests
    if request.method == 'OPTIONS':
        resp = HttpResponse('')
        resp['Content-Type'] = 'text/plain charset=UTF-8'
        resp['Content-Length'] = 0
        resp.status_code = 204
    else:
        try:
            iprot = TBinaryProtocol.TBinaryProtocol(
                TMemoryBuffer(request.body))
            oprot = TBinaryProtocol.TBinaryProtocol(TMemoryBuffer())
            core_processor.process(iprot, oprot)
            resp = HttpResponse(oprot.trans.getvalue())

        except Exception as e:
            resp = HttpResponse(
                json.dumps({'error': str(e)}, indent=2),
                content_type="application/json")
    try:
        resp['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
    except:
        pass
    resp['Access-Control-Allow-Methods'] = "POST, PUT, GET, DELETE, OPTIONS"
    resp['Access-Control-Allow-Credentials'] = "true"
    resp['Access-Control-Allow-Headers'] = ("Authorization, Cache-Control, "
                                            "If-Modified-Since, Content-Type")

    return resp


@csrf_exempt
def service_account_binary(request):
    # Catch CORS preflight requests
    if request.method == 'OPTIONS':
        resp = HttpResponse('')
        resp['Content-Type'] = 'text/plain charset=UTF-8'
        resp['Content-Length'] = 0
        resp.status_code = 204
    else:
        try:
            iprot = TBinaryProtocol.TBinaryProtocol(
                TMemoryBuffer(request.body))
            oprot = TBinaryProtocol.TBinaryProtocol(TMemoryBuffer())
            account_processor.process(iprot, oprot)
            resp = HttpResponse(oprot.trans.getvalue())

        except Exception as e:
            resp = HttpResponse(
                json.dumps({'error': str(e)}, indent=2),
                content_type="application/json")

    try:
        resp['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
    except:
        pass
    resp['Access-Control-Allow-Methods'] = "POST, PUT, GET, DELETE, OPTIONS"
    resp['Access-Control-Allow-Credentials'] = "true"
    resp['Access-Control-Allow-Headers'] = ("Authorization, Cache-Control, "
                                            "If-Modified-Since, Content-Type")

    return resp


@csrf_exempt
def service_core_json(request):
    # Catch CORS preflight requests
    if request.method == 'OPTIONS':
        resp = HttpResponse('')
        resp['Content-Type'] = 'text/plain charset=UTF-8'
        resp['Content-Length'] = 0
        resp.status_code = 204
    else:
        try:
            iprot = TJSONProtocol.TJSONProtocol(TMemoryBuffer(request.body))
            oprot = TJSONProtocol.TJSONProtocol(TMemoryBuffer())
            core_processor.process(iprot, oprot)
            resp = HttpResponse(
                oprot.trans.getvalue(),
                content_type="application/json")

        except Exception as e:
            resp = HttpResponse(
                json.dumps({'error': str(e)}, indent=2),
                content_type="application/json")

    try:
        resp['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
    except:
        pass
    resp['Access-Control-Allow-Methods'] = "POST, PUT, GET, DELETE, OPTIONS"
    resp['Access-Control-Allow-Credentials'] = "true"
    resp['Access-Control-Allow-Headers'] = ("Authorization, Cache-Control, "
                                            "If-Modified-Since, Content-Type")

    return resp


####add by beyhhhh>>>>
def move_code_to_repo(request, repo_base, repo):

    """
    move the code in the public to a private repo
    and if no code was selected we return a warning
    and we will git push the data at the same time

    add the code in the public will updata it information
    for it may slove more datasets
    """
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)

    action_record(username,clone_name,"move_the_public_codes_to_project")

    code_list =  request.POST.getlist('check_box_list')
    ran = random.randint(0, 1)
    for c in range(0,len(code_list)):
        if code_list[c] == 'e621bfc2f2292c4e3f903517111361ffed868cd2_Titanic_Tutorial.ipynb':
            if ran == 0:
                code_list[c] = 'f7c59407eafdf65aa57520da0ecf4cda9881e194_Titanic_Tutorial.ipynb'
                f = open(public_code + "/record.txt", "a" )
                TM = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
                f.write('username:%s  project:%s\n move_time:%s  \nf7c59407eafdf65aa57520da0ecf4cda9881e194_Titanic_Tutorial.ipynb\n' % (username,clone_name,TM))
                f.close()


    path = public_code + "/"
    target = get_projec_path(username,clone_name) + "/"
    with DataHubManager(user=username, repo_base=repo_base) as manager:
            data_list = manager.repo_data_list(username,clone_name)


    if len(code_list) > 0:
        for a in code_list:
            code_name = ""
            if os.path.isfile(path +"json/"+ a +".json"):
                f = open(path +"json/"+ a +".json")
                dic = json.load(f)
                code_name = dic["name"]
                for data_set_in_repo in data_list:
                    C = True
                    for data_set_match_code in dic["data_set"]:
                        if data_set_match_code == data_set_in_repo:
                            C = False
                    if C:
                        dic["data_set"].append(data_set_in_repo)
                with open(path +"json/"+ a +".json", "w") as f:
                    f.write(json.dumps(dic, indent=2))

            if os.path.isfile(path + "public_code/" + a):
                print "move the public code to target"
                shutil.copyfile(path + "public_code/" + a ,target + code_name)
                #shutil.copyfile(path +"json/"+ a + ".json",target + a + ".json")


    return HttpResponseRedirect("/browse/" + username + "/" + repo + "/")


def move_data_to_repo(request, repo_base, repo):
    username = request.user.get_username()
    data_list = request.POST.getlist('check_box_list')
    clone_name = get_clone_name(username,repo)
    path =public_data + "/json"
    target = get_project_config(username,clone_name)

    action_record(username,clone_name,"move_the_public_datas_to_project")

    if os.path.isfile(target):
        f = open(target)
        repo_dic = json.load(f)
        for a in data_list:
            if os.path.isfile(path + "/" + a + ".json"):
                f = open(path + "/" + a + ".json")
                data_dic = json.load(f)

                repo_dic[u"date_set"][data_dic["id"]] = data_dic
        with open(target,"w") as w:
            w.write(json.dumps(repo_dic, indent=2, ensure_ascii=False).encode('utf8'))

    return HttpResponseRedirect("/browse/" + username + "/" + repo + "/")



def public_data_set(request,repo_base = None):

    """
    show the public in the public data set and the visitor could also
    watch the public data sets
    """
    username = request.user.get_username()
    public_repos = DataHubManager.list_public_repos()


    repos = None
    if username != '':
        if not repo_base:
            repo_base = username
        with DataHubManager(user=username, repo_base=repo_base) as manager:
            repos = manager.list_repos()


    date_path = public_data + "/json"

    data_sets ={}

    if os.path.isdir(date_path):
        data_list = os.listdir(date_path)
        for a in data_list:
            if os.path.isfile(date_path + "/" + a):
                f = open(date_path + "/" + a)
                dic = json.load(f)
                if dic["public"]:
                    kind = dic["class"]
                    if data_sets.has_key(kind):
                        data_sets[kind].append(dic)
                    else:
                        data_sets[kind] = []
                        data_sets[kind].append(dic)


    data_list = []
    for a in data_sets:
        data_list.append({"name":a,"List":[ data for data in data_sets[a] ]})

    res = {
        'login': username,
        'repo_base': 'repo_base',
        'repos': repos,
        'data_list': data_list,
    }

    res.update(csrf(request))
    return render_to_response("repo-browse-data-sets.html",res)

def add_datas_to_repo(request, repo_base, repo):
    """
    to make the window show the datas that in the public data_set
    and user could select the data_sets it wants add to the certain project
    """
    username = request.user.get_username()
    public_repos = DataHubManager.list_public_repos()
    clone_name = get_clone_name(username,repo)
    action_record(username,clone_name,"enter_the_public_datas_label")

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        repos = manager.list_repos()

    basic_path = public_data + "/data_set_public"
    #### it has been delect something

    date_path = public_data + "/json"

    data_sets ={}

    if os.path.isdir(date_path):
        data_list = os.listdir(date_path)
        for a in data_list:
            if os.path.isfile(date_path + "/" + a):
                f = open(date_path + "/" + a)
                dic = json.load(f)
                if dic["public"]:
                    kind = dic["class"]
                    if data_sets.has_key(kind):
                        data_sets[kind].append(dic)
                    else:
                        data_sets[kind] = []
                        data_sets[kind].append(dic)


    data_list = []
    for a in data_sets:
        data_list.append({"name":a,"List":[ data for data in data_sets[a] ]})

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'data_list':data_list,
    }
    res.update(csrf(request))
    return render_to_response("repo-browse-add-data.html",res)


def add_codes_to_repo(request, repo_base, repo):
    """
    we add the def at the twice changes

    the windows to add some codes to the repo
    to manage
    """
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    clone_name = get_clone_name(username,repo)

    action_record(username,clone_name,"enter_the_public_codes_label")

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        Data_list = manager.repo_data_list(username,clone_name)
        ### to get the cvs that the repo has, so we can select the codes that have someting to do with the cvs
        ### get the codes in the public, include the name details and the cvs that it sloved before

    public_code_list = get_public_code_list()

    general_codes = []
    special_codes = []
    other_codes = []

    for a in public_code_list:
        OK = True
        if len(a["data_set"]) == 0:
            general_codes.append(a)
            continue

        for c in a["data_set"]:
            for d in Data_list:
                if d == c:
                    special_codes.append(a)
                    OK = False
                    break
            if not OK:
                break
        if OK:
            other_codes.append(a)


    res= {
        "login": username,
        "repo_base":repo_base,
        "repo":repo,
        "general_codes":general_codes,
        "special_codes":special_codes,
        "other_codes":other_codes,
        }

    res.update(csrf(request))
    return render_to_response("repo-browse-add-code.html",res)


def get_public_code_list():
    json_path =public_code + "/json"
    code_list = []
    if os.path.isdir(json_path):
        file_list = os.listdir(json_path)
        for a in file_list:
            if a == "f7c59407eafdf65aa57520da0ecf4cda9881e194_Titanic_Tutorial.ipynb.json":
                continue
            if os.path.isfile(json_path+ "/" + a):
                f = open(json_path+ "/" + a)
                code_list.append(json.load(f))
    return  code_list





def add_to_the_repo(request,repo_base):
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    data_list = request.POST.getlist('check_box_list')
    Repo = request.POST.getlist('repo')
    repo = Repo[0]
    clone_name = get_clone_name(username,repo)
    path = public_data + "/"
    target = get_projec_path(username,clone_name) + "/"

    if len(data_list) > 0:
        for a in data_list:
            if os.path.isfile(path + a):
                c = a.split('/')
                shutil.copyfile(path + a,target + c[1])
    return HttpResponseRedirect("/browse/" + username + "/" + repo)


####<<<<add by beyhhhh



'''
Repository Base
'''
#### the def may not used and we use the public data sets and public codes to relpace it.
def public(request):
    """
    browse public repos. Login not required
    """
    username = request.user.get_username()
    public_repos = DataHubManager.list_public_repos()



    # This should really go through the api... like everything else
    # in this file.
    public_repos = serializers.serialize('json', public_repos)

    return render_to_response("public-browse.html", {
        'login': username,
        'repo_base': 'repo_base',
        'repos': [],
        'public_repos': public_repos,
    })


def user(request, repo_base=None):
    username = request.user.get_username()

    if not repo_base:
        repo_base = username

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        repos = manager.list_repos()

    visible_repos = []
    public_role = settings.PUBLIC_ROLE

    for repo in repos:
        collaborators = manager.list_collaborators(repo)
        collaborators = [c.get('username') for c in collaborators]
        collaborators = filter(
            lambda x: x != '' and x != repo_base, collaborators)
        non_public_collaborators = filter(
            lambda x: x != public_role, collaborators)

        visible_repos.append({
            'name': repo,
            'owner': repo_base,
            'public': True if public_role in collaborators else False,
            'collaborators': non_public_collaborators,
        })

    collaborator_repos = manager.list_collaborator_repos()

    return render_to_response("user-browse.html", {
        'login': username,
        'repo_base': repo_base,
        'repos': visible_repos,
        'collaborator_repos': collaborator_repos})


'''
Repository
'''

@csrf_protect
def repo(request, repo_base, repo):
    '''
    forwards to repo_tables method
    list the Code and Date and Commit and Record and
    '''


    username = request.user.get_username()

    right = {}
    if username == 'zhangyang_2014311425' or 'ztj':
        right['code_public'] = True
        right['data_public'] = True
    clone_name =  get_clone_name(username,repo)
    if repo_base.lower() == 'user':
        repo_base = username


    os.system("sudo chown -R %s:%s  %s" %  (username,username,get_user_path(username)))

    action_record(username,clone_name,"enter_the_project")

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        Data_list = manager.repo_data_list(username,clone_name)
        Code_list = manager.repo_code_list(username,clone_name)
        Conf_list = manager.repo_conf_list(username,clone_name)

    clone_name = get_clone_name(username,repo)


    data_set = {}
    for a in Data_list:
        if data_set.has_key(a["name"]):
            data_set[a["name"]].append(a)
        else:
            data_set[a["name"]] = [a]

    ####the thread to check the changes in the clone flord

    '''
    res_start_watchdog_system(user_name,clone_name)
    '''

    ####the record for push
    try:
    #if True:
        commit_list = {}
        commit_list = db_connect.get_poject_exp_list(username,clone_name)
        for commit in commit_list['exp_records']:
            if commit.has_key('return'):
                commit['return_html_show'] = manage_code_to_html(commit['return'])
    except:
        commit_list = {}

    cont = {
        "login": username,
        "repo_base":repo_base,
        "repo":repo,
        "data_set":data_set,
        "Code_list":Code_list,
        "Conf_list":Conf_list,
        "commit_list":commit_list,
        "right":right
        }

    cont.update(csrf(request))
    return render_to_response("repo-browse-project-information.html", cont)


def manage_code_to_html(code):
    c = ''
    for a in code:
        if a == '\n':
            c = c + '<br>'
        else:
            c = c + a
    return c
####it was useless >>>>

def repo_tables(request, repo_base, repo):
    '''
    shows the tables under a repo.
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    '''
    get the base tables and views of the user's repo
    '''
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        base_tables = manager.list_tables(repo)
        views = manager.list_views(repo)

    rls_table = 'policy'

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'base_tables': base_tables,
        'views': views,
        'rls-table': rls_table
    }

    res.update(csrf(request))
    return render_to_response("repo-browse-tables.html", res)

"""
def repo_files(request, repo_base, repo):
    '''
    shows thee files in a repo
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    '''
    beyhhhh do some changes to classify the CSV files
    '''

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        files = manager.list_repo_files(repo)
    data_list = []
    for a in files:
        if a[a.rfind('.'):] == ".csv":
            data_list.append(a)

    '''
    beyhhhh do some changes to classify the CSV files
    '''

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'files': data_list
    }

    res.update(csrf(request))
    return render_to_response("repo-browse-files.html", res)

#### add by beyhhhh>>>

def repo_codes(request, repo_base, repo):
    '''
    shows the codes in a repo
    it was useless
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        uploaded_files = manager.list_repo_files(repo)
        dataset_list = manager.list_selected_dataset(repo)

    code_list = []

    for a in uploaded_files:
        if a[a.rfind('.'):] == ".py":
            code_list.append(a)
            continue
        if a[a.rfind('.'):] == ".ipynb":
            code_list.append(a)
        if a[a.rfind('.'):] == ".json":
            code_list.append(a)

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'files': code_list,
        'dataset':dataset_list}
    res.update(csrf(request))
    return render_to_response("repo-browse-codes.html", res)





@csrf_protect
def data_code_list_update(request,repo_base,repo):
    '''
    list the codes and datas in the manage flord
    '''

    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        Data_list = manager.get_Data_list()
        Code_list = manager.get_Code_list()

    cont = {
        "login": username,
        "repo_base":repo_base,
        "repo":repo,
        "Data_list":Data_list,
        "Code_list":Code_list
        }
    return render_to_response("data_code_list_update.html", cont,context_instance=RequestContext(request))




@csrf_protect
def update_file_flord_codes_data(request,repo_base,repo):
    '''
    updata the data and codes in the manage flord
    in the repo flord
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    List = request.POST.getlist('check_box_list')
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.updata_user_repo(repo,List)

    return HttpResponseRedirect("/browse/" + username + "/" + repo + "/data_code_list_update")


"""
@csrf_protect
def upload_github(request, repo_base, repo):
    '''
    push the code to the github
    '''
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)

    action_record(username,clone_name,"Push_project_upload_github")

    if repo_base.lower() == 'user':
        repo_base = username

    watchdog.update_project(get_projec_path(username,clone_name))
    branch = get_branch(username,clone_name)
    project = get_project(username,clone_name)
    data = project

    Push_Code.__Push__(username,clone_name,data,branch)
    return HttpResponseRedirect('/browse/'+ username + '/' + repo)
"""
@csrf_protect
def creat_new_data_sets(request,repo_base,repo):
    '''
    to copy the data_sets from file flord to the manage flord
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    List = request.POST.getlist('check_box_list')
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        uploaded_files = manager.list_repo_files(repo)

        address = manager.move_files(repo,List,True)
    return HttpResponseRedirect('/browse/'+ username + '/' + repo + '/codes')

@csrf_protect
def creat_new_codes(request,repo_base,repo):
    '''
    to copy the codes from files flord to the manage flord
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username
    List = request.POST.getlist('check_box_list')
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        uploaded_files = manager.list_repo_files(repo)
        address = manager.move_files(repo,List,False)
    return HttpResponseRedirect('http://10.1.0.195:8888/tree/sunjiaojiao/datahub'+ address)
    # return HttpResponseRedirect('/browse/'+ username + '/' + repo + '/data_code_list_update')




def data_code_list_update_github(request, repo_base, repo):
    '''
    to update the file from clone flord to the gitlab
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username


    with DataHubManager(user=username, repo_base=repo_base) as manager:
        List = manager.list_repo_files(repo)
    Data_list = []
    Code_list = []

    for a in List:
        if a[a.rfind('.'):] == ".csv":
            Data_list.append(a)
        if a[a.rfind('.'):] == ".py":
            Code_list.append(a)
        if a[a.rfind('.'):] == ".ipynb":
            Code_list.append(a)
        if a[a.rfind('.'):] == ".json":
            Code_list.append(a)
    rent = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        "Code_list": Code_list,
        "Data_list": Data_list,
        }

    return render_to_response("data_code_list_update_github.html", rent,context_instance=RequestContext(request))

### <<add by beyhhhh

def repo_cards(request, repo_base, repo):
    '''
    shows the cards in a repo
    '''
    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        cards = manager.list_repo_cards(repo)

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'cards': cards
    }

    res.update(csrf(request))
    return render_to_response("repo-browse-cards.html", res)
"""
#### <<<<it was useless

import json



###add by beyhhhh>>
def creat_github_repo(username,clone_name):
    """
    to creat a repo in the gatlab
    and so we can clone it in the local
    """
    shell = "curl  " + hearder + user_id_pass + api_url+ "projects\"" + " -d \"name=" + clone_name +"\"" + "   -d \"public=true\""

    print shell
    pexpect.run(shell)


def run_the_exp(request,repo_base,repo,commit_id,src):
    username = request.user.get_username()
    clone_name =  get_clone_name(username,repo)

    action_record(username,clone_name,"run_the_exp_get_the_result")
    try:
        run.run(username,clone_name,commit_id,src)
    except:
        print "the run has some problem in the function run.run in the datalab Run"
    return HttpResponseRedirect('/browse/'+ username + '/' + repo)



def reset_project_commit(request, repo_base,repo,short_id):
    '''
    reset the project commit ,to make it be the commit that user wanted
    '''
    username = request.user.get_username()
    clone_name =  get_clone_name(username,repo)
    '''
    shut_down_watchdog_system(username,clone_name)
    '''
    action_record(username,clone_name,"reset_to_"+short_id)
    target_path = get_projec_path(username,clone_name)
    if os.path.isdir(target_path):
        try:
            os.chdir(target_path)
            os.system("git checkout " + short_id)
            os.system("git add .")

            b = pexpect.spawn("git commit -a -m \"update the time\"")
            index = b.expect(['nothing to commit','file changed',pexpect.TIMEOUT])
            if index == 1:
                branch_name = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))
                os.system("git branch  " +  branch_name)
                c = pexpect.spawn("git push ")
                c.expect(".*Username for")
                c.sendline("root")
                c.expect(".*Password for ")
                c.sendline("git123456")
                c.interact()
        except Exception,ex:
            return "the file over"
    '''
    res_start_watchdog_system(username,clone_name)
    '''
    return HttpResponseRedirect('/browse/'+ username + '/' + repo)


def get_branch_code(username,repo,commit_id,P_id):
    '''
    get codes in the branch in the certain  commit
    '''

    clone_name =  get_clone_name(username,repo)
    target_path = get_projec_path(username,clone_name)
    if os.path.isdir(target_path):
        '''
        shut_down_watchdog_system(username,clone_name)
        '''
        os.chdir(target_path)
        os.system("git checkout " + commit_id)

        codes = os.listdir(target_path)

        code_list = []
        for a in codes:
            if a[a.rfind('.'):] == ".py":
                f = open( target_path + '/'+ a)
                code_list.append({"name":a ,"code": f.read()})
                f.close()
            if a[a.rfind('.'):] == ".java":
                f = open( target_path + '/'+ a)
                code_list.append({"name":a ,"code": f.read()})
                f.close()

            if a[a.rfind('.'):] == ".ipynb":
                f = open(target_path + '/' + a)
                code_list.append({"name":a ,"code": f.read()})
                f.close()
            if a[a.rfind('.'):] == ".json":
                f = open(target_path + '/' + a)
                code_list.append({"name":a ,"code": f.read()})
                f.close()

        os.system("git checkout " + P_id)
        '''
        res_start_watchdog_system(username,clone_name)
        '''
        return code_list



def commit_code_watch(request, repo_base,repo,branch_name):

    '''
    to list the codes in a certain commit(branch) project

    '''

    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)
    target_path = get_projec_path(username,clone_name)



    if os.path.isdir(target_path):
        os.chdir(target_path)
        ID = get_project_id(username,clone_name)

        c = pexpect.run("git status")

        Post_shell = commal_url + "projects/" + str(ID) + "/repository/branches\""
        a = pexpect.run(Post_shell)
        branch_list = json.loads(a)
        N = None
        for commit in branch_list:
            if "On branch " + commit["name"] in c:
                N = commit["name"]
            if commit["name"] == branch_name:
                branch = commit

        action_record(username,clone_name,"watch_the_branch"+branch["commit"]["id"])
        code_list = get_branch_code(username,clone_name,branch_name,N)

        ####get the information from the html
        res = {
            'login': username,
            'repo_base': repo_base,
            'repo': repo,
            'branch':branch,
            'code_list':code_list,
            }

    return render_to_response("repo-code_list.html", res)





def code_branch_list(request, repo_base,repo):
    """
    to list the branches in the project
    """
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)
    target_path = get_projec_path(username,clone_name)
    """
    shut_down_watchdog_system(user_name,clone_name)
    """

    action_record(username,clone_name,"watch_the_branch_list")

    if os.path.isdir(target_path):
        os.chdir(target_path)
        ID = get_project_id(username,clone_name)

        Post_shell = commal_url + "projects/" + str(ID) + "/repository/branches\""




        try:
            a = pexpect.run(Post_shell)
            branch_list = json.loads(a)

            c = pexpect.run("git status")
            N = None
            for commit in branch_list:
                if "On branch " + commit["name"] in c:
                    N = commit["name"]
                    commit["position"] = 0
                else:
                    commit["position"] = 1
        except:
            print "can't get the branch, Maybe no push in this project"


        res = {
            'login': username,
            'repo_base': repo_base,
            'repo': repo,
            'branch_list':branch_list,
            }
    """
    res_start_watchdog_system(user_name,clone_name)
    """

    return render_to_response("repo-branch_list.html", res)




def Make_data_set_public(request, repo_base, repo, file_id ):
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)
    json_path =  public_data + "/json"
    target_path = json_path + "/" + file_id + ".json"

    if os.path.isfile(target_path):
        f = open(target_path)
        dic = json.load(f)
        dic["public"] = True

        with open(target_path, "w") as f:
            f.write(json.dumps(dic, indent=2))

    return HttpResponseRedirect('/browse/'+ username + '/' + repo)

def Make_code_public(request, repo_base, repo, file_id):
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)


    commit = get_commit(username,clone_name)
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        Data_list = manager.repo_data_list(username,clone_name)
        Code_list = [file_id]
        move_code_to_public(username,repo,Code_list,Data_list,commit["id"])

        return HttpResponseRedirect('/browse/'+ username + '/' + repo)


###<<add by beyhhhh
@login_required
def repo_create(request, repo_base):
    '''
    creates a repo (POST), or returns a page for creating repos (GET)
    '''
    username = request.user.get_username()
    if username != repo_base:
        message = (
            'Error: Permission Denied. '
            '%s cannot create new repositories in %s.'
            % (username, repo_base)
        )
        return HttpResponseForbidden(message)

    if request.method == 'POST':
        repo = request.POST['repo']
        with DataHubManager(user=username, repo_base=repo_base) as manager:
            manager.create_repo(repo)

        ####add by beyhhhh>>

        ###to set the name in the gitlab
        clone_name = get_clone_name(username,repo)
        creat_github_repo(username,clone_name)
        clone_path = git_url+ clone_name +".git"

        action_record(username,clone_name,"creat_the_project")

        path = get_user_path(username)

        if os.path.isdir(path):
            if os.path.isdir(get_projec_path(username,clone_name)):
                os.shutil.rmtree(get_projec_path(username,clone_name))

            os.chdir(path)

            b = os.system("git clone  " + clone_path)

            if os.path.isdir(path + clone_name):
                os.chdir(path + clone_name)
                c = pexpect.spawn("git push origin master")
                c.expect(".*Username for")
                c.sendline("root")
                c.expect(".*Password for ")
                c.sendline("git123456")
                c.interact()



            repo_dict = {}
            repo_dict["repo_name"] = clone_name
            repo_dict["username"] = username
            repo_dict["date_set"] = {}
            repo_dict["creat_data"] = {}
            repo_dict["time"] = time.strftime("%Y_%m_%d_%H_%M_%S",time.localtime(time.time()))

            with open(get_project_config(username,clone_name), "w") as f:
                    f.write(json.dumps(repo_dict, indent=2, ensure_ascii=False).encode('utf8'))

            #param_dic = {}
            #with open(get_project_param(username,clone_name), "w") as f:
                    #f.write(json.dumps(param_dic, indent=2, ensure_ascii=False).encode('utf8'))

        ####<<add by beyhhhh
        ####add the multy process

        """
        res_start_watchdog_system(user_name,clone_name)
        """

        return HttpResponseRedirect('/browse/'+ username +'/')

    elif request.method == 'GET':
        res = {'repo_base': repo_base, 'login': username}
        res.update(csrf(request))
        return render_to_response("repo-create.html", res)


@login_required
def repo_delete(request, repo_base, repo):
    '''
    deletes a repo in the current database (repo_base)
    '''
    username = request.user.get_username()
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_repo(repo=repo, force=True)


    ### set the clone flord name
    clone_name = get_clone_name(username,repo)

    action_record(username,clone_name,"delect_the_project")

    path = get_user_path(username) + "/"
    if os.path.isdir(path + clone_name):
        shutil.rmtree(path + clone_name)
    else:
        print "the path isn't ok!" + path

    ID = get_project_id(username,clone_name)

    Post_shell ="curl  -X \"DELETE\" " + hearder + user_id_pass + api_url + "projects/" + str(ID) + "\""

    print Post_shell
    a = pexpect.run(Post_shell)
    return HttpResponseRedirect(reverse('browser-user-default'))

"""
###it was useless
@login_required
def repo_settings(request, repo_base, repo):
    '''
    returns the settings page for a repo.
    '''
    username = request.user.get_username()
    public_role = settings.PUBLIC_ROLE

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        collaborators = manager.list_collaborators(repo)

    # if the public role is in collaborators, note that it's already added
    repo_is_public = next(
        (True for c in collaborators if
            c['username'] == settings.PUBLIC_ROLE), False)

    # remove the current user, public user from the collaborator list
    # collaborators = [c.get('username') for c in collaborators]

    collaborators = [c for c in collaborators if c['username']
                     not in ['', username, settings.PUBLIC_ROLE]]

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'collaborators': collaborators,
        'public_role': public_role,
        'repo_is_public': repo_is_public}
    res.update(csrf(request))

    return render_to_response("repo-settings.html", res)


@login_required
def repo_collaborators_add(request, repo_base, repo):
    '''
    adds a user as a collaborator in a repo


    to make a repo public repo_public
    '''
    username = request.user.get_username()
    collaborator_username = request.POST['collaborator_username']
    db_privileges = request.POST.getlist('db_privileges')
    file_privileges = request.POST.getlist('file_privileges')

    ###change by beyhhhh>>>


    commit_id = get_present_commit(username,repo)

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.add_collaborator(
            repo, collaborator_username,
            db_privileges=db_privileges,
            file_privileges=file_privileges
        )
        Data_list = manager.repo_data_list(username,repo)
        Code_list = manager.repo_code_list(username,repo)
        move_code_to_public(username,repo,Code_list,Data_list,commit_id)

    ####<<<change by beyhhh
    return HttpResponseRedirect(
        reverse('browser-repo_settings', args=(repo_base, repo,)))
"""

#####add by beyhhhh>>>

def move_code_to_public(username,repo,code_list,data_list,commit_id):
    clone_name = get_clone_name(username,repo)

    json_path = public_code + "/json/"

    src_path = public_code + "/public_code/"

    path = get_projec_path(username,clone_name) +"/"


    if not os.path.isdir(src_path) or not os.path.isdir(json_path):
        return
    for code_l in code_list:
        code = code_l
        if os.path.isfile(path + code):
            shutil.copyfile(path + code,src_path + commit_id + "_" + code)
            dic = {"name":code,"repo":repo,"username" : username,"data_set":data_list, "commit_id":commit_id,"commit_name":commit_id + "_" + code}
            dic["short_commit_id"] = commit_id[0:11]

            with open(json_path + commit_id + "_" + code + '.json', 'w') as f:
                    f.write(json.dumps(dic, indent=2))



def Push_process(target_path):
     if os.path.isdir(target_path):
            os.chdir(target_path)
            os.system("git add .")

            d = pexpect.spawn("git commit -a -m " + "\" update\"")
            index = d.expect(['nothing to commit','file changed',pexpect.TIMEOUT])
            if index == 1 or index == 0:
                c = pexpect.spawn("git push")
                c.expect(".*Username for")
                c.sendline("root")
                c.expect(".*Password for")
                c.sendline("git123456")
                g = c.interact()
                return "Push Successfully"
            #if index == 0:
                #print "you have change nothing"
                #return "You have change nothing, have nothing to push"

            if index == 2:
                print "there is something wrong"
                return "there is something wrong"


#####<<<add by beyhhhh
"""
###it was useless
@login_required
def repo_collaborators_remove(request, repo_base, repo, collaborator_username):
    '''
    removes a user from a repo
    '''
    username = request.user.get_username()

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_collaborator(
            repo=repo, collaborator=collaborator_username)

    # if the user is removing someone else, return the repo-settings page.
    # otherwise, return the browse page
    if username == repo_base:
        return HttpResponseRedirect(
            reverse('browser-repo_settings', args=(repo_base, repo,)))
    else:
        return HttpResponseRedirect(reverse('browser-user-default'))


'''
Tables & Views
'''
"""

def table(request, repo_base, repo, table):
    '''
    return a page indicating how many
    '''
    current_page = 1
    if request.POST.get('page'):
        current_page = request.POST.get('page')

    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    url_path = reverse('browser-table', args=(repo_base, repo, table))

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        query = manager.select_table_query(repo, table)

        res = manager.paginate_query(
            query=query, current_page=current_page, rows_per_page=50)

    # get annotation to the table:
    annotation, created = Annotation.objects.get_or_create(url_path=url_path)
    annotation_text = annotation.annotation_text

    data = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'table': table,
        'annotation': annotation_text,
        'current_page': current_page,
        'next_page': current_page + 1,  # the template should relaly do this
        'prev_page': current_page - 1,  # the template should relaly do this
        'url_path': url_path,
        'column_names': res['column_names'],
        'tuples': res['rows'],
        'total_pages': res['total_pages'],
        'pages': range(res['start_page'], res['end_page'] + 1),  # template
        'num_rows': res['num_rows'],
        'time_cost': res['time_cost']
    }

    data.update(csrf(request))

    # and then, after everything, hand this off to table-browse. It turns out
    # that this is all using DataTables anyhow, so the template doesn't really
    # use all of the data we prepared. ARC 2016-01-04
    return render_to_response("table-browse.html", data)
####add by beyhhhh >>

def table_show(request, repo_base, repo, file_name):
    username = request.user.get_username()

    file_path = public_data + "/public_data/" + file_name
    with open(file_path,'rb') as f:
        reader = list(csv.reader(f))
        f.close()

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'data_name':file_name,
        'data':reader,
    }

    return render_to_response("repo-browse-data-shows.html", res)


def show_board(request):
    username = request.user.get_username()

    action_record(username,"no_project","Leader_Board")

    file_path = public_data + "/titanic_leader_board.csv"
    with open(file_path,'rb') as f:
        reader = list(csv.reader(f))
        f.close()

    res = {
        'login': username,
        'data_name':'Leader Board',
        'data':reader,
    }

    return render_to_response("repo-browse-data-shows.html", res)

def log_show(request):
    username = request.user.get_username()

    file_path = public_data + "/titanic_leader_board.csv"
    with open("%s/record.csv"% (clone_file_path),'rb') as f:
        reader = list(csv.reader(f))
        f.close()

    res = {
        'login': username,
        'data_name':'Leader Board',
        'data':reader,
    }

    return render_to_response("repo-browse-data-shows.html", res)

"""
def updata_record_result(request):
    username = request.user.get_username()
    file_path = public_data + "/titanic_leader_board.csv"
    with open(file_path,'rb') as f:
        reader = list(csv.reader(f))
        f.close()

    reader.pop(0)
    for a in reader:
        username = a[1]
        with DataHubManager(user=a[1], repo_base=a[1]) as manager:
            repos = manager.list_repos()
            for repo_name in repos:
                print 'repo_name: ',repo_name,'  user_name: ', username
                if db_connect.update_exp_feature(a[1],get_clone_name(username,repo_name),a[2],"accuracy",a[3]):
                    print "begin write"
                    if not os.path.isdir("/home/ubuntu/result"):
                        os.mkdir("/home/ubuntu/result")
                    if not os.path.isdir("/home/ubuntu/result/%s"%(username)):
                        os.mkdir("/home/ubuntu/result/%s"%(username))


                    data = db_connect.get_poject_exp_list(username,get_clone_name(username,repo_name))

                    data_list = []
                    for a in data["exp_records"]:

                        if a.has_key("accuracy"):

                            print a

                            data_dic = {}
                            data_dic["time"] = a["time"]
                            data_dic["commit"] = a["commit"]["id"]
                            data_dic["accuracy"] = a["accuracy"]
                            data_dic["project"] = get_clone_name(username,repo_name)
                            data_dic["user_name"] = username
                            data_list.append(data_dic)
                    if data_list == []:
                        continue
                    print data_list
                    FIELDS = ['user_name','time', 'commit', 'accuracy', 'project']
                    csv_file = open("/home/ubuntu/result/%s/%s.csv"%(username,repo_name),'wb')
                    writer = csv.DictWriter(csv_file, fieldnames = FIELDS)
                    writer.writerow(FIELDS)
                    writer.writerows(data_list)
                    csv_file.close()

    return

def creat_csv(username,file_name,data):
    return
"""

def accuracy_show(request):
    res={}

    List_user = os.listdir("/home/ubuntu/result")
    plot_record = {}
    file_name_record = {}
    for user in List_user:
        if os.path.isdir("/home/ubuntu/result/%s"%(user)):
            record = os.listdir("/home/ubuntu/result/%s"%(user))
            file_names = []
            for file_name in record:
                file_path = "/home/ubuntu/result/%s/%s"%(user,file_name)
                with open(file_path,'rb') as f:
                    reader = list(csv.reader(f))
                    f.close()

                if len(reader) <= 10:
                    continue
                file_names.append(file_name)
                data = []
                time = []
                SUM = 0
                plot_record[file_name] = {}
                for acu in reader:
                    data.append(float(acu[3][0:-1]))
                    time.append(acu[1])
                plot_record[file_name]['data'] = data
                plot_record[file_name]['time'] = time
            file_name_record[user] = file_names

    res = {
        'plot_record':json.dumps(plot_record),
        'file_name_record':json.dumps(file_name_record)
    }
    return render_to_response("repo-browse-accuracy-show.html", res)

import types
def result_show(request):
    username = request.user.get_username()
    file_path = public_data + "/titanic_leader_board.csv"
    with open(file_path,'rb') as f:
        reader = list(csv.reader(f))
        f.close()

    num = {}
    num["nine"] = 0
    num["eight"] = 0
    num["seven"] = 0
    num["six"] = 0
    num["five"] = 0
    num["last"] = 0

    rank = []
    Ran=[]

    for a in range(1,len(reader)):
        reader[a].append(float(reader[a][3][0:-1]))
        rank.append(reader[a][4])
        Ran.append('%s\n%s'%(str(a),reader[a][1]))
        if reader[a][4] >= 90:
            num["nine"] = num["nine"] + 1
            continue
        if reader[a][4] >= 80:
            num["eight"] = num["eight"] + 1
            continue
        if reader[a][4] >= 70:
            num["seven"] = num["seven"] + 1
            continue
        if reader[a][4] >= 60:
            num["six"] = num["six"] + 1
            continue
        if reader[a][4] >= 50:
            num["five"] = num["five"] + 1
            continue
        num["last"] = num["last"] + 1

    print num



    res = {
        'login': username,
        'data_name':'Leader Board',
        'data':reader,
        'num':num,
        'range':json.dumps(Ran),
        'rank':json.dumps(rank)
    }
    return render_to_response("repo-browse-result-show.html", res)
###<<<<add by beyhhhh

@login_required
def table_export(request, repo_base, repo, table_name):
    username = request.user.get_username()

    DataHubManager.export_table(
        username=username, repo_base=repo_base, repo=repo,
        table=table_name, file_format='CSV', delimiter=',', header=True)

    return HttpResponseRedirect(
        reverse('browser-repo_files', args=(repo_base, repo)))


@login_required
def table_delete(request, repo_base, repo, table_name):
    '''
    Deletes the given table.

    Does not currently allow the user the option to cascade in the case of
    dependencies, though the delete_table method does allow cascade (force) to
    be passed.
    '''
    username = request.user.get_username()

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_table(repo, table_name)

    return HttpResponseRedirect(
        reverse('browser-repo_tables', args=(repo_base, repo)))


@login_required
def view_delete(request, repo_base, repo, view_name):
    """
    Deletes the given view.

    Does not currently allow the user the option to cascade in the case of
    dependencies, though the delete_table method does allow cascade (force) to
    be passed.
    """
    username = request.user.get_username()

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_view(repo, view_name)

    return HttpResponseRedirect(
        reverse('browser-repo_tables', args=(repo_base, repo)))

'''
Files
'''


@login_required
def file_upload(request, repo_base, repo):
    username = request.user.get_username()
    data_file = request.FILES['data_file']

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.save_file(repo, data_file)

    return HttpResponseRedirect(
        reverse('browser-repo', args=(repo_base, repo)))



###add by beyhhhh>>

@login_required
def code_upload(request, repo_base, repo):
    username = request.user.get_username()
    data_file = request.FILES['data_file']

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.save_file(repo, data_file)

    return HttpResponseRedirect(
        reverse('browser-repo_codes', args=(repo_base, repo)))




def data_upload(request, repo_base, repo):

    '''
    upload the data that the use has
    '''
    username = request.user.get_username()
    data_file = request.FILES['data_file']
    data_name = clean_file_name(data_file.name)
    if not data_name.endswith(".csv"):
        return HttpResponseRedirect('/browse/'+ username + '/' + repo)
    file_path = "%s/%s/%s" % (public_data
,"public_data",data_name)
    with open(file_path, 'wb+') as destination:
        for chunk in data_file.chunks():
            destination.write(chunk)

    data_information(username, data_name, file_path)

    data_list = [data_name]
    clone_name = get_clone_name(username,repo)
    path =public_data + "/json"
    target = get_project_config(username,clone_name)
    if os.path.isfile(target):
        f = open(target)
        repo_dic = json.load(f)
        for a in data_list:
            if os.path.isfile(path + "/" + a + ".json"):
                f = open(path + "/" + a + ".json")
                data_dic = json.load(f)

                repo_dic[u"date_set"][data_dic["id"]] = data_dic
        with open(target,"w") as w:
            w.write(json.dumps(repo_dic, indent=2, ensure_ascii=False).encode('utf8'))

    return HttpResponseRedirect("/browse/" + username + "/" + repo + "/")




def data_information(username, data_name, file_path, repo = None, data_class = None, public = False, Type = u'csv'):

    if data_name.endswith(u".csv"):
        dic = {}
        dic[u"name"] = dic[u"id"] = dic[u"commit_id"] = dic[u"short_commit_id"] = data_name
        dic[u"path"] = file_path
        dic[u"class"] = data_class
        dic[u"repo"] = repo
        dic[u"user"] = username
        dic[u"type"] = Type
        dic[u"public"] = public
        with open(u"%s/%s/%s.json" % (public_data ,u"json",data_name), 'w') as f:
            json.dump(dic, f, indent=2, default=True)

        return dic


def clean_file_name(text):
    '''
    to make the text starnd
    '''
    return text
###<<add by beyhhhh





@login_required
def file_import(request, repo_base, repo, file_name):
    username = request.user.get_username()
    delimiter = str(request.GET['delimiter'])

    if delimiter == '':
        delimiter = str(request.GET['other_delimiter'])

    header = False
    if request.GET['has_header'] == 'true':
        header = True

    quote_character = request.GET['quote_character']
    if quote_character == '':
        quote_character = request.GET['other_quote_character']

    DataHubManager.import_file(
        username=username,
        repo_base=repo_base,
        repo=repo,
        table=table,
        file_name=file_name,
        delimiter=delimiter,
        header=header,
        quote_character=quote_character)

    return HttpResponseRedirect(
        reverse('browser-repo', args=(repo_base, repo)))


@login_required
def file_delete(request, repo_base, repo, file_name):
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)
    print file_name
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_file(username,clone_name, file_name)

    return HttpResponseRedirect("/browse/" + username + "/" + repo)


def file_download(request, repo_base, repo, file_name):
    username = request.user.get_username()
    clone_name = get_clone_name(username,repo)
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        file_to_download = manager.get_file(clone_name, file_name)

    response = HttpResponse(file_to_download,
                            content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % (file_name)
    return response


'''
Query
'''


def query(request, repo_base, repo):
    query = post_or_get(request, key='q', fallback=None)
    username = request.user.get_username()

    # if this is a shared link, redirect them to the table view
    # with the SQL to be executed pre-populated
    if repo_base.lower() == 'user':
        repo_base = username
        data = {
            'login': username,
            'repo_base': repo_base,
            'repo': 'repo',
            'select_query': False,  # hides the "save as card" button
            'query': query}

        return render_to_response("query-preview-statement.html", data)

    # if the user is just requesting the query page
    if not query:
        data = {
            'login': username,
            'repo_base': repo_base,
            'repo': repo,
            'select_query': False,
            'query': query}
        return render_to_response("query-browse-results.html", data)

    # if the user is actually executing a query
    current_page = 1
    if request.POST.get('page'):
        current_page = request.POST.get('page')

    url_path = reverse('browser-query', args=(repo_base, repo))

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        res = manager.paginate_query(
            query=query, current_page=current_page, rows_per_page=50)

    # get annotation to the table:
    annotation, created = Annotation.objects.get_or_create(url_path=url_path)
    annotation_text = annotation.annotation_text

    data = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'annotation': annotation_text,
        'current_page': current_page,
        'next_page': current_page + 1,  # the template should relaly do this
        'prev_page': current_page - 1,  # the template should relaly do this
        'url_path': url_path,
        'query': query,
        'select_query': res['select_query'],
        'column_names': res['column_names'],
        'tuples': res['rows'],
        'total_pages': res['total_pages'],
        'pages': range(res['start_page'], res['end_page'] + 1),  # template
        'num_rows': res['num_rows'],
        'time_cost': res['time_cost']
    }
    data.update(csrf(request))

    return render_to_response("query-browse-results.html", data)


'''
Annotations
'''


@login_required
def create_annotation(request):
    url = request.POST['url']

    annotation, created = Annotation.objects.get_or_create(url_path=url)
    annotation.annotation_text = request.POST['annotation']
    annotation.save()
    return HttpResponseRedirect(url)


'''
Cards
'''


def card(request, repo_base, repo, card_name):
    username = request.user.get_username()

    if repo_base.lower() == 'user':
        repo_base = username

    # if the user is actually executing a query
    current_page = 1
    if request.POST.get('page'):
        current_page = request.POST.get('page')

    url_path = reverse('browser-query', args=(repo_base, repo))

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        card = manager.get_card(repo=repo, card_name=card_name)
        res = manager.paginate_query(
            query=card.query, current_page=current_page, rows_per_page=50)

    # get annotation to the table:
    annotation, created = Annotation.objects.get_or_create(url_path=url_path)
    annotation_text = annotation.annotation_text

    data = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'card': card,
        'annotation': annotation_text,
        'current_page': current_page,
        'next_page': current_page + 1,  # the template should relaly do this
        'prev_page': current_page - 1,  # the template should relaly do this
        'url_path': url_path,
        'select_query': res['select_query'],
        'column_names': res['column_names'],
        'tuples': res['rows'],
        'total_pages': res['total_pages'],
        'pages': range(res['start_page'], res['end_page'] + 1),  # template
        'num_rows': res['num_rows'],
        'time_cost': res['time_cost']
    }

    data.update(csrf(request))
    return render_to_response("card-browse.html", data)


@login_required
def card_create(request, repo_base, repo):
    username = request.user.get_username()
    card_name = request.POST['card-name']
    query = request.POST['query']
    url = reverse('browser-card', args=(repo_base, repo, card_name))

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.create_card(repo, card_name, query)

    return HttpResponseRedirect(url)


@require_POST
@login_required
def card_update_public(request, repo_base, repo, card_name):
    username = request.user.get_username()

    if 'public' in request.POST:
        public = request.POST['public'] == 'True'
    else:
        raise ValueError("Request missing \'public\' parameter.")

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.update_card(repo, card_name, public=public)

    return HttpResponseRedirect(
        reverse('browser-card', args=(repo_base, repo, card_name)))


@login_required
def card_export(request, repo_base, repo, card_name):
    username = request.user.get_username()

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.export_card(repo, card_name)

    return HttpResponseRedirect(
        reverse('browser-repo_files', args=(repo_base, repo)))


@login_required
def card_delete(request, repo_base, repo, card_name):
    username = request.user.get_username()

    with DataHubManager(user=username, repo_base=repo_base) as manager:
        manager.delete_card(repo, card_name)

    return HttpResponseRedirect(
        reverse('browser-repo_cards', args=(repo_base, repo)))

'''
record

'''
#add by strongman>>
def record(request,repo_base,repo):
    '''
    return a page indicating how many
    '''
    current_page = 1
    record="record"
    if request.POST.get('page'):
        current_page = request.POST.get('page')

    username = request.user.get_username()
    if repo_base.lower() == 'user':
        repo_base = username

    url_path = reverse('browser-record', args=(repo_base, repo))
    with DataHubManager(user=username, repo_base=repo_base) as manager:
        query = manager.select_table_query(repo, record)

        res = manager.paginate_query(
            query=query, current_page=current_page, rows_per_page=50)

    # get annotation to the table:
    annotation, created = Annotation.objects.get_or_create(url_path=url_path)
    annotation_text = annotation.annotation_text

    data = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'table': record,
        'annotation': annotation_text,
        'current_page': current_page,
        'next_page': current_page + 1,  # the template should relaly do this
        'prev_page': current_page - 1,  # the template should relaly do this
        'url_path': url_path,
        'column_names': res['column_names'],
        'tuples': res['rows'],
        'total_pages': res['total_pages'],
        'pages': range(res['start_page'], res['end_page'] + 1),  # template
        'num_rows': res['num_rows'],
        'time_cost': res['time_cost']
    }

    data.update(csrf(request))

    # and then, after everything, hand this off to table-browse. It turns out
    # that this is all using DataTables anyhow, so the template doesn't really
    # use all of the data we prepared. ARC 2016-01-04
    return render_to_response("record-browse.html", data)
##add by strongman<<

'''
Developer Apps
'''


@login_required
def apps(request):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    thrift_apps = App.objects.filter(user=user)
    oauth_apps = get_application_model().objects.filter(user=request.user)

    c = {
        'login': username,
        'thrift_apps': thrift_apps,
        'oauth_apps': oauth_apps}
    return render_to_response('apps.html', c)


@login_required
def thrift_app_detail(request, app_id):
    username = request.user.get_username()
    user = User.objects.get(username=username)
    app = App.objects.get(user=user, app_id=app_id)
    c = RequestContext(request, {
        'login': request.user.get_username(),
        'app': app
    })
    return render_to_response('thrift_app_detail.html', c)


@login_required
def app_register(request):
    username = request.user.get_username()

    if request.method == "POST":
        try:
            user = User.objects.get(username=username)
            app_id = request.POST["app-id"].lower()
            app_name = request.POST["app-name"]
            app_token = str(uuid.uuid4())
            app = App(
                app_id=app_id, app_name=app_name,
                user=user, app_token=app_token)
            app.save()

            try:
                hashed_password = hashlib.sha1(app_token).hexdigest()
                DataHubManager.create_user(
                    username=app_id, password=hashed_password, create_db=False)
            except Exception as e:
                app.delete()
                raise e

            return HttpResponseRedirect('/developer/apps')
        except Exception as e:
            c = {
                'login': username,
                'errors': [str(e)]}
            c.update(csrf(request))
            return render_to_response('app-create.html', c)
    else:
        c = {'login': username}
        c.update(csrf(request))
        return render_to_response('app-create.html', c)


@login_required
def app_remove(request, app_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        DataHubManager.remove_app(app_id=app_id)
        return HttpResponseRedirect(reverse('browser-apps'))
    except Exception as e:
        c = {'errors': [str(e)]}
        c.update(csrf(request))
        return render_to_response('apps.html', c)


@login_required
def app_allow_access(request, app_id, repo_name):
    username = request.user.get_username()
    try:
        app = None
        try:
            app = App.objects.get(app_id=app_id)
        except App.DoesNotExist:
            raise Exception("Invalid app_id")

        app = App.objects.get(app_id=app_id)

        redirect_url = post_or_get(request, key='redirect_url', fallback=None)

        if request.method == "POST":

            access_val = request.POST['access_val']

            if access_val == 'allow':
                grant_app_permission(
                    username=username,
                    repo_name=repo_name,
                    app_id=app_id,
                    app_token=app.app_token)

            if redirect_url:
                redirect_url = redirect_url + \
                    urllib.unquote_plus('?auth_user=%s' % (username))
                return HttpResponseRedirect(redirect_url)
            else:
                if access_val == 'allow':
                    return HttpResponseRedirect(
                        '/settings/%s/%s' % (username, repo_name))
                else:
                    res = {
                        'msg_title': "Access Request",
                        'msg_body':
                            "Permission denied to the app {0}.".format(app_id)
                    }
                    return render_to_response('confirmation.html', res)
        else:
            res = {
                'login': username,
                'repo_name': repo_name,
                'app_id': app_id,
                'app_name': app.app_name}

            if redirect_url:
                res['redirect_url'] = redirect_url

            res.update(csrf(request))
            return render_to_response('app-allow-access.html', res)
    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'error': str(e)}, indent=2, ensure_ascii=False),
            content_type="application/json")


'''
Row Level Security Policies
'''


@login_required
def security_policies(request, repo_base, repo, table):
    '''
    Shows the security policies defined for a table.
    '''
    username = request.user.get_username()

    # get the security policies on a given repo.table
    try:
        policies = RowLevelSecurityManager.find_security_policies(
            repo_base=repo_base, repo=repo, table=table, grantor=username,
            safe=True)
    except LookupError:
        policies = []

    # repack the named tuples. This is a bit of a hack, (since we could just
    # get the view to display named tuples)
    # but is happening for expediency
    policies = [(p.id, p.policy, p.policy_type, p.grantee, p.grantor)
                for p in policies]

    res = {
        'login': username,
        'repo_base': repo_base,
        'repo': repo,
        'table': table,
        'policies': policies}

    res.update(csrf(request))
    return render_to_response("security-policies.html", res)


@login_required
def security_policy_delete(request, repo_base, repo, table, policy_id):
    '''
    Deletes a security policy defined for a table given a policy_id.
    '''
    username = request.user.get_username()
    policy_id = int(policy_id)

    try:
        RowLevelSecurityManager.remove_security_policy(
            policy_id, username)
    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'error': str(e)}, indent=2, ensure_ascii=False),
            content_type="application/json")
    return HttpResponseRedirect(
        reverse('browse-security_policies', args=(repo_base, repo, table)))


@login_required
def security_policy_create(request, repo_base, repo, table):
    '''
    Creates a security policy for a table.
    '''
    username = request.user.get_username()
    try:
        policy = request.POST['security-policy']
        policy_type = request.POST['policy-type']
        grantee = request.POST['policy-grantee']

        RowLevelSecurityManager.create_security_policy(policy=policy,
                                                       policy_type=policy_type,
                                                       grantee=grantee,
                                                       grantor=username,
                                                       repo_base=repo_base,
                                                       repo=repo,
                                                       table=table
                                                       )

    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'error': str(e)}, indent=2),
            content_type="application/json")

    return HttpResponseRedirect(
        reverse('browse-security_policies', args=(repo_base, repo, table)))


@login_required
def security_policy_edit(request, repo_base, repo, table, policyid):
    '''
    Edits a security policy defined for a table given a policy_id.
    '''
    username = request.user.get_username()
    try:
        policy = request.POST['security-policy-edit']
        policy_type = request.POST['policy-type-edit']
        grantee = request.POST['policy-grantee-edit']
        RowLevelSecurityManager.update_security_policy(
            policyid, policy, policy_type, grantee, username)

    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'error': str(e)}, indent=2),
            content_type="application/json")

    return HttpResponseRedirect(
        reverse('browse-security_policies', args=(repo_base, repo, table)))


@login_required
def security_policy_query(request, repo_base, repo, table):
    '''
    Converts a SQL permissions statement into a new security policy.
    '''
    username = request.user.get_username()
    query = post_or_get(request, key='q', fallback=None)
    try:
        permissions_parser = RLSPermissionsParser(repo_base, username)
        permissions_parser.process_permissions(query)

    except Exception as e:
        return HttpResponse(
            json.dumps(
                {'error': str(e)}, indent=2),
            content_type="application/json")

    return HttpResponseRedirect(
        reverse('browse-security_policies', args=(repo_base, repo, table)))


class OAuthAppUpdate(ApplicationUpdate):
    """
    Customized form for updating a Django OAuth Toolkit client app.

    Reorders some fields and ignores modifications to other fields.

    Extends https://github.com/evonove/django-oauth-toolkit/blob/master/
        oauth2_provider/views/application.py
    """

    fields = ['name', 'client_id', 'client_secret', 'client_type',
              'authorization_grant_type', 'redirect_uris']

    def form_valid(self, form):
        # Make sure registrants can't disable the authorization step.
        # Only site admins can do that.
        original_object = get_application_model().objects.get(
            pk=form.instance.pk)
        form.instance.skip_authorization = original_object.skip_authorization
        return super(OAuthAppUpdate, self).form_valid(form)
