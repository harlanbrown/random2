#!/bin/bash
#TODO Use $1

COUNT=20

CRACKLIB=/usr/share/dict/cracklib-small

TARGETDIRNAME=robos-$(date +"%s")
mkdir /tmp/${TARGETDIRNAME}

function getImageBlob() {
  curl -L https://robohash.org/${WORDONE}-${WORDTWO}.${FILETYPE} -o /tmp/${TARGETDIRNAME}/${WORDONE}-${WORDTWO}.${FILETYPE}
}

function getWords () {
  # grab random words from cracklib (remove apostrophe-s endings)
  WORDONE=$(shuf -n1 ${CRACKLIB} | sed "s/'s//")
  WORDTWO=$(shuf -n1 ${CRACKLIB} | sed "s/'s//")
}

FILETYPE=png

for i in $(seq 1 ${COUNT}) 
do
  getWords
  getImageBlob
done

