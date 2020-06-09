import os
import json
import pmfellow.organization
from pmfellow.crawler_client import CrawlerClient
import base64
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1,OAuth1Session

class JiraClientFactory:
    @classmethod
    def create_oauth_client(cls,site):
        with open("oauth/{}.json".format(site.token)) as json_file:
            oauth = json.load(json_file)
            site.set_oauth(oauth)
            client = JiraClient(site)
            return client 

# requests.get(all_project_url,headers=jira_headers,auth=headeroauth)
    @classmethod
    def create_basic_client(cls,site):
        return JiraClient(site)

    @classmethod
    def oauth_jira(cls,server,app_key,rsa):
        CONSUMER_KEY = app_key
        CONSUMER_SECRET = None
        VERIFIER = ''
        with open(rsa) as f:
            RSA_KEY = f.read()
    
        JIRA_SERVER = server
        REQUEST_TOKEN_URL = JIRA_SERVER + '/plugins/servlet/oauth/request-token'
        AUTHORIZE_URL = JIRA_SERVER + '/plugins/servlet/oauth/authorize'
        ACCESS_TOKEN_URL = JIRA_SERVER + '/plugins/servlet/oauth/access-token'
    
        # oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET, signature_method=SIGNATURE_RSA, rsa_key=RSA_KEY)
        oauth = OAuth1Session(CONSUMER_KEY, signature_method=SIGNATURE_RSA, rsa_key=RSA_KEY)
        request_token = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    
        resource_owner_key = request_token['oauth_token']
        resource_owner_secret = request_token['oauth_token_secret']
    
        print("{}?oauth_token={}".format(AUTHORIZE_URL, request_token['oauth_token']))
        oauth = OAuth1Session(CONSUMER_KEY, resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret, verifier=VERIFIER,
                            signature_method=SIGNATURE_RSA, rsa_key=RSA_KEY) 
        access_token = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        print(access_token)
 


class JiraClient(CrawlerClient):
    def __init__(self,site,data_path = "./data"):
        super(JiraClient, self).__init__(site,data_path)
        if self.site.user != "oauth":
            self.session.headers.update({"Authorization":"Basic {}".format(base64.b64encode((self.site.user +":"+ self.site.token).encode('utf-8')).decode())})
        else:
            self.session.auth = OAuth1(self.site.CONSUMER_KEY,rsa_key=self.site.RSA_KEY,signature_method=SIGNATURE_RSA,resource_owner_key=self.site.ACCESS_TOKEN,resource_owner_secret=self.site.ACCESS_SECRET)

    def get_projects(self, start_from = None, private = False):
        return self.getSingleResource("/rest/api/2/project?")

    def get_project_issues(self, project, limit = None, since = None, until_date = None):
        return self.getResource("/rest/api/2/search?jql=project={}&fields=created,updated,issuetype,creator,summary,description".format(project.path),limit = limit,data_path="issues")

    def get_users(self,since = ""):
        return self.getResource("/api/v4/users?")

    def get_releases(self,project):
        return self.getResource("/api/v4/projects/{}/releases?".format(project))


