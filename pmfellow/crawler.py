import logging
import time
import datetime
from gevent import monkey; monkey.patch_all()
import gevent
from sqlalchemy.orm.query import Query
from pmfellow.jira_client import JiraClientFactory,JiraClient
from pmfellow.parser import Parser
from pmfellow.injector import Developer,Issue,Project,Contributor,Board
from pmfellow.decorator import log_time
import json


class Crawler:
    @staticmethod
    def create_client(site):
        if site.server_type == "jira":
            if site.user == "oauth":
                return JiraClientFactory.create_oauth_client(site)
            else:
                return JiraClientFactory.create_basic_client(site)
        return None

    def __init__(self,site,injector = None):
        self.site = site
        self.client = Crawler.create_client(site)
        self.injector = injector

    def page_objects(self, objects, per_page ):
        pages, m = divmod(len(objects), per_page)
        if m > 0: pages = pages + 1
        ret = []
        for i in range(pages):
           ret.append(objects[i * per_page:(i+1)*per_page])
        return ret
    
    def execute_parallel(self,func,objects = None):
        ret = {}
        g = [gevent.spawn(func, i) for i in objects]
        gevent.joinall(g)
        for _,r in enumerate(g):
            if r is None or r.value[0] is None:
                logging.info("null in execute_parallel")
            if r.value[1] is not None:
                ret[r.value[0]] = r.value[1]
        return ret

    def get_default_projects(self,projects):
        if projects is None:
            projects = self.injector.get_projects(site = self.site.iid)
        if type(projects) == Query :
            projects = projects.all()
        return list(filter(lambda x:x.size != 0, projects))

    def import_projects(self,private = False):
        data = self.client.get_projects(private = private)
        projects = Parser.parse_projects(data,self.site.server_type)
        for i in projects:
            i.site = self.site.iid
        self.injector.insert_data(projects)
        return projects
        
    @log_time
    def import_issues(self,projects = None,limit = None, until = None, dump = None ):
        projects = self.get_default_projects(projects)

        for idx,i in enumerate(projects):
            last = None # self.injector.get_project_last_issue(i.path)
            if last is not None:
                issues = self.client.get_project_issues(i, since = last.created_at + datetime.timedelta(seconds=1), until_date = until, limit = limit)
            else:
                issues = self.client.get_project_issues(i,until_date = until,limit = limit)
            new_issues = Parser.json_to_db(issues, Issue, format=self.site.server_type, project=i, site=self.site)
            self.injector.insert_data(new_issues)
            logging.info("[{}/{}]imported:{}".format(idx,len(projects),i.path))
        return

    @log_time
    def import_boards(self):
        boards = []
        for paged_objs in self.page_objects(Parser.json_to_db(self.client.get_boards()["views"],Board,site=self.site),100):
            data = self.execute_parallel(lambda x:(x,self.client.get_board_config(x.oid)["columnConfig"]["columns"]),paged_objs)
            for i in data:
                boards.append({"oid":i.oid,"name":i.name,"columns":",".join(list(map(lambda  x : x["name"],data[i])))})
        with open("board.json","w") as outfile:
            json.dump(boards, outfile)

        projects = []
        for paged_objs in self.page_objects(Parser.json_to_db(self.client.get_boards()["views"],Board,site=self.site),100):
            data = self.execute_parallel(lambda x:(x,self.client.get_board_projects(x.oid)),paged_objs)
            for i in data:
                projects.append({"oid":i.oid,"name":i.name,"projects":data[i]})
        with open("board_projects.json","w") as outfile:
            json.dump(projects, outfile)
        return

    @log_time
    def import_users(self):
        data = self.client.get_users()
        users = Parser.json_to_db(data,Developer,format = self.site.server_type, site = self.site)
        self.injector.insert_data(users)
        return users

    @log_time
    def detail_users(self, since = None, until = None):
        users = self.injector.get_users(since = since, until = until, site = self.site.iid)
        logging.info(len(users))
        for paged_objs in self.page_objects(users,100):
            data = self.execute_parallel(lambda x:(x,self.client.get_user_detail(x)),paged_objs)
            for i in data:
                Developer.from_github(data[i],i)
        self.injector.db_commit()
        return users

    @log_time
    def import_changes(self, project, limit = None, until = None, issuetype = None, dump = False):
        issues = self.injector.get_issues(site = self.site.iid, project = project.path,issuetype=issuetype )
        logging.info(issues)
        changes = []
        for paged_objs in self.page_objects(issues,100):
            data = self.execute_parallel(lambda x:(x,self.client.get_issue_changelog(x,dump=dump)),paged_objs)
            changes.extend(data.values())
        with open("{}.json".format(project.path),"w") as outfile:
            json.dump(changes, outfile)
        return