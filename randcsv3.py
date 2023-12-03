#!/usr/bin/python3
import csv, datetime, json, os, random, string

#https://nixos.wiki/wiki/Python
#python -m venv .venv
#source .venv/bin/activate
#echo requests > requirements.txt
#Robohash
#Pillow==9.5.0
#pip install -r requirements.txt
#python -m venv .venv; source .venv/bin/activate; pip install requests

import requests

HOSTNAME = 'localhost'
PORT = '8080'
AUTH = ('Administrator', 'Administrator')
DOCMODE = False
WSTYPE = 'Workspace'
DOCTYPE = 'File'
POSTCSV = True
CREATEWORKSPACEROOT = False

# curl -n localhost:8080/nuxeo/api/v1/path/default-domain/workspaces -d '{"entity-type":"document","name":"ws1","type":"Workspace","properties":{"dc:title":"ws1"}}' -H content-type:application/json
# BATCH=$(curl -n -X POST localhost:8080/nuxeo/api/v1/upload | sed -e 's/{"batchId":"//' -e 's/"}//');
# curl -n -X POST localhost:8080/nuxeo/api/v1/upload/${BATCH}/0 -H X-File-Name:out.csv -H X-File-Type:text/csv -T /tmp/out.csv
# curl -n -X POST localhost:8080/nuxeo/api/v1/upload/${BATCH}/0/execute/CSV.Import -d '{"params":{"path":"/default-domain/workspaces/ws1","documentMode":false}}' -H content-type:application/json

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
    filename = '/nix/store/kygh7jbmia2k9pfvm3dghz1rva1wad6q-cracklib-2.9.8/share/cracklib/cracklib-small'
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


def makeRecord(ecm_type):
    wordone = randword(1)
    wordtwo = randword(1)
    desc = randword(3)
    ecm_name = '-'.join([wordone,wordtwo])
    dc_title = ecm_name
    dc_description = desc
    n = getNature()
    if n:
        dc_nature = n
    else:
        dc_nature = ''
    return [ecm_name,ecm_type,dc_title,dc_description,dc_nature]


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
    payload = {'entity-type': 'document', 'name': workspaceName, 'type': WSTYPE, 'properties': {'dc:title': workspaceName }}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/default-domain/'  +  workspaceRootName
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return workspaceName


def postCsv(workspaceRootName, workspaceName):
    payload = {'params':{'path':'/default-domain/'+workspaceRootName+'/'+workspaceName, 'documentMode': DOCMODE}}
    files = {
        'request': (None, json.dumps(payload), 'application/json+nxrequest'),
        'out.csv': ('out.csv', open(csvfilename, 'rb'), 'text/csv')
        }
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/automation/CSV.Import'
    auth = AUTH
    response = requests.post(url, files=files, auth=auth)
    return response


def checkDocType(doctype):
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/config/types/' + doctype
    auth = AUTH
    response = requests.get(url, auth=auth)
    if response.status_code == 200 :
        return True
    else:
        return False


def getNature():
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/directory/nature'
    auth = AUTH
    response = requests.get(url, auth=auth)
    if response.status_code == 200 :
        return random.choice(response.json()['entries'])['id'] 
    else:
        return False


csvfilename = '/tmp/out' + ''.join(random.choices(string.ascii_letters + string.digits, k=8)) +'.csv'
lvl1 = 100
def main():
    with open(csvfilename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['name','type','dc:title','dc:description','dc:nature'])
        for i in range(lvl1):
            writer.writerow(makeRecord(DOCTYPE))
    if POSTCSV:
        if CREATEWORKSPACEROOT:
            pass
        else:
            workspaceRoot = 'workspaces'
            workspace = createWorkspace(workspaceRoot)
            response = postCsv(workspaceRoot,workspace)
            print(str(workspace))
            print(str(response))
    else:
        print(' '.join(['csv only:',csvfilename]))
            
main()

