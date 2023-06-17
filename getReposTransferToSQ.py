import requests
import os
from github import Github, UnknownObjectException
from sonarqube import SonarQubeClient
from sonarqube.utils.exceptions import ValidationError
from os.path import exists
GAME='game-development'
GAMEdir='Game'
ECOMMERCE='e-commerce'
ECOMdir='E-c-o-M'
url = 'http://localhost:9000'
username = "admin"
password = "********************"
sonar = SonarQubeClient(sonarqube_url=url, username=username, password=password)
GithubSearchURL='https://api.github.com/search/repositories?q={topic}is:featured+language:java&sort=stars&order=desc&per_page=100&page=1'.format(topic=ECOMMERCE)
req2 = requests.get(GithubSearchURL)
result =req2.json()
parent_dir='C:/Programming/Flutter/ProjectRepo/'
github=Github(login_or_token='****************************')
repoQueue =0
repoToBeDownloaded=result['items'][repoQueue]
items=result['items']
#print(items)
#list=[]
#for item in items:
#   if item['stargazers_count'] >30:
#        list.append({'name':item['name'], 'stargazers':item['stargazers_count']})
#print(list)
for item in items:
    if item['stargazers_count'] >12:
        directory = str(item['stargazers_count']) + ECOMdir +item['name']
        path = os.path.join(parent_dir, directory)
        newPath=os.path.join(path,directory)
        repo=github.get_repo(item['full_name'])
        containsPom = False
        try:
            havepom=repo.get_contents(path='pom.xml')
            print('{project} contains pom file'.format(project= item['name']))
            containsPom=True
        except UnknownObjectException as e:
            print('{project} does not contain pom file'.format(project= item['name']))
        if containsPom:
            try:
                os.mkdir(path)
                os.chdir(parent_dir)
                os.system(('git clone {repo_url} {name}').format(repo_url=item['clone_url'],name=directory))
                repoQueue=repoQueue + 1 
            except Exception as e:
                print(e)
            try:
                #-D maven.test.skip=true 
                result = sonar.projects.create_project(project=directory, name=directory, visibility="public")
                os.chdir(path)
                os.system(('mvn clean verify sonar:sonar -D maven.test.skip=true -D sonar.projectKey={projectKey} -D sonar.host.url=http://localhost:9000 -D sonar.login=************************************ -e -up -X').format(projectKey=directory))
                print('downloaded {name}'.format(name=directory))
            except ValidationError as e:
                print(str(e))   
        print('************************************************************************************************')
        print(repoQueue)
        print('************************************************************************************************') 