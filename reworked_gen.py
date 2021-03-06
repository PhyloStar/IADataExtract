#usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import re
from collections import defaultdict
import os

dname='solo'
outfn='subset.tsv'
dname='html'
outfn='all.tsv'

langs = {}

for l in open('lang_key.csv','r'):
    line = l.split('\t')
    #for narrow language key; if wide, line[4]
    #langs[line[0]]=line[3]
    if '_' in line[3]:
        langs[line[0]] = line[4]
    else:
        langs[line[0]] = line[3]

def process_suppl_meanings(s):

    supplMeanings = re.split(r'Addenda:',s)[0]
    supplMeanings = re.sub('\*','',supplMeanings)
    supplMeanings = re.split(r';',supplMeanings)
    supplMeanings = [s.strip() for s in supplMeanings if s != '']
    for sp1 in supplMeanings:
        currLang=''
        currMeaning=''
        if 'ʼ,' in sp1:
            frags = sp1.split(", ")
            frags = [f.strip() for f in frags if f != '']
            currWord = ''
            currForm = ''

            for l in range(len(frags)):
                sp2 = frags[l]
                if sp2[0:sp2.find('.')]+'.' in langs.keys():
                    currLang = langs[sp2[0:sp2.find('.')]+'.']
                if re.match(r'[a-z]\.',sp2):
                    currForm = re.search(r'([a-z]\.)', sp2).group(1)
                if '<i>' in sp2 and currWord == '':
                    currWord = re.split('.*<i>(.*)</i>.*',sp2)[1]
                if 'ʻ' in sp2 and 'ʼ' in sp2 and currWord != '':
                    try:
                        currMeaning = re.search(currWord+'[^ʻ]+ʻ ([^ʼ]+) ʼ',sp2).group(1)
                    except Exception:
                        pass
                else:
                    if l<len(frags)-1 and 'ʻ' in sp1 and 'ʼ' in sp1:
                        try:
                            if re.search(currWord+'[^ʻ]+ʻ ([^ʼ]+) ʼ',sp1) != None:
                                currMeaning = re.search(currLang+'.+'+currWord+'[^ʻ]+ʻ ([^ʼ]+) ʼ',sp1).group(1)
                        except Exception:
                            pass
                if currWord != '' and currLang != '':
                    finalMeanings.append(tuple([currLang,currWord,currForm,currMeaning,mainWord,mainMeaning,entry,fn]))
                    currWord = ''
                    currMeaning = ''
                    currForm = ''

        else:
            frags = sp1.split()
            currWord = ''
            currForm = ''

            for l in range(len(frags)):
                sp2 = frags[l]
                # if sp2 == '--':
                #     break

                if re.sub(r',','',sp2) in langs.keys():
                    currLang = langs[re.sub(r',','',sp2)]
                if sp2[0:sp2.find('.')]+'.' in langs.keys() and currLang == '':
                    currLang = langs[sp2[0:sp2.find('.')]+'.']
                if re.match(r'[a-z]\.',sp2):
                    currForm = sp2
                if '<i>' in sp2 and currWord == '':
                    currWord = re.split('.*<i>(.*)</i>.*',sp2)[1]
                if 'ʻ' in sp2 and '<i' not in sp2:
                    try:
                        currMeaning = re.search(currWord+'[^ʻ]+ʻ (' + frags[l+1] + '[^ʼ]*) ʼ',sp1).group(1)
                    except Exception:
                        pass
                    # currMeaning = currMeaning[2:][:-2]
                    if currWord != '':
                        if currLang != '':
                            finalMeanings.append(tuple([currLang,currWord,currForm,currMeaning,mainWord,mainMeaning,entry,fn]))
                        else:
                            currWord = ''
                            currMeaning = ''
                            currForm = ''

        


    return(sm)

def cdial_split(s):
    chunks = []
    ss = s.split()
    counter = 0
    for s in ss:
        if counter == 1:
            if 'ʻ' in s:
                chunks[-1] = chunks[-1] + ' ʻ'
            elif 'ʼ' in s:
                chunks[-1] = chunks[-1] + ' ʼ'
            else:
                chunks[-1] = chunks[-1] + ' ' + s
        if counter == 0:
            chunks.append(s)
        if 'ʻ' in s:
            counter = 1
        if 'ʼ' in s:
            counter = 0
    return(chunks)

