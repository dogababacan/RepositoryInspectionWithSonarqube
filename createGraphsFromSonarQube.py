from sonarqube import SonarQubeClient
from sonarqube.utils.exceptions import ValidationError
from sklearn.cluster import KMeans
from sklearn import preprocessing
import sklearn.cluster as cluster
import sklearn.metrics as metrics
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display
import copy

GAME='game-development'
GAMEDIR='Game'
ECOMMERCE='ecommerce'
ECOMDIR='E-c-o-M'
type=ECOMDIR
def getAllDataToDF(type):
    def remove_prefix(text, prefix, starcount):
        return text[len(prefix)+starcount:]
    def sortKeys(myDict):
        myKeys = list(myDict.keys())
        myKeys.sort()
        sorted_dict = {i: myDict[i] for i in myKeys}
        return sorted_dict
    url = 'http://localhost:9000'
    username = "admin"
    password = "**********"
    sonar = SonarQubeClient(sonarqube_url=url, username=username, password=password)
    projects = sonar.projects.search_projects()
    measures=[]
    apps={}
    appsWOncloc={}
    appsDivNcloc={}
    appsNormalized={}
    count=0
    projectTypes= [type]
    for projectType in projectTypes:
        for project in projects['components']:
            if projectType in project['key']:
                location = str(project['key']).find(projectType)
                app={}
                try:
                    req= sonar.measures.get_component_with_specified_measures(component=project['key'],metricKeys='functions,code_smells,bugs,vulnerabilities,duplicated_lines,lines,security_hotspots,blocker_violations,critical_violations,major_violations,classes,cognitive_complexity,complexity,class_complexity,file_complexity,comment_lines,executable_lines_data,file_complexity_distribution,directories,statements,ncloc,generated_ncloc,class_complexity,function_complexity,new_technical_debt')#,ncloc_language_distribution,effort_to_reach_maintainability_rating_a
                    if req!=[] and req['component']['measures']!=[]:
                        measures.append(req)
                        values={}
                        for data in measures[count]['component']['measures']:
                            values[data['metric']]=data['value']
                        values['stars']= str(project['key'])[0:location]
                    # if projectType=='E-c-o-M':
                    #    values['type']='Ecommerce'
                    #else:
                    #    values['type']=projectType 
                        projectName=remove_prefix(project['key'],projectType,location)
                        values=sortKeys(values)
                        app[projectName]= values
                        apps[projectName]= values
                        apps= sortKeys(apps)
                        appsWOncloc[projectName]=copy.deepcopy(values)
                        appsNormalized[projectName]=copy.deepcopy(values)
                        app= sortKeys(app)
                        ncloc=app[projectName]['ncloc']
                        for metric in app[projectName]:
                            if metric=='stars' or metric=='ncloc' or metric == 'development_cost':
                                val=app[projectName][metric]
                                app[projectName][metric]=float(val)
                            else:    
                                val=app[projectName][metric]
                                app[projectName][metric]=float(val)/float(ncloc)
                        appsDivNcloc[projectName]=app[projectName]
                        count = count +1
                except ValidationError as e:
                    print(e)
    appsDivNcloc= sortKeys(appsDivNcloc)
    return appsDivNcloc, appsWOncloc,appsNormalized

appsDivNcloc, appsNonNcloc,appsNormalized = getAllDataToDF(type)
writer = pd.ExcelWriter(type+'All.xlsx', engine='xlsxwriter')
df=pd.DataFrame(appsDivNcloc).T.astype(float)
df_NonNormalized=pd.DataFrame(appsNonNcloc).T.astype(float)
dftoNormalize=pd.DataFrame(appsNormalized).T.astype(float)
df_normalized=(dftoNormalize - dftoNormalize.min()) / (dftoNormalize.max() - dftoNormalize.min())
df.to_csv(type+'12', encoding='utf-8', index=False)

df_NonNormalized.to_excel(writer, sheet_name='OriginalData')
df.to_excel(writer, sheet_name='DivByNclocData')
df_normalized.to_excel(writer, sheet_name='NormalizedData')
#display(df_normalized)
writer.close()
#df=pd.DataFrame(appsDivNcloc).T
#display(df)
#plotter(df)