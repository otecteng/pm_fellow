import os
import json
import pmfellow.organization
from pmfellow.crawler_client import CrawlerClient
import base64
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1

class JiraClientFactory:
    @classmethod
    def create_oauth_client(cls,site):
        with open(site.token)) as json_file:
            oauth = json.load(json_file)
            site.set_oauth(oauth)
            client = JiraClient(site)            
            return client 

# requests.get(all_project_url,headers=jira_headers,auth=headeroauth)
    @classmethod
    def create_basic_client(cls,site):
        return JiraClient(site)

class JiraClient(CrawlerClient):
    def __init__(self,site,data_path = "./data"):
        super(JiraClient, self).__init__(site,data_path)
        if self.site.user != "oauth":
            self.session.headers.update({"Authorization":"Basic {}".format(base64.b64encode((self.site.user +":"+ self.site.token).encode('utf-8')).decode())})
        else:
            self.headeroauth = OAuth1(self.site.CONSUMER_KEY, client_secret=self.site.CONSUMER_SECRET,resource_owner_key=self.site.ACCESS_TOKEN, resource_owner_secret=self.site.ACCESS_SECRET, signature_method=self.site.SIGNATURE_RSA,rsa_key=self.site.RSA_KEY, signature_type='auth_header')
        
        # self.session.headers.update({"PRIVATE-TOKEN":"{}".format(self.token)})
    
    def getProjects(self,limit = None):
        return self.getResource("/api/v4/projects?",limit = limit)

    def get_projects(self, start_from = None, private = False):
        return self.getSingleResource("/rest/api/2/project?")

    def get_project_issues(self, project, limit = None, since = None, until_date = None):
        return self.getResource("/rest/api/2/search?jql=project={}&fields=created,updated,issuetype,creator,summary,description".format(project.path),limit = limit,data_path="issues")

    def getCommit(self,project,commit):
        return self.getSingleResource("/api/v4/projects/{}/repository/commits/{}".format(project,commit))

    def get_commits(self,project,since = ""):
        return self.getResource("/api/v4/projects/{}/repository/commits?since={}".format(project,since))

    def get_users(self,since = ""):
        return self.getResource("/api/v4/users?")

    def get_pull_requests(self,project,state = "all"):
        return self.getResource("/api/v4/projects/{}/merge_requests?&state={}".format(project.oid,state))

    def get_tags(self,project):
        return self.getResource("/api/v4/projects/{}/repository/tags?".format(project))

    def get_releases(self,project):
        return self.getResource("/api/v4/projects/{}/releases?".format(project))


