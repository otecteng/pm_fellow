import logging
from pmfellow.injector import Project,Issue,Developer,Group

class Parser:
    @staticmethod
    def json_to_db(data,db_class, format="jira", site = None, project = None):
        func = getattr(db_class, "from_{}".format(format))
        if func is None:
            logging.error("can not find function {} in {}".format("from_{}".format(format),db_class))
            return []
        ret = [func(i) for i in data]
        if site is not None:
            [setattr(i,"site",site.iid) for i in ret]
        if project is not None:
            [setattr(i,"project",project.path) for i in ret]
        return ret

    @staticmethod
    def parse_projects(data,format="jira"):
        return list(map(lambda x:Project.from_jira(x),data))

    @staticmethod
    def parse_users(data,format="jira"):
        return list(map(lambda x:Developer.from_jira(x),data))

    @staticmethod
    def parse_groups(data,format="jira"):
        return list(map(Group.from_jira,data))
