import json

class Metric:
    def leadtime(self,project,start="",end=""):
        with open("{}.json".format(project),"r",encoding="utf-8") as f:
            data = json.load(f)
            for i in data:
                if len(i["logs"]) == 0:
                    continue
                print(i["issue"])
        return
