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

1.6 get project issues  and change logs
```
pmfellow issue import --site=site_iid [--since=iid] [--project=project_iid]
pmfellow issue log --site=site_iid [--project=project_iid] [--dump=true]
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

## Docker image  

## Example
Download issue change log and caculate metric lead time    
```
python3 -m pmfellow issue log --site=1 --project=1  
python3 -m pmfellow metric leadtime --site=1 --project=1 --status="IN QA,Done"
```

Want to know the practise of project management? what kind of issue types are used in projects
```
python3 -m pmfellow issue meta --site=1
python3 -m pmfellow board import --site=1
```

