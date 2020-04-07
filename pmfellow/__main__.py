"""repo crawler via command-line.

Usage:
    pmfellow db <command> --conn=<str> [--fellow_db=<str>] [--fellow_db=<str>] [--fellow_password=<str>] [--logging=<debug>]
    pmfellow site <command> [<args>]
    pmfellow project <command> [--site=<id>] [--since=<id>] [--private] [--projects=<filter>] [--logging=<debug>]
    pmfellow user <command> [--site=<id>] [--since=<id>] [--until=<id>] [--logging=<debug>]
    pmfellow group <command> [--site=<id>] [<args>]       
    pmfellow commit <command> [--site=<id>] [--project=<id>] [--since=<id>] [--limit=<n>] [--until=<date>] [--style=<str>] [--logging=<debug>]
    pmfellow event <command> [--site=<id>] [--project=<id>] [--since=<id>] [--limit=<n>] [--until=<date>]
    pmfellow pr <command> [--site=<id>] [--since=<id>] [--logging=<debug>]
    pmfellow tag <command> [--site=<id>] [--project=<id>] [--since=<id>] [--limit=<n>] [--logging=<debug>]
    pmfellow release <command> [--site=<id>] [--project=<id>] [--since=<id>] [--logging=<debug>]
    pmfellow branch <command> [--site=<id>] [--project=<id>] [--since=<id>] [--limit=<n>] [--logging=<debug>]

Options: 
    -h,--help 
    --conn=<str>    database connection string
    --site=<id>     repo site id
    --since=<id>    since project iid
    --project=<id>  project iid
    --projects=<filter>  project path like filter
    --private       processing private projects
    --until=<date>   until date of commit
    --style=<str>    commit message style check string
    --logging=<debug> logging level

Example:
    pmfellow db init --conn=root:xxx@localhost
    pmfellow site add https://user:password@site?name&type
    pmfellow projects remote owner
    pmfellow projects list
    pmfellow projects import site_id
    pmfellow commit update *
    pmfellow commit update project
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
        return injector.get_projects( site = arguments["--site"],since = arguments["--since"])
    if arguments["--site"] is None:
        logging.error("site or project must be assiged")
    return injector.get_projects( site = arguments["--site"] )

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
        projects = parse_projects_args(arguments,injector).all()
        if command == "update":
            data = Crawler(site,injector).update_projects(projects)
        if command == "stat":
            data = Crawler(site,injector).stat_projects(projects)
        if command == "commits":
            data = Crawler(site,injector).commits_projects(projects)            
        if command == "contributor":
            data = Crawler(site,injector).contributor_projects(projects)
            
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

    projects = parse_projects_args(arguments,injector)
    if arguments["pr"]:
        if command == "import":
            Crawler(site,injector).import_pull_requests(projects)
            return

    if arguments["commit"]:
        if command == "import":
            until_date = None
            if arguments["--until"]:
                until_date = datetime.datetime.strptime(arguments["--until"], "%Y-%m-%d")
            logging.info("importing commits of {} from ".format(site.name,until_date))
            Crawler(site,injector).import_commits(projects,limit = arguments["--limit"], until = until_date)
        if command == "stat":
            logging.info("stat commits of {}".format(site.name))
            Crawler(site,injector).stat_commits(projects,limit = arguments["--limit"])
        if command == "style":
            logging.info("check style of commits of {}".format(site.name))
            for project in projects:
                for commit in injector.get_commits(project=project):
                    commit.style_check(re.compile(arguments["--style"]))
            injector.db_commit()
            return


    if arguments["event"]:
        if command == "import":
            logging.info("importing event of {} from ".format(site.name))
            Crawler(site,injector).import_events(projects,limit = arguments["--limit"])

    if arguments["tag"]:
        if command == "import":
            logging.info("importing tags of {}".format(site.name))
            Crawler(site,injector).get_tags(projects)
        return

    if arguments["release"]:
        if command == "import":
            logging.info("importing release of {}".format(site.name))
            Crawler(site,injector).import_releases(projects)
        return

    if arguments["branch"]:
        if command == "import":
            logging.info("importing branch of {}".format(site.name))
            Crawler(site,injector).import_branches(projects)
        return

    if arguments["group"]:
        if command == "import":
            # can not import more than 1000 groups now
            data = Crawler.create_client(site).get_groups()
            injector.insert_data(Parser.parse_groups(data,site.server_type))
            logging.info("total imported groups {}".format(len(data)))
        return

if __name__ == '__main__':
    main()