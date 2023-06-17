import requests
import os
from sonarqube import SonarQubeClient
from github import Github, UnknownObjectException
from sonarqube.utils.exceptions import ValidationError
from os.path import exists

URL = 'http://localhost:9000'
USERNAME = "admin"
PASSWORD = "Db959000"
sonar = SonarQubeClient(sonarqube_url=URL, username=USERNAME, password=PASSWORD)
TOKEN='***************************' #Place your Github Token Here
GITHUBSEARCHURL='https://api.github.com/search/repositories?q=e-commerceis:featured+language:java&sort=stars&order=desc&per_page=100&page=1'
headers = {'Authorization': 'token ' + TOKEN}
#url = 'https://github.com/roundcube/roundcubemail/releases/latest'
#r = requests.get(url)
#version = r.url.split('/')[-1]
#url2 = ('https://api.github.com/repos/libgdx/libgdx/releases')
#req = requests.get(url2)
#r2=req.json()
#allVersions=[]
#for data in r2:
#    allVersions.append({'tag' : data['tag_name']})
req2 = requests.get(GITHUBSEARCHURL)
result =req2.json()
parent_dir='C:/Programming/Flutter/ProjectRepo/'
items=result['items']
github=Github(login_or_token=TOKEN)
def downloadThenUpload(sonar, parent_dir, github, item):
    repoToBeDownloaded=item
    tagnameUrl= ('https://api.github.com/repos/{name}/releases').format(name=repoToBeDownloaded['full_name'])
    tagNameReq = requests.get(tagnameUrl, headers=headers)
    tagNameList=tagNameReq.json()
    releasesWasEmpty = False
    if tagNameList == []:
        tagnameUrl= ('https://api.github.com/repos/{name}/tags').format(name=repoToBeDownloaded['full_name'])
        tagNameReq = requests.get(tagnameUrl,headers=headers)
        tagNameList=tagNameReq.json()
        releasesWasEmpty = True
    repo=github.get_repo(item['full_name'])
    tagcount=0
    for tagQueue in tagNameList:
        if releasesWasEmpty == False:
            tagName=tagQueue['tag_name']
        else:
            tagName=tagQueue['name']
        directory=repoToBeDownloaded['name']+tagName+'No'+str(tagcount)
        path = os.path.join(parent_dir, directory)
        newPath=os.path.join(path,directory)
        
        havepom = pomCheck(item, repo)
        if havepom:
            makeDirAndClone(parent_dir, repoToBeDownloaded, tagName, directory, path)
            tagcount = uploadToSonar(sonar, tagcount, tagName, directory, path)
            if tagcount == 5:
                break
        else:
            break

def makeDirAndClone(parent_dir, repoToBeDownloaded, tagName, directory, path):
    try:
        os.mkdir(path)
        os.chdir(parent_dir)
        os.system(('git clone --depth 1 --branch {tag_name} {repo_url} {name}').format(tag_name=tagName,repo_url=repoToBeDownloaded['clone_url'],name=directory))
    except Exception as e:
        print(e)

def pomCheck(item, repo):
    containsPom=False
    try:
        havepom=repo.get_contents(path='pom.xml')
        print('{project} contains pom file'.format(project= item['name']))
        containsPom=True
    except UnknownObjectException as e:
        print('{project} does not contain pom file'.format(project= item['name']))

    return containsPom

def uploadToSonar(sonar, tagcount, tagName, directory, path):
    try:
        #-D maven.test.skip=true
        tagcount=tagcount +1
        result = sonar.projects.create_project(project=directory, name=directory, visibility="public")
        os.chdir(path)
        os.system(('mvn clean verify sonar:sonar -D maven.test.skip=true -D sonar.projectKey={projectKey} -D sonar.host.url=http://localhost:9000 -D sonar.login=************************************ -e -up -X').format(projectKey=directory))
        # Instead of ********** create and use your own sonarqube api token from the sonarqube application you installed
        print('downloaded {tag}'.format(tag=tagName))

    except ValidationError as e:
        print(str(e))
    return tagcount

for item in items:
    downloadThenUpload(sonar, parent_dir, github, item) 
