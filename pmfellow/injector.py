# -*- coding: UTF-8 -*-
import re
import json
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Float, DateTime,Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
import logging
from pmfellow.safe_parser import Convertor

Base = declarative_base()
class Project(Base):
    __tablename__ = 'project'
    iid = Column(Integer, primary_key=True)    
    oid = Column(Integer)
    site = Column(Integer)
    path = Column(String(64))
    private = Column(Boolean)
    description = Column(String(512))
    owner = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pushed_at = Column(DateTime)
    language = Column(String(64))
    size = Column(Integer)
    participation = Column(Integer)
    commits = Column(Integer)
    
    def __init__(self,data = None):
        if data:
            self.oid = data["id"]
            self.path = data["path_with_namespace"]
            self.created_at = datetime.datetime.strptime(data["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
            self.updated_at = datetime.datetime.strptime(data["last_activity_at"][:19], "%Y-%m-%dT%H:%M:%S")
            self.owner = data["owner"]["username"]

    def __str__(self):
        return "{}\t{}\t{}".format(self.path,self.created_at,self.updated_at)

    @staticmethod
    def from_jira(data,ret = None):
        if ret is None:
            ret = Project()
        if len(data) == 0:
            logging.warning("empty data, project {}".format(ret.iid))
            return ret
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"key","path")
        Convertor.json2db(data,ret,"name","description")
        Convertor.json2db(data,ret,"projectTypeKey","language")
        if "projectCategory" in data and data["projectCategory"]:
            ret.owner = data["projectCategory"]["name"]
        return ret

class Site(Base):
    __tablename__ = 'site'
    iid = Column(Integer, primary_key=True)    
    name = Column(String(64))
    server_type = Column(String(64))
    url = Column(String(64))
    user = Column(String(64))
    token = Column(String(64))
    created_at = Column(DateTime)
    
    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}".format(self.iid,self.name,self.server_type,self.url,self.created_at)

    def set_oauth(self,oauth):
        self.CONSUMER_KEY = oauth['consumer_key']
        self.CONSUMER_SECRET = oauth['consumer_secret']
        self.ACCESS_TOKEN = oauth['access_token']
        self.ACCESS_SECRET = oauth['access_token_secret']
        with open(oauth['key_cert']) as f:
            self.RSA_KEY = f.read()

class Group(Base):
    __tablename__ = 'developer_group'
    iid = Column(Integer, primary_key=True)    
    name = Column(String(64))
    oid = Column(Integer)
    site = Column(Integer)
    location = Column(String(64))
    repo_count = Column(Integer)
    created_at = Column(DateTime)
    def __str__(self):
        return "{}\t{}\t{}\t{}".format(self.iid,self.name,self.repo_count,self.location)

    @staticmethod
    def from_github(data):
        ret = Group()
        ret.name = data["name"]
        ret.location = data["location"]
        ret.description = data["description"]
        if data["repositories"]:
            ret.repo_count = data["repositories"]["totalCount"]
        return ret

class Issue(Base):
    __tablename__ = 'issue'
    iid = Column(Integer, primary_key=True)
    id = Column(String(64))
    project = Column(String(128))
    site = Column(Integer)
    project_oid = Column(Integer)
    oid = Column(Integer)

    issuetype = Column(String(64))
    author_name = Column(String(64))
    author_email = Column(String(64))
    summary = Column(String(512))
    status = Column(String(64))
    description = Column(String(1024))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def __str__(self):
        return "{}[{}]:{}".format(self.created_at,self.author_email,self.message)

    @staticmethod
    def from_jira(data,ret = None):
        if ret is None:
            ret = Issue()
        if len(data) == 0:
            logging.warning("empty data, project {}".format(ret.iid))
            return ret
        Convertor.json2db(data,ret,"id","oid")
        Convertor.json2db(data,ret,"key","id")
        subdata = data["fields"]
        Convertor.json2db(subdata,ret,"created","created_at")
        Convertor.json2db(subdata,ret,"updated","updated_at")
        Convertor.json2db(subdata,ret,"summary")
        Convertor.json2db(subdata,ret,"description")

        ret.issuetype = data["fields"]["issuetype"]["name"]
        ret.status = data["fields"]["status"]["name"]
        if "creator" in data["fields"] and data["fields"]["creator"] is not None:
            if "displayName" in data["fields"]["creator"]:
                ret.author_name = data["fields"]["creator"]["displayName"]
            else:
                ret.author_name = data["fields"]["creator"]["name"]
                ret.author_email = data["fields"]["creator"]["emailAddress"]

        return ret

