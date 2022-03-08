#!/usr/bin/python3
import os, random, datetime, tempfile
from robohash import Robohash

#targetdir='-'.join(['robos',datetime.datetime.now().strftime('%s')])

size = 12000

targetdir = tempfile.mkdtemp()

def randimg(filename):
    rh = Robohash(filename)
    rh.assemble(roboset='set1', sizex=size, sizey=size)
    pathtoimg = targetdir  + '/' + filename
    with open(pathtoimg, 'wb') as f:
        rh.img.save(f, format='png')
    return pathtoimg

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

count=4
def main():
    for i in range(count):
        docname = '_'.join([randword(1),randword(1)])
        filename = docname + '.png'
        pathtoimg = randimg(filename)
        print(pathtoimg)

main()

