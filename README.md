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
pmfellow project import --site=site_iid
```

1.6 get project issues  
```
pmfellow issue import --site=site_iid [--since=iid] [--project=project_iid] 
```

# JIRA SaaS User  
## How to generate a api-token  
```
https://id.atlassian.com/manage-profile/security/api-tokens
```

## How to generate OAuth2 token
```
JiraClientFactory.oauth_jira(cls,server,app_key,rsa)
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