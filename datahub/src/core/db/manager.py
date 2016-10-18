# -*- coding: utf-8 -*-
import six
import hashlib
import os
import errno
import re
import codecs
import csv
import json
from shutil import rmtree
import shutil
import pexpect
from django.contrib.auth.models import User

from config import settings
from core.db.connection import DataHubConnection
from core.db.rlsmanager import RowLevelSecurityManager
from core.db.errors import PermissionDenied
from inventory.models import App, Card, Collaborator, DataHubLegacyUser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

clone_file_path = "/home/ubuntu/workspace/clone_file"
public_code = "/home/ubuntu/workspace/code_public"
public_data = "/home/ubuntu/workspace/data_set_public"



def get_projec_path(username,clone_name):
    return u"/home/%s/%s" % (username,clone_name)

def get_user_path(username):
    return u"/home/%s" % (username)

def get_project_config(username,clone_name):
    return (get_projec_path(username,clone_name) + u"/config")

def get_project_parma(username,clone_name):
    return (get_projec_path(username,clone_name) + u"/param")

def get_clone_name(username,repo):
    return repo

####add by beyhhhh
def remove(path):
    for name in os.listdir(path):
        if name[0] == '.':
            continue
        os.remove(path + name)
        print ("Delete File: " + name)
#### add by beyhhhh

class _superuser_connection():
    superuser_con = None

    def __init__(self, repo_base=None):
        self.repo_base = repo_base

    def __enter__(self):
        self.superuser_con = DataHubConnection(
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            repo_base=self.repo_base)
        return self.superuser_con

    def __exit__(self, type, value, traceback):
        self.superuser_con.close_connection()


