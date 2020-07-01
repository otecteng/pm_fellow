"""repo crawler via command-line.

Usage:
    pmfellow db <command> --conn=<str> [--fellow_db=<str>] [--fellow_db=<str>] [--fellow_password=<str>] [--logging=<debug>]
    pmfellow site <command> [<args>]
    pmfellow project <command> [--site=<id>] [--since=<id>] [--private] [--project=<id>] [--projects=<filter>] [--logging=<debug>]
    pmfellow user <command> [--site=<id>] [--since=<id>] [--until=<id>] [--logging=<debug>]
    pmfellow group <command> [--site=<id>] [<args>]
    pmfellow issue <command> [--site=<id>] [--project=<id>] [--since=<id>] [--limit=<n>] [--until=<date>] [--logging=<debug>]
    pmfellow metric <command> [--site=<id>] [--project=<id>] [--status=<a,b>]
    pmfellow board <command> [--site=<id>] [<args>]

Options: 
    -h,--help 
    --conn=<str>    database connection string
    --site=<id>     repo site id
    --since=<id>    since project iid
    --project=<id>  project iid
    --projects=<filter>  project path like filter
    --private       processing private projects
    --until=<date>   until date of commit
    --status=<a,b>    story status of start and end
    --logging=<debug> logging level

Example:
    pmfellow db init --conn=root:xxx@localhost
    pmfellow site add https://user:password@site?name&type
    pmfellow projects remote owner
    pmfellow projects list
    pmfellow projects import site_id
    pmfellow user import
"""
import os
import sys
import re
import json
import time
import datetime
import logging
from docopt import docopt
from pmfellow.crawler import Crawler
from pmfellow.injector import Injector,Site,Project
from pmfellow.parser import Parser
from pmfellow.repo_mysql import RepoMySQL
from pmfellow.metric import Metric

def get_arg(key,default_value = None, args = None):
    if key in os.environ:
        return os.environ[key]
    if args and key in args:
        return args[key]
    return default_value

def parse_projects_args(arguments,injector):
    if arguments["--project"]:
        return [injector.get_obj(Project,arguments["--project"])]
    if arguments["--since"]:
        return injector.get_projects( site = arguments["--site"],since = arguments["--since"]).all()
    if arguments["--site"] is None:
        logging.error("site or project must be assiged")
    return injector.get_projects( site = arguments["--site"] ).all()

def main():
    arguments = docopt(__doc__, version = 'Repo Fellow')
    if arguments["--logging"] == "debug":
        logging.basicConfig(filename = "log/fellow.log",level = logging.DEBUG,format = "%(asctime)s %(message)s", filemode = 'a')
    else:
        logging.basicConfig(filename = "log/fellow.log",level = logging.INFO,format = "%(asctime)s %(message)s", filemode = 'a')
    logger = logging.getLogger()    
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    command = arguments["<command>"]

    db_user, db_password, db = get_arg("FELLOW_USER","pm"), get_arg("FELLOW_PASSWORD","fellow"), get_arg("FELLOW_DB","pm_fellow")
    injector = Injector(db_user = db_user, db_password = db_password,database = db)
    site = Site()
    site.server_type,site.url,site.token = get_arg("GIT_SERVER"), get_arg("GIT_SITE"), get_arg("GIT_TOKEN")
    
    if arguments["db"]:
        if command == "init":
            if arguments["--conn"]:
                db_user, db_password, db_host = re.split(":|@",arguments["--conn"])
            RepoMySQL().init_db(host = db_host, root_password = db_password)
        return

    if arguments["project"]:
        site = injector.get_obj(Site,arguments["--site"])
        injector = Injector(db_user = db_user, db_password = db_password,database = db)                    
        if command == "list":
            for i in injector.get_projects():
                logging.info(i)
            return
        if command == "import":
            data = Crawler(site,injector).import_projects(arguments["--private"])
            logging.info("total imported projects {}".format(len(data)))
            return
            
    if arguments["site"]:
        if command == "add":
            Injector(db_user = db_user, db_password = db_password,database = db).add_site(arguments["<args>"])
        if command == "list":
            for i in Injector(db_user = db_user, db_password = db_password,database = db).get_sites(): logging.info(i)
        return

    site = injector.get_obj(Site,arguments["--site"])
    
    if arguments["user"]:
        if command == "import":
            data = Crawler(site,injector).import_users()
            logging.info("total imported users {}".format(len(data)))
            return
        if command == "detail":
            data = Crawler(site,injector).detail_users(since = arguments["--since"],until = arguments["--until"])
            return

    if arguments["board"]:
        if command == "import":
            data = Crawler(site,injector).import_boards()
        return

    projects = parse_projects_args(arguments,injector)

    if arguments["issue"]:
        if command == "import":
            until_date = None
            if arguments["--until"]:
                until_date = datetime.datetime.strptime(arguments["--until"], "%Y-%m-%d")
            logging.info("importing issues of {} from ".format(site.name,until_date))
            Crawler(site,injector).import_issues(projects,limit = arguments["--limit"], until = until_date)
            return
        if command == "log":
            for i in projects:
                logging.info("importing issue changes of {} from {}".format(site.name,i.path))
                Crawler(site,injector).import_changes(i)
            return

    if arguments["metric"]:
        if command == "leadtime":
            status_start,status_end = arguments["--status"].split(",")
            for i in projects:
                Metric().leadtime(i.path,status_start=status_start,status_end=status_end)

if __name__ == '__main__':
    main()