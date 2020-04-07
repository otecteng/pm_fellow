import logging
import time
import datetime
from gevent import monkey; monkey.patch_all()
import gevent
from sqlalchemy.orm.query import Query
from pmfellow.jira_client import JiraClient
from pmfellow.parser import Parser
from pmfellow.injector import Developer,Issue,Project,Contributor
from pmfellow.decorator import log_time



class Crawler:
    @staticmethod
    def create_client(site):
        if site.server_type == "jira":
            return JiraClient(site)
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

    def get_project(self,project):
        return (project,self.client.get_project(project))

    @log_time
    def update_projects(self,projects = None):
        projects = self.get_default_projects(projects)

        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.get_project,paged_objs)
            [Project.from_github(data[i],i) for i in data]    
        self.injector.db_commit()

    def get_project_statistic(self,project):
        return (project,self.client.get_project_statistic(project))

    @log_time
    def stat_projects(self,projects = None):
        projects = self.get_default_projects(projects)

        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.get_project_statistic,paged_objs)
            [Project.statistic_github(data[i],i) for i in data]
        self.injector.db_commit()

    def updated_project_commits(self,project):
        return (project,self.client.get_commit_pages(project))

    @log_time
    def commits_projects(self,projects = None):
        projects = self.get_default_projects(projects)

        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(self.updated_project_commits,paged_objs)
            for project in data:
                project.commits = data[project] * self.client.recordsPerPage
        self.injector.db_commit()

    @log_time
    def contributor_projects(self,projects = None):
        projects = self.get_default_projects(projects)
        contribution_items = []
        for paged_objs in self.page_objects(projects,100):
            data = self.execute_parallel(lambda x:(x,self.client.get_contributors(x)),paged_objs)
            if self.site.server_type == "github":
                for i in data:
                    contribution_items = contribution_items + Contributor.from_github(data[i],i)
            if self.site.server_type == "gitee":
                for i in data:
                    contribution_items = contribution_items + Contributor.from_gitee(data[i],i)
        self.injector.insert_data(contribution_items)
        
    @log_time
    def import_issues(self,projects = None,limit = None, until = None):
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

    def stat_commit(self,commit):
        return (commit,self.client.get_commit(commit.project,commit.id))

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
    def import_events(self,projects = None,limit = None):
        projects = self.get_default_projects(projects)
        for idx,i in enumerate(projects):
            data = self.client.get_project_events(i)
            new_events = Parser.json_to_db(data, Event,format=self.site.server_type, project=i, site=self.site)
            self.injector.insert_data(new_events)
            self.injector.db_commit()
            logging.info("[{}/{}]imported:{}".format(idx,len(projects),i.path))
        return

    @log_time
    def import_pull_requests(self,projects = None,limit = None, until = None):
        projects = self.get_default_projects(projects)
        for idx,i in enumerate(projects):
            data = self.client.get_pull_requests(i)
            new_prs = Parser.json_to_db(data, Pull,format=self.site.server_type, project=i, site=self.site)
            self.injector.insert_data(new_prs)
            logging.info("[{}/{}]imported:{}".format(idx,len(projects),i.path))
        return
