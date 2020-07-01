import json
from datetime import datetime
class Metric:
    def leadtime(self,project,status_start="IN DEV",status_end="READY FOR QA"):
        with open("{}.json".format(project),"r",encoding="utf-8") as f:
            data = json.load(f)
            stories = []
            for i in data:
                if len(i["logs"]) == 0:
                    continue
                start = self.get_status_time(i,status_start)
                end = self.get_status_time(i,status_end,reverse=True)
                if start and end:
                    start = datetime.strptime(start[:19], '%Y-%m-%dT%H:%M:%S')
                    end = datetime.strptime(end[:19], '%Y-%m-%dT%H:%M:%S')
                    stories.append("{}:{},{},{:.2f}".format(i["issue"],start,end,(end-start).days + (end-start).seconds/(60*60*24)))
            with open("{}.csv".format(project),"w",encoding="utf-8") as f:
                for i in stories:
                    f.write(i + "\r\n")
            print("total: {}, stories with start end:{}".format(len(data),len(stories)))
        return

    def get_status_time(self,issue,status,reverse=False):
        logs = list(map(lambda x : x.split(","),issue["logs"]))
        if reverse:
            logs.reverse()
        for i in logs:
            if status == i[2]:
                return i[0]
        return None
