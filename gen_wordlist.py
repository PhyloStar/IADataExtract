#usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import os
from nltk.corpus import words

eng_list = list(set([l.lower() for l in words.words()]))
eng_list = set(eng_list + [ten+'-'+digit for ten in ['twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety'] for digit in ['one','two','three','four','five','six','seven','eight','nine']])
#inflected forms not included

langs = {}

for l in open('lang_key.csv','r'):
    line = l.split('\t')
    #for narrow language key; if wide, line[4]
    #langs[line[0]]=line[3]
    if '_' in line[3]:
        langs[line[0]] = line[4]
    else:
        langs[line[0]] = line[3]


def cdial_split(s):
    chunks = []
    ss = s.split()
    counter = 0
    for s in ss:
        if counter == 1:
            chunks[-1] = chunks[-1] + ' ' + s
        if counter == 0:
            chunks.append(s)
        if s.startswith('ʻ'):
            counter = 1
        if s.startswith('ʼ'):
            counter = 0
    return(chunks)


forms = []
for fn in os.listdir('html'):
    f = open('html/'+fn,'r')
    texts=f.read()
    f.close()
    texts = texts.split('<number>')
    for text in texts:
        if '</number>' in text:
            entry=text.split('</number')[0]
        head = text.split('<br>')[0]
        head = cdial_split(head)
        text = text.split()
        counter = 0
        reflexes = []
        etyms = [e for e in text if e.startswith('<b>') or e.startswith('*<b>')]
        if len(etyms) > 0:
            etym = etyms[0]
            etym = re.sub('\<[^\<]*\>|\d','',etym)
        else:
            etym = ''
        glosses = [e for e in head if 'ʻ' in e]
        glosses_ = []
        for g in glosses:
            g_ = ''
            for w in re.split(r'[\s|-]',g):
                #get rid of word in each gloss if not in English
                if re.sub('[\W|ʻ|ʼ]+','',w) in eng_list or re.sub('[\W|ʻ|ʼ]+','',w).strip('s') in eng_list or re.sub('[\W|ʻ|ʼ]+','',w).strip('es') in eng_list or re.sub('[\W|ʻ|ʼ]+','',w).strip('ing') in eng_list or re.sub('[\W|ʻ|ʼ]+','',w).strip('ing')+'e' in eng_list or re.match('\d+',w):
                    g_ += re.sub('[\W|ʻ|ʼ]+','',w)+' '
                    #glosses_.append(re.sub('[\W|ʻ|ʼ]+','',w))
            glosses_.append(g_.strip())
        glosses_ = [g for g in glosses_ if g != '']
        for l in range(len(text)-1):
            if text[l].endswith('.') and text[l].split('.')[-2]+'.' in langs.keys() and text[l+1].startswith('<i>'):
                if '&' not in text[l+1] and '*' not in text[l+1]:
                    reflexes.append([langs[text[l].split('.')[-2]+'.'],text[l+1]])
                    counter += 1
        if counter >= 0:
            if etym != '':# and etym[0] != '*':
                for r in reflexes:
                    forms.append(tuple([r[0],re.sub(r"\<[^\>]*\>|\(|\)|\_|\/|\,|\;|\:|\.|\?|\]|\-|\\",'',r[1]).lower(),etym.strip('*').strip(',').strip(':').strip(';').lower(),', '.join(glosses_),entry,fn]))



f = open('cdial_wordlist.tsv','w')
for l in sorted(set(forms)):
    print('\t'.join(l),file=f)


f.close()
