#!/usr/bin/python3
import csv, datetime, json, os, random, requests, string
from robohash import Robohash


# createImageBlob's gonna need a S3 Direct Upload capability

HOSTNAME = 'localhost'
PORT = '8080'
AUTH = ('Administrator', 'Administrator')
USEBLOBS = True
FORMAT = 'png'
MIMETYPE = 'image/png'


def md5sum(filename, blocksize=65536):
    h = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            h.update(block)
    return h.hexdigest()


def randimg(filename):
    size = 300
    rh = Robohash(filename)
    rh.assemble(roboset='set1', sizex=size, sizey=size)
    with open('/tmp/' + filename, 'wb') as f:
        rh.img.save(f, format=FORMAT)
    return '/tmp/' + filename


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


def makeRecord(ecm_type):
    wordone = randword(1)
    wordtwo = randword(1)
    desc = randword(3)
    ecm_name = '-'.join([wordone,wordtwo])
    dc_title = ecm_name
    dc_description = desc.replace(' ','_')
    return [ecm_name,ecm_type,dc_title,dc_description]


def getBatchId():
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/upload'
    auth = AUTH
    response = requests.post(url, auth=auth)
    return response.json()['batchId']


def createImageBlob(batchid, filename, mimetype, imgfile):
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/upload/' + batchid + '/0'
    headers = {'X-File-Type': mimetype, 'X-File-Name': filename}
    auth = AUTH
    response = requests.post(url, data=open(imgfile,'rb'), headers=headers, auth=auth)
    return response


def createDocument(workspaceRootName, workspaceName, docname, doctype, description, batchid):
    if batchid:
        payload =  {'entity-type': 'document', 'name': docname, 'type': doctype, 'properties': {'dc:title': docname, 'dc:description': description, 'file:content': {'upload-batch': batchid, 'upload-fileId': '0'}}}
    else:
        payload =  {'entity-type': 'document', 'name': docname, 'type': doctype, 'properties': {'dc:title': docname, 'dc:description': description }}

    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/default-domain/' + workspaceRootName + '/' + workspaceName
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    if response:
        print('/nuxeo/api/v1/path/default-domain/' + workspaceRootName + '/' + workspaceName + '/' + docname)
    return response


def checkDocType(doctype):
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/config/types/' + doctype
    auth = AUTH
    response = requests.get(url, auth=auth)
    if response.status_code == 200 :
        return True
    else:
        return False


# 
# sep blob creation from doc creation
# handle batchid for local and s3
# s3 req boto and bucket info

lvl1 = 10
lvl2 = 10
wstype = 'Workspace'
doctype = 'File'
randomiz = False
randWorkspaceRoot = False
def main():
    if checkDocType(doctype):
        if randWorkspaceRoot:
            wsr = createWorkspaceRoot()
        else:
            wsr = 'workspaces'
        for i in range(lvl1):
            ws = createWorkspace(wsr)
            print(ws)
            for j in range(lvl2):
                b = getBatchId()
                r = makeRecord(doctype)
                if randomiz:
                    k = 32
                    docname = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
                else:
                    docname = r[0]
                if USEBLOBS:
                    filename = docname + '.' + FORMAT
                    pathtoimg = randimg(filename)
                    img = createImageBlob(b, filename, MIMETYPE, pathtoimg)
                    print(img)
                else:
                    b = None
                doc = createDocument(wsr, ws, docname, doctype, r[3], b)
                print(doc)


main()