class DataHubManager:

    def __init__(self, user=settings.ANONYMOUS_ROLE, repo_base=None,
                 is_app=False):

        # blank users are set to anonymous role
        if user == '':
            user = settings.ANONYMOUS_ROLE

        username = None
        password = None

        if is_app:
            app = App.objects.get(app_id=user)
            username = app.app_id
            password = hashlib.sha1(app.app_token).hexdigest()
        else:
            user = User.objects.get(username=user)
            username = user.username
            password = user.password

        if not repo_base:
            repo_base = username

        self.username = username
        self.repo_base = repo_base

        self.user_con = DataHubConnection(
            user=username,
            repo_base=repo_base,
            password=password)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close_connection()

    """ Basic Operations. """

    def change_repo_base(self, repo_base):
        """Changes the repo base and resets the DB connection."""
        self.user_con.change_repo_base(repo_base=repo_base)

    def close_connection(self):
        self.user_con.close_connection()

    def create_repo(self, repo):
        """
        Creates a repo in the current repo_base.

        Returns True on success.

        Succeeds if repo already exists.

        Raises ValueError on an invalid repo name.
        Raises ProgrammingError on permission denied.
        """
        #change by strongman
        #create_record_file(repo)
        print "create repo"

        return self.user_con.create_repo(repo=repo)

    def list_repos(self):

        ###add by beyhhhh the same way I want to use, but change the way to get the list..
        """
        Returns a list of repo (schema) names in the current repo_base.

        Should never fail or raise any exceptions.
        """
        return self.user_con.list_repos()


    def rename_repo(self, repo, new_name):
        """
        Renames a repo.

        Returns True on success.

        Raises ValueError if either name has invalid characters.
        Raises LookupError if the repo doesn't exist.
        Raises ValueError if the new name is taken.
        Raises PermissionDenied if not repo_base owner.
        """
        # only a repo owner can rename a repo:
        if self.repo_base != self.username:
            raise PermissionDenied()

        # rename in user_con
        success = self.user_con.rename_repo(repo=repo, new_name=new_name)
        if success:
            # update collaborator(s), if there are any
            Collaborator.objects.filter(
                repo_name=repo, repo_base=self.repo_base).update(
                    repo_name=new_name)

        return success

    def list_collaborator_repos(self):
        """
        Lists repos to which the current user has been granted access.

        Returns Collaborator objects, which have repo_base and repo attributes.
        Includes repos across all databases, not just the DataHubManager's
        repo_base.

        Note that this method relies on the Collaborators django model. If a
        user bypasses DataHub's API and grants permissions via the database,
        that will not be reflected in this response.

        Should never fail or raise any exceptions.
        """
        user = User.objects.get(username=self.username)

        return Collaborator.objects.filter(user=user)

    def delete_repo(self, repo, force=False):
        """
        Deletes a repo.

        Pass force=True to delete the repo even if it is not empty.

        Returns True on success.

        Raises ValueError if repo has invalid characters.
        Raises LookupError if the repo doesn't exist.
        Raises InternalError if the repo is not empty and force is not True.
        Raises PermissionDenied if not repo_base owner.
        """
        # Only a repo owner can delete repos.
        if self.repo_base != self.username:
            raise PermissionDenied()
        # remove related collaborator objects
        Collaborator.objects.filter(
            repo_name=repo, repo_base=self.repo_base).delete()


        # finally, delete the actual schema
        res = self.user_con.delete_repo(repo=repo, force=force)
        DataHubManager.delete_user_data_folder(self.repo_base, repo)
        return res

    def create_table(self, repo, table, params):
        """
        Creates a table in the current repo_base.

        Returns True on success.

        Raises ValueError if repo, table, or the column names have invalid
        characters.
        Raises LookupError if the repo doesn't exist.
        Raises ValueError if the table already exists.
        Raises TypeError if params isn't iterable.
        Raises KeyError if params doesn't have the right structure.
        Raises ProgrammingError if the params has invalid values.
        Raises PermissionDenied on insufficient permissions.
        """
        return self.user_con.create_table(
            repo=repo, table=table, params=params)

    def list_tables(self, repo):
        """
        Lists the tables in a repo.

        Returns a list of table names.

        Raises LookupError on insufficient permissions or if the repo doesn't
        exist.
        Raises ValueError if repo is invalid.
        """
        return self.user_con.list_tables(repo=repo)

    def describe_table(self, repo, table, detail=False):
        """
        Lists a table's schema. If detail=True, provides all schema info.

        Default return includes column names and types only.

        Returns empty list on insufficient permissions.
        Raises ValueError if repo or table are missing or the empty string.
        """
        if repo.strip() in ['', None]:
            raise ValueError("repo cannot be empty.")
        if table.strip() in ['', None]:
            raise ValueError("table cannot be empty.")
        return self.user_con.describe_table(repo, table, detail)

    def list_table_permissions(self, repo, table):
        """
        Lists the current user's permissions on a table.

        Default return includes column names and types only.

        Returns empty list on insufficient permissions.
        Raises ValueError if repo or table are missing or the empty string.
        """
        if repo.strip() in ['', None]:
            raise ValueError("repo cannot be empty.")
        if table.strip() in ['', None]:
            raise ValueError("table cannot be empty.")
        return self.user_con.list_table_permissions(repo, table)

    def create_view(self, repo, view, sql):
        """
        Creates a view in the current repo_base from a given query.

        Returns True on success.

        Raises ValueError if repo or view have invalid characters.
        Raises ProgrammingError if the repo doesn't exist.
        Raises ProgrammingError if the view already exists.
        Raises ProgrammingError if the query has syntax errors.
        Raises PermissionDenied on insufficient permissions.
        """
        return self.user_con.create_view(
            repo=repo, view=view, sql=sql)

    def list_views(self, repo):
        """
        Lists the views in a repo.

        Returns a list of view names.

        Raises LookupError on insufficient permissions or if the repo doesn't
        exist.
        """
        return self.user_con.list_views(repo=repo)

    def describe_view(self, repo, view, detail=False):
        """
        Lists a view's schema. If detail=True, provides all schema info.

        Default return includes column names and types only.

        Returns empty list on insufficient permissions.
        Raises ValueError if repo or table are missing or the empty string.
        """
        if repo.strip() in ['', None]:
            raise ValueError("repo cannot be empty.")
        if view.strip() in ['', None]:
            raise ValueError("view cannot be empty.")
        return self.user_con.describe_view(repo, view, detail)

    def delete_view(self, repo, view, force=False):
        """
        Deletes a view.

        Set force=True to drop dependent objects (e.g. other views).

        Return True on success.

        Raises ValueError if repo or view has invalid characters.
        Raises ProgrammingError if the repo or view do not exist, even without
        sufficient permissions to see the repo exists.
        Raises ProgrammingError on insufficient permissions.
        """
        return self.user_con.delete_view(repo=repo, view=view, force=force)

    def delete_table(self, repo, table, force=False):
        """
        Deletes a table.

        Set force=True to drop dependent objects (e.g. views).

        Return True on success.

        Raises ValueError if repo or table has invalid characters.
        Raises ProgrammingError if the repo or table do not exist, even without
        sufficient permissions to see the repo exists.
        Raises ProgrammingError on insufficient permissions.
        """
        return self.user_con.delete_table(repo=repo, table=table, force=force)

    def get_schema(self, repo, table):
        """
        Lists a table or view's schema.

        Raises NameError if the repo or table/view does not exist.
        """
        return self.user_con.get_schema(repo=repo, table=table)

    def explain_query(self, query):
        """
        Returns the result of calling EXPLAIN on the query.

        Raises ProgrammingError on query syntax errors.
        Raises ProgrammingError on insufficient repo permissions.
        """
        return self.user_con.explain_query(query)

    def execute_sql(self, query, params=None):
        """
        Executes the query and returns its result.

        Raises ProgrammingError on query syntax errors.
        Raises ProgrammingError on insufficient repo permissions.
        Raises LookupError on invalid role or repo.
        Raises ValueError on invalid query parameters.
        Raises other psycopg2 errors depending on the query.
        """
        return self.user_con.execute_sql(query=query, params=params)

    def add_collaborator(
            self, repo, collaborator, db_privileges, file_privileges):
        """
        Grants a user or app privileges on a repo.

        - collaborator must match an existing User's username or an existing
        App's app_id.
        - db_privileges must be an array of SQL privileges as strings.
          e.g. ['SELECT', 'UPDATE', 'INSERT']
        - file_privileges must be an array of file privileges.
          e.g. ['read', 'write']

        Returns True on success.

        Raises ValueError if collaborator owns or is already a collaborator of
        repo or if db_privileges or file_privileges are invalid.
        Raises LookupError if repo does not exist.
        Raises User.DoesNotExist if collaborator does not exist.
        Raises PermissionDenied on insufficient permissions.
        """
        # Usage is probably not the right check, but neither is CREATE.
        # The trouble is that roles INHERIT permissions from one another
        # depending on whether that flag was set during creation... and I
        # haven't figured out a way to check on whether a user can grant
        # permission to another without actually doing it.
        # For now, we limit adding_collaborators to the actual owner, who has
        # create privileges
        DataHubManager.has_repo_db_privilege(
            self.username, self.repo_base, repo, 'CREATE')

        # you can't add yourself as a collaborator
        if self.username == collaborator:
            raise ValueError(
                "Can't add a repository's owner as a collaborator.")

        collaborators = self.list_collaborators(repo)
        if collaborator in (c['username'] for c in collaborators):
            raise ValueError(
                "{0} is already a collaborator of {1}.".format(
                    collaborator, repo))

        db_privileges = [p.upper() for p in db_privileges]
        file_privileges = [p.lower() for p in file_privileges]

        invalid_db_privileges = set(db_privileges) - {
            'SELECT', 'INSERT', 'UPDATE', 'DELETE',
            'TRUNCATE', 'REFERENCES', 'TRIGGER'}
        if len(invalid_db_privileges) > 0:
            raise ValueError(
                "Unsupported db privileges: \"{0}\"".format(
                    ','.join(invalid_db_privileges)))
        invalid_file_privileges = set(file_privileges) - {'read', 'write'}
        if len(invalid_file_privileges) > 0:
            raise ValueError(
                "Unsupported file privileges: \"{0}\"".format(
                    ','.join(invalid_file_privileges)))

        try:
            app = App.objects.get(app_id=collaborator)
            collaborator_obj, _ = Collaborator.objects.get_or_create(
                app=app, repo_name=repo, repo_base=self.repo_base)
        except App.DoesNotExist:
            user = User.objects.get(username=collaborator)
            collaborator_obj, _ = Collaborator.objects.get_or_create(
                user=user, repo_name=repo, repo_base=self.repo_base)

        # convert privileges list to string and save the object
        db_privilege_str = ', '.join(db_privileges).upper()
        file_privilege_str = ', '.join(file_privileges).lower()

        collaborator_obj.permission = db_privilege_str
        collaborator_obj.file_permission = file_privilege_str

        collaborator_obj.save()

        return self.user_con.add_collaborator(
            repo=repo,
            collaborator=collaborator,
            db_privileges=db_privileges
        )






    def delete_collaborator(self, repo, collaborator):
        """
        Removes a user's or app's privileges on a repo.

        Returns True on success.

        Raises LookupError when repo or collaborator does not exist.
        Raises User.DoesNotExist if collaborator owns repo.
        Raises PermissionDenied on insufficient permissions.
        """
        with _superuser_connection(self.repo_base) as conn:
            collaborators = conn.list_collaborators(repo=repo)
            collaborators = [c.get('username') for c in collaborators]

            # Current user must be the repo's owner or the collaborator to be
            # removed and must be an existing collaborator. If not the owner
            # and removing someone else, current user must have CREATE db
            # privileges.
            if (self.username not in [collaborator, self.repo_base] or
                    self.username not in collaborators):
                DataHubManager.has_repo_db_privilege(
                    self.username, self.repo_base, repo, 'CREATE')
            # The reason we're enforcing permission checks this way is to deal
            # with the edge case where a user removes himself as a collaborator
            # from another user's repo.
            if collaborator not in collaborators:
                raise LookupError('Failed to delete collaborator.'
                                  ' %s is not a collaborator in the specified '
                                  'repository.' % collaborator)

            collab = User.objects.get(username=collaborator)
            Collaborator.objects.get(
                user=collab, repo_name=repo, repo_base=self.repo_base).delete()

            result = conn.delete_collaborator(
                repo=repo, collaborator=collaborator)
        return result

    def list_repo_files(self, repo):
        """
        Lists a repo's files.

        Returns an empty list on bad repo names.

        Raises PermissionDenied on insufficient privileges, even for bad repo
        names.
        """
        # check for permissions
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'read')

        # make a directory for files, if it doesn't already exist
        repo_dir = DataHubManager.create_user_data_folder(self.repo_base, repo)

        uploaded_files = [f for f in os.listdir(repo_dir)]
        return uploaded_files

    def list_repo_cards(self, repo):
        """
        Lists a repo's cards.

        Returns an empty list on bad repo names.

        Raises PermissionDenied on insufficient privileges, even for bad repo
        names.
        """
        # check for permission
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'read')

        # get the relevant cards
        cards = Card.objects.all().filter(
            repo_base=self.repo_base, repo_name=repo)
        cards = [c.card_name for c in cards]
        return cards

    def list_collaborators(self, repo):
        """
        returns a list of objects with keys 'username' and 'permissions'.
        'permissions' are tied to the database being queried, and left to the
        user to be interpreted. For postgres, see
        http://www.postgresql.org/docs/9.4/static/sql-grant.html
        An example response:
        # [{'username': 'foo_user', 'permissions': 'UC'},
           {'username': 'bar_user', 'permissions': 'U'}]

        Doesn't raise any exceptions, though it really should raise
        PermissionDenied if the current user isn't a collaborator.
        """
        # get the database's idea of permissions
        with _superuser_connection(self.repo_base) as conn:
            db_collabs = conn.list_collaborators(repo=repo)

        # merge it with the datahub collaborator model permissions
        usernames = (db_collab['username'] for db_collab in db_collabs)
        dh_collabs = Collaborator.objects.filter(user__username__in=usernames,
                                                 repo_base=self.repo_base,
                                                 repo_name=repo)
        for db_collab in db_collabs:
            db_collab['file_permissions'] = next(
                (dh_collab.file_permission for dh_collab in dh_collabs
                    if dh_collab.user.username == db_collab['username']),
                '')

        return db_collabs

    #add by strongman>>
    def create_record_file(self,repo):
        """
        Saves a record file to a repo.

        """

        DataHubManager.create_user_data_folder(self.repo_base, repo)

        file_name = "record.csv"
        file_path = user_data_path(self.repo_base, repo,file_name)
        f= open(file_path, 'wb+')
        print "success create record file"
        f.close()



    #add by strongman<<

    def save_file(self, repo, data_file):
        """
        Saves a file to a repo.

        Raises PermissionDenied on insufficient privileges.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')

        DataHubManager.create_user_data_folder(self.repo_base, repo)

        file_name = clean_file_name(data_file.name)
        file_path = user_data_path(self.repo_base, repo, file_name)
        with open(file_path, 'wb+') as destination:
            for chunk in data_file.chunks():
                destination.write(chunk)

    def delete_file(self,username, clone_name, file_name):
        """
        Deletes a file from a repo.

        Raises PermissionDenied on insufficient privileges.
        """
        repo = clone_name
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')
        
        
        file_path = user_data_path(self.repo_base, repo, file_name)
        
        file_path = get_projec_path(username,clone_name) + "/" + file_name
        print file_path
        if os.path.isfile(file_path):
            os.remove(file_path)

    def get_file(self, repo, file_name):
        """
        Gets the contents of a file in a repo.

        Raises PermissionDenied on insufficient privileges.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'read')

        file_path = user_data_path(self.repo_base, repo, file_name)
        file = open(file_path).read()
        return file

    #add by beyhhhh>>



    def move_code_to_public(self,username,repo,code_list,data_list):
        clone_name = get_clone_name(username,repo)
        path = get_projec_path(username,clone_name)+ "/"
        src_path = public_code + "/src/"
        json_path = public_code + "/json/"
        for code in code_list:
            if os.path.isfile(path + code):
                shutil.copyfile(path + code,src_path + code)
                dic = {"name":code,"repo":repo,"username" : username,"data_set":data_list}
                with open(json_path + code + '.json', 'w') as f:
                    f.write(json.dumps(dic, indent=2, ensure_ascii=False))

    def repo_data_list(self,username,repo):
        """
        list the data sets that in the repo
        """
        ###even now still need some changes for the data version
        clone_name = get_clone_name(username,repo)
        target_path = get_project_config(username,clone_name)
        data_list = []
        if os.path.isfile(target_path):
            f = open(target_path)
            dic = json.load(f)

            for a in dic["date_set"]:
                data_list.append(dic["date_set"][a])

        print "get data list "
        return data_list

    def repo_code_list(self,username,repo):
        """
        list the codes that in the repo
        """
        clone_name = get_clone_name(username,repo)
        target_path = get_projec_path(username,clone_name) + "/"
        code_list = []

        if os.path.isdir(target_path):
            file_list = os.listdir(target_path)

        for a in file_list:
            dic = {}
            if a[a.rfind('.'):] == ".py":
                dic["name"] = a
                dic["url"] = "edit"
                code_list.append(dic)

            if a[a.rfind('.'):] == ".ipynb":
                dic["name"] = a
                dic["url"] = "notebooks"
                code_list.append(dic)
                
            if a[a.rfind('.'):] == ".param":
                dic["name"] = a
                dic["url"] = "edit"
                code_list.append(dic)
            if not '.' in a:
                dic["name"] = a
                dic["url"] = "edit"
                code_list.append(dic)
        return code_list



    def repo_conf_list(self,username,repo):
        clone_name = get_clone_name(username,repo)
        target_path = get_projec_path(username,clone_name) + "/"
        conf_list = []

        if os.path.isdir(target_path):
            file_list = os.listdir(target_path)
        for a in file_list:
            if a[a.rfind('.'):] == "":
                conf_list.append(a)
                 
        return conf_list

    """
    def push_github(self,username,repo):
        '''
        push the code to the github
        '''
        print "manager Push"
        ###set the name in gitlab
        clone_name = get_clone_name(username,repo)

        clone_path = get_projec_path(username,clone_name) +"/"
        if os.path.isdir(clone_path):
            os.chdir(clone_path)

            print "Begine push"
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
                print "Push Successfully"
                return "Push Successfully"
            #if index == 0:
                #print "you have change nothing"
                #return "You have change nothing, have nothing to push"

            if index == 2:
                print "there is something wrong"
                return "there is something wrong"
        else:
            return "there is something wrong"

        return



    ####those code was used in the second changes and was useless

    def updata_user_repo(self,repo,file_list):
        #update the code and the data_set in the test flord to the repo flord


        path = "/home/ubuntu/sunjiaojiao/datahub"
        test_flord_path = path + "/user_data/"+self.username+"/"

        data_path = user_data_path(self.repo_base, repo) + "/"
        print data_path
        print test_flord_path
        for file_name in file_list:
            print test_flord_path + file_name
            if os.path.isfile(test_flord_path + file_name):
                print data_path + file_name
                shutil.copyfile(test_flord_path + file_name,user_data_path(self.repo_base, repo,file_name))
                print "cp " + file_name+" successfully"
            if os.path.isdir(test_flord_path + file_name):
                shutil.copytree(test_flord_path + file_name,data_path + file_name)
                print "cp " + file_name+" successfully"

    def move_files(self,repo,files,Cleaning = True):

        #to get the user files, which the user coding in
        path = "/home/ubuntu/sunjiaojiao/datahub"
        print path
        base_path = path+"/user_data/"+self.username+"/"
        if os.path.isdir(base_path):
            if Cleaning:
                print "clean the flord"
                remove(base_path)
                print "KKKK"
        else:
            os.mkdir(base_path)

        print "move the files"
        for a in files:
            print a
            self.move_the_file(repo,a,base_path)
        print "move_files"
        return "/user_data/"+self.username+"/"

    def move_the_file(self,repo,file_name,target_path):
        #Move the file(file_name) to target
        path = user_data_path(self.repo_base, repo, file_name)
        print "the path is " + path
        print "  the now path is " + os.getcwd()

        if os.path.isdir(path):
            shutil.copytree(path,target_path + file_name)

        if os.path.isfile(path):
            shutil.copyfile(path,target_path + file_name)
        else:
            return "The file(or flord) " + a + " can't find" +" " + path + a

        return "successfully move the " + file_name + " to " + target_path






    def get_Data_list(self):
        #get the Data_set list in user test flord
        path = "/home/ubuntu/sunjiaojiao/datahub" + "/user_data/"+self.username+"/"
        Data_list = []
        print "the path is " + path
        for a in os.listdir(path):
            if a[a.rfind('.'):] == '.csv':
                Data_list.append(a)
        print "data list is "
        return Data_list

    def get_Code_list(self):
        #get the code list in user test flord
        path = "/home/ubuntu/sunjiaojiao/datahub" + "/user_data/"+self.username+"/"
        print "the path is " + path
        Code_list = []
        for a in os.listdir(path):
            if a[a.rfind('.'):] == '.ipynb':
                Code_list.append(a)
            if a[a.rfind('.'):] == '.py':
                Code_list.append(a)
            if a[a.rfind('.'):] == '.json':
                Code_list.append(a)
        print "code list is "
        print Code_list
        return Code_list
    """

    def export_table(self, repo, table, file_format='CSV',
                     delimiter=',', header=True):
        """
        Exports a table to a file in the same repo.

        Defaults to CSV format with header row.

        Raises LookupError on invalid repo or table.
        Raises ProgrammingError on invalid combinations of file_format,
        delimiter, and header.
        Raises PermissionDenied on insufficient privileges.
        """
        # clean up names:
        repo = clean_str(repo, '')
        table = clean_str(table, '')

        # check for permissions
        DataHubManager.has_repo_db_privilege(
            self.username, self.repo_base, repo, 'CREATE')

        # make the base_repo and repo's folder, if they don't already exist
        DataHubManager.create_user_data_folder(self.repo_base, repo)

        # define the file path for the new table
        file_name = clean_file_name(table)
        file_path = user_data_path(
            self.repo_base, repo, file_name, file_format)

        # format the full table name
        table_name = '%s.%s' % (repo, table)

        # pass arguments to the connector
        self.user_con.export_table(
            table_name=table_name,
            file_path=file_path,
            file_format=file_format,
            delimiter=delimiter,
            header=header)

    def export_view(self, repo, view, file_format='CSV',
                    delimiter=',', header=True):
        """
        Exports a view to a file in the same repo.

        Defaults to CSV format with header row.

        Raises LookupError on invalid repo or view.
        Raises ProgrammingError on invalid combinations of file_format,
        delimiter, and header.
        Raises PermissionDenied on insufficient privileges.
        """
        # clean up names:
        repo = clean_str(repo, '')
        view = clean_str(view, '')

        # check for permissions
        DataHubManager.has_repo_db_privilege(
            self.username, self.repo_base, repo, 'CREATE')

        # make the repo_base and repo's folder, if they don't already exist
        DataHubManager.create_user_data_folder(self.repo_base, repo)

        # define the file path for the new view
        file_name = clean_file_name(view)
        file_path = user_data_path(
            self.repo_base, repo, file_name, file_format)

        # format the full view name
        view_name = '%s.%s' % (repo, view)

        self.user_con.export_view(
            view_name=view_name,
            file_path=file_path,
            file_format=file_format,
            delimiter=delimiter,
            header=header)

    def update_card(self, repo, card_name, new_query=None,
                    new_name=None, public=None):
        """
        Updates a card's name, query, and/or public visibility.

        Returns the card on success.

        Raises ValueError if new_name is the empty string.
        Raises TypeError on invalid public parameter.
        Raises PermissionDenied on insufficient privileges or bad new_query.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')

        card = Card.objects.get(
            repo_base=self.repo_base, repo_name=repo, card_name=card_name)
        # update the card
        if new_query is not None:
            # Queries for cards must work
            try:
                self.execute_sql(new_query)
            except Exception:
                raise PermissionDenied(
                    'Either missing required privileges or bad query')
            card.query = new_query
        if new_name is not None:
            if len(new_name) < 1:
                raise ValueError("new_name must be longer than zero "
                                 "characters")
            card.card_name = new_name
        if public is not None:
            if type(public) is not bool:
                raise TypeError("public must be of type bool")
            card.public = public

        card.save()
        return card

    def get_card(self, repo, card_name):
        """
        Gets a card in a repo.

        Raises PermissionDenied on insufficient privileges.
        """
        # This goes through manage.py because, it requires a check that the
        # user actually has repo access.
        card = Card.objects.get(
            repo_base=self.repo_base, repo_name=repo, card_name=card_name)
        if not card.public:
            DataHubManager.has_repo_file_privilege(
                self.username, self.repo_base, repo, 'read')

        card = Card.objects.get(
            repo_base=self.repo_base, repo_name=repo, card_name=card_name)

        return card

    def create_card(self, repo, card_name, query):
        """
        Creates a card in a repo from a given query.

        Returns the card on success.

        Raises IntegrityError if card with same name already exists.
        Raises PermissionDenied on insufficient privileges or bad query.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')

        # to create a card, the user must be able to successfully execute
        # the query from their own database user.
        try:
            self.execute_sql(query)
        except Exception:
            raise PermissionDenied(
                'Either missing required privileges or bad query')

        card, created = Card.objects.get_or_create(
            repo_base=self.repo_base, repo_name=repo,
            card_name=card_name, query=query)

        return card

    def export_card(self, repo, card_name, file_format='CSV'):
        """
        Exports the results of a card to a new file in the repo.

        Any existing file with that name is overwritten.

        Raises PermissionDenied on insufficient privileges or bad query.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')

        card = Card.objects.get(repo_base=self.repo_base,
                                repo_name=repo, card_name=card_name)
        query = card.query

        # to export a card, the user must be able to successfully execute
        # the query from their own database user.
        try:
            self.execute_sql(query)
        except Exception:
            raise PermissionDenied(
                'Either missing required privileges or bad query')

        # create the user data folder if it doesn't already exist
        DataHubManager.create_user_data_folder(self.repo_base, repo)

        file_name = clean_file_name(card_name)
        file_path = user_data_path(
            self.repo_base, repo, file_name, file_format)

        self.user_con.export_query(query=query,
                                   file_path=file_path,
                                   file_format=file_format)

    def delete_card(self, repo, card_name):
        """
        Deletes a card from a repo.

        Raises Card.DoesNotExist for invalid card_name.
        Raises PermissionDenied on insufficient privileges.
        """
        DataHubManager.has_repo_file_privilege(
            self.username, self.repo_base, repo, 'write')

        card = Card.objects.get(repo_base=self.repo_base,
                                repo_name=repo, card_name=card_name)
        return card.delete()

    def limit_and_offset_select_query(self, query, limit, offset):
        """
        Modifies select queries, adding limits and offsets.

        Used primarily for pagination
        """
        return self.user_con.limit_and_offset_select_query(
            query=query, limit=limit, offset=offset)

    def paginate_query(self, query, current_page, rows_per_page):
        """
        Set variables for query pagination, limiting query statement
        to just the section of the table that will be displayed
        """
        explanation = self.explain_query(query)

        num_rows = explanation['num_rows']
        time_cost = explanation['time_cost']
        byte_width = explanation['byte_width']
        total_pages = 1 + (num_rows / rows_per_page)

        # set first page that a user can navigate to
        start_page = current_page - 5
        if start_page < 1:
            start_page = 1

        # set the last page that a user can navigate to
        end_page = start_page + 10
        if end_page > total_pages:
            end_page = total_pages

        # set the offset
        offset = (current_page - 1) * rows_per_page

        # add limit and offset for select queries
        res = self.limit_and_offset_select_query(
            query=query, limit=rows_per_page, offset=offset)
        select_query = res['select_query']
        query = res['query']

        # actually make the query
        column_names = None  # top columns
        rows = None  # in tuple form

        res = self.execute_sql(query)

        # determine the column_names and rows
        if select_query or res['row_count'] > 0:  # normal case
            column_names = [field['name'] for field in res['fields']]
            rows = res['tuples']
        else:  # query just returned a bool
            column_names = ['status']
            rows = [['success' if res['status'] else res['error']]]

        result = {
                'num_rows': num_rows,
                'time_cost': time_cost,
                'byte_width': byte_width,
                'total_pages': total_pages,
                'start_page': start_page,
                'end_page': end_page,
                'column_names': column_names,
                'rows': rows,
                'select_query': select_query
        }

        return result

    def select_table_query(self, repo, table):
        """
        Return a database query for selecting the table.

        Necessary for keeping sq/nosql queries out of views.
        """
        return self.user_con.select_table_query(
            repo_base=self.repo_base, repo=repo, table=table)

    """
    Static methods that don't require permissions
    """

    @staticmethod
    def create_user_data_folder(repo_base, repo=''):
        """
        Creates a user data folder for the given user.

        Optionally accepts a specific repo's folder to create.
        Fails silently if the folder already exists.
        Returns the deleted path.
        """
        repo_dir = os.path.abspath(
            os.path.join(os.sep, 'user_data', repo_base, repo))
        try:
            os.makedirs(repo_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return repo_dir

    @staticmethod
    def delete_user_data_folder(repo_base, repo=''):
        """
        Deletes a user data folder for the given user.

        Optionally accepts a specific repo's folder to delete.
        Fails silently if the folder does not exist.
        Returns the deleted path.
        """
        repo_dir = os.path.abspath(
            os.path.join(os.sep, 'user_data', repo_base, repo))
        try:
            rmtree(repo_dir)
        except OSError as e:
            if e.errno:
                pass
        return repo_dir

    @staticmethod
    def user_data_folder_exists(username):
        """Returns true if user has a folder in /user_data. False otherwise."""
        repo_dir = os.path.abspath(
            os.path.join(os.sep, 'user_data', username))
        return os.path.exists(repo_dir)

    @staticmethod
    def list_public_repos():
        """
        Lists repositories that are accessible by the dh_public user.
        """
        return Collaborator.objects.filter(user__username=settings.PUBLIC_ROLE)

    """
    The following methods run in superuser mode only
    """

    @staticmethod
    def user_exists(username):
        with _superuser_connection() as conn:
            result = conn.user_exists(username)
        return result

    @staticmethod
    def database_exists(db_name):
        with _superuser_connection() as conn:
            result = conn.database_exists(db_name)
        return result

    """ User/Role Management """

    @staticmethod
    def create_user(username, password, create_db=True):
        """Creates a DB role, database, and data folder for a new user."""
        with _superuser_connection() as conn:
            res = conn.create_user(
                username=username, password=password, create_db=create_db)
            DataHubManager.create_user_data_folder(username)
        return res

    @staticmethod
    def create_user_database(username):
        """Creates the database and data folder for a user."""
        with _superuser_connection() as conn:
            res = conn.create_user_database(username=username)
        return res

    @staticmethod
    def _remove_django_user(username):
        # Get the user associated with the username, delete their apps, and
        # then delete the user
        try:
            user = User.objects.get(username=username)
            apps = App.objects.filter(user=user)
            for app in apps:
                app_id = app.app_id
                DataHubManager.remove_app(app_id=app_id)

            Collaborator.objects.filter(user=user).delete()
            user.delete()
        except User.DoesNotExist:
            user = None

        # Do the same thing for legacy users
        try:
            legacy_user = DataHubLegacyUser.objects.get(username=username)
            apps = App.objects.filter(legacy_user=legacy_user)
            for app in apps:
                app_id = app.app_id
                DataHubManager.remove_app(app_id=app_id)
            legacy_user.delete()
        except DataHubLegacyUser.DoesNotExist:
            legacy_user = None

        # Raise a not found exception if this didn't result in any deletions
        if not user and not legacy_user:
            raise User.DoesNotExist()

    @staticmethod
    def remove_user(username, remove_db=True, ignore_missing_user=False):
        # Delete the Django user
        try:
            DataHubManager._remove_django_user(username)
        except User.DoesNotExist as e:
            if not ignore_missing_user:
                raise e

        # Delete the user's db
        if remove_db:
            DataHubManager.remove_database(username)

        # Make a connection, and delete the user's database role
        with _superuser_connection() as conn:
            try:
                # Try the simple case first: delete the user when they have no
                # db permissions left
                result = conn.remove_user(username=username)
            except:
                # Assume the failure was outstanding db permissions. Remove
                # them and try again.
                all_db_list = DataHubManager.list_all_databases()
                for db in all_db_list:
                    DataHubManager.drop_owned_by(username=username,
                                                 repo_base=db)
                result = conn.remove_user(username=username)

            RowLevelSecurityManager.remove_user_from_policy_table(
                username=username)

        return result

    @staticmethod
    def remove_app(app_id):
        app = App.objects.get(app_id=app_id)
        Collaborator.objects.filter(app=app).delete()
        app.delete()

        with _superuser_connection() as conn:
            conn.remove_user(username=app_id)

    @staticmethod
    def drop_owned_by(username, repo_base):
        with _superuser_connection(repo_base) as conn:
            result = conn.drop_owned_by(username)
        return result

    @staticmethod
    def list_all_users():
        with _superuser_connection() as conn:
            result = conn.list_all_users()
        return result

    @staticmethod
    def list_all_databases():
        """
        lists all user databases. Does not list some,
        like postgres, templates0, templates1, or datahub
        """
        with _superuser_connection() as conn:
            result = conn.list_all_databases()
        return result

    @staticmethod
    def remove_database(repo_base, revoke_collaborators=True):
        collaborators = Collaborator.objects.filter(repo_base=repo_base)
        for collaborator in collaborators:
            collaborator.delete()

        DataHubManager.delete_user_data_folder(repo_base)
        with _superuser_connection() as conn:
            result = conn.remove_database(repo_base, revoke_collaborators)
        return result

    @staticmethod
    def change_password(username, password):
        with _superuser_connection() as conn:
            result = conn.change_password(username=username,
                                          password=password)
        return result

    """ Import/Export Files """

    @staticmethod
    def import_file(username, repo_base, repo, table, file_name,
                    file_format='CSV', delimiter=',', header=True,
                    encoding='ISO-8859-1', quote_character='"'):
        # check for permissions
        print "enter the import file"
        delimiter = delimiter.decode('string_escape')

        DataHubManager.has_repo_db_privilege(
            username, repo_base, repo, 'CREATE')

        # prepare some variables
        file_path = user_data_path(repo_base, repo, file_name)
        file_path = public_data + "/public_data/" + file_name
        print file_path
        table_name, _ = os.path.splitext(file_name)
        table_name = clean_str(table_name, 'table')
        dh_table_name = '%s.%s.%s' % (repo_base, repo, table_name)

        # open the file
        print "open the file"
        if os.path.isfile(file_path):
            print "readddddd"
            f = codecs.open(file_path, 'r', 'ISO-8859-1')
        print "read"
        data = csv.reader(f, delimiter=delimiter)
        print "OK"

        # create a table for the data
        cells = data.next()
        columns = [clean_str(str(i), 'col') for i in range(0, len(cells))]
        if header:
            columns = map(lambda x: clean_str(x, 'col'), cells)
        columns = rename_duplicates(columns)

        query = 'CREATE TABLE %s (%s text' % (dh_table_name, columns[0])
        print query
        for column in columns[1:len(columns)]:
            query += ', %s %s' % (column, 'text')
        query += ')'

        manager = DataHubManager(user=username, repo_base=repo_base)
        manager.execute_sql(query=query)

        # populate the newly created table with data from the csv
        with _superuser_connection(repo_base) as conn:
            result = conn.import_file(
                table_name=dh_table_name,
                file_path=file_path,
                file_format=file_format,
                delimiter=delimiter,
                header=header,
                encoding=encoding,
                quote_character=quote_character)
        return result

    """ Access Privilege Checks """

    @staticmethod
    def has_base_privilege(login, repo_base, privilege):
        with _superuser_connection(repo_base) as conn:
            result = conn.has_base_privilege(
                login=login, privilege=privilege)
        return result

    @staticmethod
    def has_repo_db_privilege(login, repo_base, repo, privilege):
        """
        Raises PermissonDenied if user does not have the DATABASE privilege
        passed in the argument, e.g. 'USAGE'.

        Relies on database role management, so this is a pretty straightforward
        call.
        """
        repo = repo.lower()
        repo_base = repo_base.lower()
        with _superuser_connection(repo_base) as conn:
            result = conn.has_repo_db_privilege(
                login=login, repo=repo, privilege=privilege)
        if not result:
            raise PermissionDenied()

    @staticmethod
    def has_repo_file_privilege(login, repo_base, repo, privilege):
        """
        Raises PermissonDenied if user does not have the FILE privilege passed
        in the argument, e.g. 'read'.
        """
        repo = repo.lower()
        repo_base = repo_base.lower()

        # Users always have privileges over their own files.
        if login == repo_base:
            return

        # Check if the current user or the public user has the privilege on
        # this repo.
        # The anonymous user is never explicitly shared with, so we don't need
        # to check for that.
        permitted_collaborators = Collaborator.objects.filter(
            repo_base=repo_base,
            repo_name=repo,
            file_permission__contains=privilege,
            user__username__in=[settings.PUBLIC_ROLE, login])
        if not next((c for c in permitted_collaborators), None):
            raise PermissionDenied()

    @staticmethod
    def has_table_privilege(login, repo_base, table, privilege):
        # a straightforward call to the DB, since it manages this
        with _superuser_connection(repo_base) as conn:
            result = conn.has_table_privilege(
                login=login, table=table, privilege=privilege)
        return result

    @staticmethod
    def has_column_privilege(login, repo_base, table, column, privilege):
        # a straightforward call to the DB, since it manages this
        with _superuser_connection(repo_base) as conn:
            result = conn.has_column_privilege(login=login,
                                               table=table,
                                               column=column,
                                               privilege=privilege)
        return result


def user_data_path(repo_base, repo='', file_name='', file_format=None):
    """
    Returns an absolute path to a file or repo in a user's data folder.

    user_data_path('foo') => '/user_data/foo'
    user_data_path('foo', repo='bar') => '/user_data/foo/bar'
    user_data_path('foo', repo='bar', file_name='baz')
        => '/user_data/foo/bar/baz'

    Raises ValueError on non-string input, if repo_base is '', or if file_name
    is provided without repo.
    """
    if len(repo_base) == 0:
        raise ValueError('Invalid repo_base.')
    if len(file_name) > 0 and len(repo) == 0:
        raise ValueError('Must pass in repo when providing file_name.')
    parts = [repo_base, repo, file_name]
    for p in parts:
        if (not isinstance(p, six.string_types) or p.startswith('.')):
            raise ValueError('Invalid path component.')
    path = os.path.abspath(os.path.join(os.sep, 'user_data', *parts))

    if file_format:
        if re.match('[^0-9a-zA-Z_-]', file_format):
            raise ValueError('Invalid file format specified.')
        path = '%s.%s' % (path, file_format)

    return path


def clean_file_name(text):
    # remove leading periods
    return re.sub('^\.+', '', text)


def clean_str(text, prefix):
    string = text.strip().lower()

    # replace whitespace with '_'
    string = re.sub(' ', '_', string)

    # remove invalid characters
    string = re.sub('[^0-9a-zA-Z_]', '', string)

    # remove leading characters until a letter or underscore
    string = re.sub('^[^a-zA-Z_]+', '', string)

    if string == '':
        return clean_str(prefix + text, '')

    return string


def rename_duplicates(columns):
    columns = [c.lower() for c in columns]
    new_columns = []
    col_idx = {c: 1 for c in columns}

    for c in columns:
        if columns.count(c) == 1:
            new_columns.append(c)
        else:
            # add a suffix
            new_columns.append(c + str(col_idx[c]))
            col_idx[c] += 1

    return new_columns