class Developer(Base):
    __tablename__ = 'developer'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    site = Column(Integer)
    username = Column(String(64))
    name = Column(String(64))
    email = Column(String(64))
    repo_count = Column(Integer)
    created_at = Column(DateTime)

class Board(Base):
    __tablename__ = 'board'
    iid = Column(Integer, primary_key=True)
    oid = Column(Integer)
    site = Column(Integer)
    name = Column(String(64))

    @staticmethod
    def from_jira(data,ret = None):
        if ret is None:
            ret = Board()
        Convertor.json2db(data,ret,"name")
        Convertor.json2db(data,ret,"id","oid")
        return ret

    def __str__(self):
        return "{} {}".format(self.oid,self.name)


class Contributor(Base):
    __tablename__ = 'contributor'
    iid = Column(Integer, primary_key=True)    
    project = Column(String(64))
    project_oid = Column(Integer)
    developer = Column(String(64))
    developer_oid = Column(Integer)
    site = Column(Integer)
    contribution = Column(Integer)
    created_at = Column(DateTime)

    @staticmethod
    def from_github(data,project):
        ret = []
        for i in data:
            c = Contributor(i,project)
            c.contribution = i["contributions"]
            c.developer = i["login"]
            c.developer_oid = i["id"]
            ret.append(c)
        return ret

    @staticmethod
    def from_gitee(data,project):
        ret = []
        for i in data:
            c = Contributor(i,project)
            c.contribution = i["contributions"]
            c.developer = i["name"]
            ret.append(c)
        return ret

    def __init__(self,json_data,project):
        self.project = project.path
        self.project_oid = project.oid
        self.site = project.site

    def __str__(self):
        return "{}<={}[{}]".format(self.project,self.developer,self.contribution)

class Injector:
    def __init__(self,db_user = "repo", db_password = "", host = "localhost", database = "repo_fellow"):
        self.engine = create_engine("mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8mb4".format(db_user,db_password,host,database))
        DBSession = sessionmaker(bind = self.engine)
        self.db_session = DBSession()
        Convertor.load_schema(Project())
        Convertor.load_schema(Developer())
        Convertor.load_schema(Issue())
    
    def insert_data(self,data):
        for i in data:
            self.db_session.add(i)
        self.db_session.commit()
    
    def get_projects(self,since = None, site = None, ids = None):
        if ids:
            return list(map(lambda x:self.db_session.query(Project).get(x),ids))
        if since and site:
            return self.db_session.query(Project).filter(Project.site == site).filter(Project.iid > since)
        if site:
            return self.db_session.query(Project).filter(Project.site == site)
        return self.db_session.query(Project)

    def get_users(self,since = None, until = None, site = None):
        ret = self.db_session.query(Developer)
        if since:
            ret = ret.filter(Developer.iid >= int(since))
        if until:
            ret = ret.filter(Developer.iid < int(until))
        if site:
            ret = ret.filter(Developer.site == site)
        return ret.all()

    def get_project(self,path):
        return self.db_session.query(Project).filter(Project.path == path).first()

    def get_obj(self,type,iid):
        return self.db_session.query(type).get(iid)

    def list_obj(self,type,filter = None):
        if filter:
            return self.db_session.query(type).filter(filter).all()
        return self.db_session.query(type).all()

    def db_commit(self):
        self.db_session.commit()

    def add_site(self,site_url):
        # http://user:password@url?name&type
        args = re.split(":|#|@|\?|&",site_url)
        if len(args) == 7: # user includes @
            args[1] = args[1] + "@" + args[2]
            for i in range(2,6):
                args[i] = args[i+1]
        site = Site()
        site.name,site.user,site.token,site.url,site.server_type = args[4],args[1][2:],args[2],"{}://{}".format(args[0],args[3]),args[5]
        self.db_session.add(site)
        self.db_session.commit()
        logging.info("server added, iid = {}".format(self.db_session.query(Site).filter(Site.name == site.name).first().iid))

    def get_sites(self):
        return self.db_session.query(Site)

    def get_issues(self,site,project):
        return self.db_session.query(Issue).filter(Issue.site == site,Issue.project == project).all()