# <number>(\d+)<\/number> <b>([^ ]+)<\/b> ([^ʼ|^ʻ]+\.) ʻ ([^ʼ]+) ʼ
# re.split(r'(\d+)<\/number> <b>([^ ]+)<\/b> ([^ʼ|^ʻ]+\.) ʻ ([^ʼ]+) ʼ',text)

forms = []

supplMeanings=[]
finalMeanings=[]
finalMeanings.append(tuple(["Lang","Word","Word Form","Supp Meaning","Main Word","Main Meaning","Entry","File"]))

fnCount=0
htmlFiles=[f for f in os.listdir(dname) if re.match(r'.*\.html$', f)]
for fn in htmlFiles:
    
    mainMeaning=''
    fnCount+=1
    # print(fnCount,': Processing ' + dname+'/'+fn)
    f = open(dname+'/'+fn,'r')
    texts=f.read()
    f.close()
    texts = texts.split('<number>')
    for text in texts:
        if '</number>' in text:
            entry=text.split('</number')[0]
            # Replace newlines with spaces
            text = re.sub('\n',' ',text)
            text = re.sub('  ',' ',text)
            # Delete any text within parens
            text = re.sub('<br>','',re.sub('&.t;','',re.sub('\([^\)]+\)','',text)))
            firstMeaning = re.split(r'(\d+)<\/number>[^<]+<b>([^ ]+)<\/b> ([^ʼ|^ʻ]+\.) ʻ ([^ʼ]+) ʼ',text)
            if len(firstMeaning)==6:
                try:
                    mainWord=firstMeaning[2]
                    mainMeaning=firstMeaning[4]
                    process_suppl_meanings(firstMeaning[5])
                except Exception:
                    pass
            else:
                firstMeaning = re.split(r'(\d+)<\/number>[^<]+<b>([^ ]+)<\/b>[^ʻ]+ʻ ([^ʼ]+) ʼ',text)
                try:
                    mainWord=firstMeaning[2]
                    mainMeaning=firstMeaning[3]
                    process_suppl_meanings(firstMeaning[4])
                except Exception:
                    pass

'''
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
                w_ = w
                clean_= re.sub('[\W|ʻ|ʼ]+','',w_)
                # if clean_ in eng_list or clean_.strip('s') in eng_list or clean_.strip('es') in eng_list or clean_.strip('ing') in eng_list or clean_.strip('est') in eng_list or clean_.strip('d') in eng_list or clean_.strip('ing')+'e' in eng_list or re.match('\d+',w):
                #    g_ += re.sub('[\W|ʻ|ʼ|,|-]+','',w)+' '
                # g_ += re.sub('[\W|ʻ|ʼ|,|-]+','',w)+' '
                g_ += w + ' '
                    #glosses_.append(re.sub('[\W|ʻ|ʼ]+','',w))
            glosses_.append(re.sub('[ʻ|ʼ]+','',g_).strip())
        glosses_ = [g for g in glosses_ if g != '']
        for l in range(len(text)-1):
            if text[l].endswith('.') and text[l].split('.')[-2]+'.' in langs.keys() and text[l+1].startswith('<i>'):
                if '&' not in text[l+1] and '*' not in text[l+1]:
                    reflexes.append([langs[text[l].split('.')[-2]+'.'],text[l+1]])
                    counter += 1
        if counter >= 0:
            if etym != '':# and etym[0] != '*':
                for r in reflexes:
                    meaning = ', '.join(glosses_)
                    meaning = re.sub('\*','',meaning)
                    # meaning = meaning+'|'+strSM
                    # forms.append(tuple([r[0],re.sub(r"\<[^\>]*\>|\(|\)|\_|\/|\,|\;|\:|\.|\?|\]|\-|\\",'',r[1]).lower(),etym.strip('*').strip(':').strip(';').lower(),meaning+'|'+str(supplMeanings),entry,fn]))
                    forms.append(tuple([r[0],re.sub(r"\<[^\>]*\>|\(|\)|\_|\/|\,|\;|\:|\.|\?|\]|\-|\\",'',r[1]).lower(),etym.strip('*').strip(':').strip(';').lower(),mainMeaning+'|'+str(finalMeanings),entry,fn]))
'''


f = open(outfn,'w')
for l in sorted(set(finalMeanings)):
    print('\t'.join(l),file=f)


f.close()
