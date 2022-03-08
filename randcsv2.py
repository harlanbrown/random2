#!/usr/bin/python3
import csv, datetime, json, os, random, requests

HOSTNAME = 'localhost'
PORT = '8080'
AUTH = ('Administrator', 'Administrator')


def randint(places):
    return str(random.randint(0,(10 ** places))).zfill(places)


def randdate():
# start with 2001-01-01
# add 0-7000 days to it
# add 0-86400 seconds to it
# return in "+%Y-%m-%d 00:00:00" format as string
    #dt = datetime.date(2001,1,1)+datetime.timedelta(days=random.randint(0,7000),seconds=random.randint(0,86400))
    dt = datetime.date(2001,1,1)+datetime.timedelta(days=random.randint(0,7000))
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def randword(count):
# http://www.regexprn.com/2008/11/read-random-line-in-large-file-in.html
    filename = '/usr/share/dict/cracklib-small'
    file = open(filename,'r')

#Get the total file size
    file_size = os.stat(filename)[6]

    words = []
    for x in range(count):
#Seek to a place in the file which is a random distance away
#Mod by file size so that it wraps around to the beginning
        file.seek((file.tell()+random.randint(0,file_size-1))%file_size)

#dont use the first readline since it may fall in the middle of a line
        file.readline()
#this will return the next (complete) line from the file
        line = file.readline()

#here is your random line in the file
        word = line.strip()
        words.append(word.replace('\'s',''))
    return ' '.join(words)


def createWorkspaceRoot():
    workspaceRootName = randword(2).replace(' ','-')
    payload = {'entity-type': 'document', 'name': workspaceRootName, 'type': 'WorkspaceRoot', 'properties': {'dc:title': workspaceRootName}}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/default-domain'
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return workspaceRootName


def createWorkspace(workspaceRootName):
    workspaceName = randword(2).replace(' ','-')
    payload = {'entity-type': 'document', 'name': workspaceName, 'type': wstype, 'properties': {'dc:title': workspaceName }}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/default-domain/'  +  workspaceRootName
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return workspaceName


def postCsv(workspaceRootName, workspaceName):
    payload = {'params':{'path':'/default-domain/'+workspaceRootName+'/'+workspaceName}}
    files = {
        'request': (None, json.dumps(payload), 'application/json+nxrequest'),
        'out.csv': ('out.csv', open('/tmp/out.csv', 'rb'), 'text/csv')
        }
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/site/automation/CSV.Import'
    auth = AUTH
    response = requests.post(url, files=files, auth=auth)
    return response

def getSizes():
    sizes=[]
    sizevals=["Big and Tall", "L, XL, XXL", "Large and Small", "Large", "Medium", "Small", "large", "medium", "small", "xl, xxl, xs, x, m"]
    #for i in range(0,int(numpy.random.normal(2,1,1))):
    for i in range(0,random.randrange(3)):
        size = random.choice(sizevals)
        if size:
            if size not in sizes:
                sizes.append(size)
    return sizes


def makeRecord(ecm_type):
    wordone = randword(1)
    wordtwo = randword(1)
    desc = randword(3)
    ecm_name = ' '.join([wordone,wordtwo])
    dc_title = ecm_name
    dc_description = desc
    sizes = '|'.join(getSizes())
    return [ecm_name,ecm_type,dc_title,dc_description,sizes]


csvfilename = '/tmp/out.csv'
lvl1 = 1
lvl2 = 8
wstype = 'Workspace'
doctype = 'File'
randWorkspaceRoot = False
def main():
    if randWorkspaceRoot:
        wsr = createWorkspaceRoot()
    else:
        wsr = 'workspaces'
    for i in range(lvl1):
        with open(csvfilename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['name','type','dc:title','dc:description','custom:stringList'])
            for j in range(lvl2):
                writer.writerow(makeRecord(doctype))
        ws = createWorkspace(wsr)
        response = postCsv(wsr,ws)
        print('    '  +  ws + '    ' + str(response))
main()


