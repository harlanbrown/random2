#!/usr/bin/python
import csv,os,random,requests,json

HOSTNAME = 'localhost'
PORT = '8080'
AUTH = ('Administrator', 'Administrator')


def randword(count):
# http://www.regexprn.com/2008/11/read-random-line-in-large-file-in.html
    filename="/usr/share/dict/cracklib-small"
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

def createUser(username,firstname,lastname,company,email):
    payload =  {'entity-type': 'user', 'id': username, 'properties': {'username':username,'firstName':firstname,'lastName':lastname,'company':company,'email':email,'groups':['members']}}
    data_json = json.dumps(payload)
    url = 'http://' + HOSTNAME + ':' + PORT + '/nuxeo/api/v1/user'
    headers = {'Content-Type': 'application/json'}
    auth = AUTH
    response = requests.post(url, data=data_json, headers=headers, auth=auth)
    return response


csvfilename='/tmp/users.csv'
csvfilename2='/tmp/user2group.csv'
users=[]
def main():
    with open(csvfilename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['username','firstname','lastname','email','company'])

        ruct=0
        for i in range(10000):
            if (random.randint(0,4) == 4):
                if (ruct < 8):
                    emailSuff='ru'
                    ruct=ruct+1
            else:
                emailSuff='com'
            company='compone'
            firstname=randword(1)
            lastname=randword(1)
            username=firstname[:1]+lastname
            emailAddr=username+'@'+company+'.'+emailSuff
            writer.writerow([username,'',firstname,lastname,company,emailAddr])
            users.append(username)
            createUser(username,firstname,lastname,company,emailAddr)
        ruct=0
        for i in range(10):
            if (ruct < 8):
                emailSuff='ru'
                ruct=ruct+1
            else:
                emailSuff='com'
            company='comptwo'
            firstname=randword(1)
            lastname=randword(1)
            username=firstname[:1]+lastname
            emailAddr=username+'@'+company+'.'+emailSuff
            writer.writerow([username,'',firstname,lastname,company,emailAddr])
            users.append(username)
            createUser(username,firstname,lastname,company,emailAddr)
  
        educt=0
        for i in range(3000):
            if (random.randint(0,1) == 1):
                if (ruct < 1800):
                    emailSuff='edu'
                    ruct=ruct+1
            else:
                emailSuff='com'
            company='comptre'
            firstname=randword(1)
            lastname=randword(1)
            username=firstname[:1]+lastname
            emailAddr=username+'@'+company+'.'+emailSuff
            writer.writerow([username,'',firstname,lastname,company,emailAddr])
            users.append(username)
            createUser(username,firstname,lastname,company,emailAddr)
  
        for i in range(150):
            emailSuff='fr'
            company='compfor'
            firstname=randword(1)
            lastname=randword(1)
            username=firstname[:1]+lastname
            emailAddr=username+'@'+company+'.'+emailSuff
            writer.writerow([username,'',firstname,lastname,company,emailAddr])
            users.append(username)
            createUser(username,firstname,lastname,company,emailAddr)

    with open(csvfilename2, 'w') as csvfile2:
        writer = csv.writer(csvfile2, delimiter=',')
        writer.writerow(['userId','groupId'])
        for user in users:
            writer.writerow([user,'members'])


main()  
