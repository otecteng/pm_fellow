# Usage  

1.How to use the package  
1.1 Init database  
```
pmfellow db init --conn=user:password@host
```

1.2 Set db access in env  
```
export FELLOW_USER=xxx
export FELLOW_DB=xxx
export FELLOW_PASSWORD=xxx
```

1.3 Create site  
```
pmfellow site add "https://user:token@site?name&type"
pmfellow site list
```
token: repo private access token  
site: url, host only  
name:  
type: github or gitlab  

1.4 get site developers and groups
```
pmfellow user import --site=site_iid
pmfellow group import --site=site_iid
```

1.5 get site projects  
```
nohup pmfellow project import --site=site_iid &
pmfellow project import --site=site_iid --private
```

1.6 get project size and statistic  
```
pmfellow project update --site=site_iid
pmfellow project contributor --site=site_iid --since=iid
pmfellow project stat --site=site_iid --since=iid
pmfellow project commits --site=site_iid --since=iid

```
update: get size,pushed date  
stat: get weekly commit count of previos year  
commits: get total commits pages of project  

1.7 get project commits  
```
pmfellow commit import --site=site_iid [--since=iid] [--project=project_iid] [--limit=200]
pmfellow tag import --site=site_iid [--since=iid]
pmfellow release import --site=site_iid [--since=iid]
pmfellow branch import --site=site_iid [--since=iid]
pmfellow commit style --site=site_iid --since=iid --style="(.*)#(.*)\s+(.*):\s+(.*?)"
```

# Develop  
## Version Requirement  
Python 3.7  
MySQL 5.7

## Install depemdency
```
pip3 install -r requirements.txt
```

## Run from source code
```
python3 -m pmfellow 
```

## Build package  
```
python3 setup.py sdist bdist_wheel
```
## Deploy package  
```
pip3 install pmfellow.whl
```

## For ubuntu 16  
```
sudo apt-get update
export LC_ALL=C
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt install python3.7
sudo ln -s /usr/bin/python3.7 /usr/bin/python3
sudo apt-get install python3.7-gdbm
sudo apt install python3-pip
pip3 install wheel

```