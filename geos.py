#!/usr/bin/python3
import json, requests

HOSTNAME = 'localhost'
PORT = '8080'
AUTH = ('Administrator', 'Administrator')


def createWorkspaceRoot():
    payload = {'entity-type': 'document', 'name': workspaceRootName, 'type': 'WorkspaceRoot', 'properties': {'dc:title': workspaceRootName}}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/default-domain'
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return workspaceRootName


def checkDocumentPath(path):
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/'  +  path
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.get(url, auth=auth)
    return response


def createWorkspace(parentPath, workspaceName):
    payload = {'entity-type': 'document', 'name': workspaceName, 'type': 'Workspace', 'properties': {'dc:title': workspaceName }}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/path/'  +  parentPath
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return response


def getMessages():
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/ui/i18n/messages.json'
    auth = AUTH
    response = requests.get(url, auth=auth)
    return response.json()


def getContinents():
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/directory/continent'
    auth = AUTH
    response = requests.get(url, auth=auth)
    return response.json()['entries']


def getCountries():
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/directory/country?pageSize=250'
    auth = AUTH
    response = requests.get(url, auth=auth)
    return response.json()['entries']


def main():
    messages = getMessages()
    continents = getContinents()
    countries = getCountries()

    workspaceRoot = 'workspaces'
    for i in continents:
        label = messages[i['properties']['label']]
        r = checkDocumentPath('/'.join(['default-domain',workspaceRoot,label]))
        if r.status_code == 404:
            r = createWorkspace('/'.join(['default-domain',workspaceRoot]),label)

    for i in countries:
        cid = i['properties']['id']
        parent = i['properties']['parent']
        label = messages[i['properties']['label']]
        parentWorkspace = '/'.join(['default-domain',workspaceRoot,parent])
        r = checkDocumentPath(parentWorkspace)
        if r.status_code != 404:
            newWorkspace = '/'.join([parentWorkspace,label])
            r = checkDocumentPath(newWorkspace)
            if r.status_code == 404:
                r = createWorkspace(parentWorkspace,label)
                print(r)


main()
