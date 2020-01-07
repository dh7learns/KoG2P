# -*- coding: utf-8 -*-
'''
g2p.py
~~~~~~~~~~

This script converts Korean graphemes to romanized phones and then to pronunciation.

    (1) graph2phone: convert Korean graphemes to romanized phones
    (2) phone2prono: convert romanized phones to pronunciation
    (3) graph2phone: convert Korean graphemes to pronunciation

Usage:  $ python g2p.py '스물 여덟째 사람'
        (NB. Please check 'rulebook_path' before usage.)

Yejin Cho (ycho@utexas.edu)
Jaegu Kang (jaekoo.jk@gmail.com)
Hyungwon Yang (hyung8758@gmail.com)
Yeonjung Hong (yvonne.yj.hong@gmail.com)

Created: 2016-08-11
Last updated: 2019-01-31 Yejin Cho

* Key updates made:
    - Executable in both Python 2 and 3.
    - G2P Performance test available ($ python g2p.py test)
    - G2P verbosity control available

'''

import datetime as dt
import re
import math
import sys
import optparse
import importlib

# Option
parser = optparse.OptionParser()
parser.add_option("-v", action="store_true", dest="verbose", default="False",
                  help="This option prints the detail information of g2p process.")

(options,args) = parser.parse_args()
verbose = options.verbose

def readfileUTF8(fname):
    f = open(fname, 'r')
    corpus = []

    while True:
        line = f.readline()
        line = line.encode("utf-8")
        line = re.sub(u'\n', u'', line)
        if line != u'':
            corpus.append(line)
        if not line:
            break

    f.close()
    return corpus


def writefile(body, fname):
    with open(fname, 'w', encoding="utf-8") as out:
        out.writelines(body)



def readRules(rule_book):
    f = open(rule_book, 'r',encoding="utf-8")
         
    rule_in = []
    rule_out = []

    while True:
        line = f.readline()
        line = re.sub('\n', '', line)

        if line != u'':
            if line[0] != u'#':
                IOlist = line.split('\t')
                rule_in.append(IOlist[0])
                if IOlist[1]:
                    rule_out.append(IOlist[1])
                else:   # If output is empty (i.e. deletion rule)
                    rule_out.append(u'')
        if not line: break
    f.close()

    return rule_in, rule_out


def isHangul(charint):
    hangul_init = 44032 # 가
    hangul_fin = 55203 # 힣
    return charint >= hangul_init and charint <= hangul_fin


def checkCharType(var_list):
    #  1: whitespace
    #  0: hangul
    # -1: non-hangul
    checked = []
    for i in range(len(var_list)):
        if var_list[i] == 32:   # whitespace
            checked.append(1)
        elif isHangul(var_list[i]): # Hangul character
            checked.append(0)
        else:   # Non-hangul character
            checked.append(-1)
    return checked


def graph2phone(graphs):
    # Encode graphemes as utf-8
    try:
        graphs = graphs.decode('utf-8')
    except AttributeError:
        pass

    integers = [] # integers = list of ord(char) ## by each char
    for i in range(len(graphs)):
        integers.append(ord(graphs[i]))

    # Romanization (according to Korean Spontaneous Speech corpus; 성인자유발화코퍼스)
    phones = ''
    # 초
    ONS = ['k0', 'kk', 'nn', 't0', 'tt', 'rr', 'mm', 'p0', 'pp',
           's0', 'ss', 'oh', 'c0', 'cc', 'ch', 'kh', 'th', 'ph', 'h0']
    # 중
    NUC = ['aa', 'qq', 'ya', 'yq', 'vv', 'ee', 'yv', 'ye', 'oo', 'wa',
           'wq', 'wo', 'yo', 'uu', 'wv', 'we', 'wi', 'yu', 'xx', 'xi', 'ii']
    # 종
    COD = ['', 'kf', 'kk', 'ks', 'nf', 'nc', 'nh', 'tf',
           'll', 'lk', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh',
           'mf', 'pf', 'ps', 's0', 'ss', 'oh', 'c0', 'ch',
           'kh', 'th', 'ph', 'h0']

    # Pronunciation
    idx = checkCharType(integers)
    # integers = list of ord(char) ## by each char
    # checked list of 1s,0s,-1s

    #  1: whitespace
    #  0: hangul
    # -1: non-hangul

    # ex: kor space kor space kor= [0,1,0,1,0]
        # idx = checked( list of ord(char) )

    iElement = 0
    while iElement < len(integers): # while iElement < len(list of ord(char))
        if idx[iElement] == 0:
            # ex: idx = [0,1,0,1,0]
            #       if idx[iElement] <-> if first char is kor_char
            base = 44032 # base = 44032 = ord('가')
            df = int(integers[iElement]) - base
            # df = int(first kor_char) - base // df <- diff? relative diff/loc
            # 가 - 가 = 0

            iONS = int(math.floor(df / 588)) + 1
            # largest whole int(location/588) + 1 <- floor + 1,
            # 5/4 --> 1.25 -> 1 --> (+1) --> 2
            # 가 -> ONS ----> ㄱ -> int(floor(0/588) + 1 = 1 <- ㄱ [ㄱ-ㅎ]
            iNUC = int(math.floor((df % 588) / 28)) + 1
            # 588 = 21*28 , 588*19 = 11172
            # when df > 588
            # largest whole int(remainder of (location/588) / 28) + 1
            #
            # 각 -> ㅏ -> int(floor(1 % 588) /28종) + 1 ->
            #               int(floor(1/28)) + 1 ->
            #                   0 + 1 = 1 <- ㅏ in [ㅏ-ㅣ]
            iCOD = int((df % 588) % 28) + 1
            #


            s1 = '-' + ONS[iONS - 1]  # onset
            s2 = NUC[iNUC - 1]  # nucleus

            if COD[iCOD - 1]:  # coda
                s3 = COD[iCOD - 1]
            else:
                s3 = ''
            tmp = s1 + s2 + s3
            phones = phones + tmp

        elif idx[iElement] == 1:  # space character
            tmp = '#'
            phones = phones + tmp

        phones = re.sub('-(oh)', '-', phones)
        iElement += 1
        tmp = ''

    # 초성 이응 삭제
    phones = re.sub('^oh', '', phones)
    phones = re.sub('-(oh)', '', phones)

    # 받침 이응 'ng'으로 처리 (Velar nasal in coda position)
    phones = re.sub('oh-', 'ng-', phones)
    phones = re.sub('oh([# ]|$)', 'ng', phones)

    # Remove all characters except Hangul and syllable delimiter (hyphen; '-')
    phones = re.sub('(\W+)\-', '\\1', phones)
    phones = re.sub('\W+$', '', phones)
    phones = re.sub('^\-', '', phones)
    return phones


def phone2prono(phones, rule_in, rule_out):
    # Apply g2p rules
    for pattern, replacement in zip(rule_in, rule_out):
        # print pattern
        phones = re.sub(pattern, replacement, phones)
        prono = phones
    return prono


def addPhoneBoundary(phones):
    # Add a comma (,) after every second alphabets to mark phone boundaries
    ipos = 0
    newphones = ''
    while ipos + 2 <= len(phones):
        if phones[ipos] == u'-':
            newphones = newphones + phones[ipos]
            ipos += 1
        elif phones[ipos] == u' ':
            ipos += 1
        elif phones[ipos] == u'#':
            newphones = newphones + phones[ipos]
            ipos += 1

        newphones = newphones + phones[ipos] + phones[ipos+1] + u','
        ipos += 2

    return newphones


def addSpace(phones):
    ipos = 0
    newphones = ''
    while ipos < len(phones):
        if ipos == 0:
            newphones = newphones + phones[ipos] + phones[ipos + 1]
        else:
            newphones = newphones + ' ' + phones[ipos] + phones[ipos + 1]
        ipos += 2

    return newphones


def graph2prono(graphs, rule_in, rule_out):

    romanized = graph2phone(graphs)
    romanized_bd = addPhoneBoundary(romanized)
    prono = phone2prono(romanized_bd, rule_in, rule_out)

    prono = re.sub(u',', u' ', prono)
    prono = re.sub(u' $', u'', prono)
    prono = re.sub(u'#', u'-', prono)
    prono = re.sub(u'-+', u'-', prono)

    prono_prev = prono
    identical = False
    loop_cnt = 1

    if verbose == True:
        print ('=> Romanized: ' + romanized)
        print ('=> Romanized with boundaries: ' + romanized_bd)
        print ('=> Initial output: ' + prono)

    while not identical:
        prono_new = phone2prono(re.sub(u' ', u',', prono_prev + u','), rule_in, rule_out)
        prono_new = re.sub(u',', u' ', prono_new)
        prono_new = re.sub(u' $', u'', prono_new)

        if re.sub(u'-', u'', prono_prev) == re.sub(u'-', u'', prono_new):
            identical = True
            prono_new = re.sub(u'-', u'', prono_new)
            if verbose == True:
                print('\n=> Exhaustive rule application completed!')
                print('=> Total loop count: ' + str(loop_cnt))
                print('=> Output: ' + prono_new)
        else:
            if verbose == True:
                print('\n=> Rule applied for more than once')
                print('cmp1: ' + re.sub(u'-', u'', prono_prev))
                print('cmp2: ' + re.sub(u'-', u'', prono_new))
            loop_cnt += 1
            prono_prev = prono_new

    return prono_new


def testG2P(rulebook, testset):
    [testin, testout] = readRules(testset)
    cnt = 0
    body = []
    for idx in range(0, len(testin)):
        print('Test item #: ' + str(idx+1) + '/' + str(len(testin)))
        item_in = testin[idx]
        item_out = testout[idx]
        ans = graph2phone(item_out)
        ans = re.sub(u'-', u'', ans)
        ans = addSpace(ans)

        [rule_in, rule_out] = readRules(rulebook)
        pred = graph2prono(item_in, rule_in, rule_out)

        if pred != ans:
            print('G2P ERROR:  [result] ' + pred + '\t\t\t[ans] ' + item_in + ' [' + item_out + '] ' + ans)
            cnt += 1
        else:
            body.append('[result] ' + pred + '\t\t\t[ans] ' + item_in + ' [' + item_out + '] ' + ans + '\n')

    print('Total error item #: ' + str(cnt))
    writefile(body,'good.txt')


e2k_dict = {'p0':'ㅂ','ph':'ㅍ','pp':'ㅃ','t0':'ㄷ','th':'ㅌ',
            'tt':'ㄸ','k0':'ㄱ','kh':'ㅋ','kk':'ㄲ','s0':'ㅅ',
            'ss':'ㅆ','h0':'ㅎ','c0':'ㅈ','ch':'ㅊ','cc':'ㅉ',
            'mm':'ㅁ','nn':'ㄴ','rr':'ㄹ','pf':'ㅂ','tf':'ㄷ',
            'kf':'ㄱ','mf':'ㅁ','nf':'ㄴ','ng':'ㅇ','ll':'ㄹ',
            'ks':'ㄳ','nc':'ㄵ','nh':'ㄶ','lk':'ㄺ','lm':'ㄻ',
            'lb':'ㄼ','ls':'ㄽ','lt':'ㄾ','lp':'ㄿ','lh':'ㅀ',
            'ps':'ㅄ','ii':'ㅣ','ee':'ㅔ','qq':'ㅐ','aa':'ㅏ',
            'xx':'ㅡ','vv':'ㅓ','uu':'ㅜ','oo':'ㅗ','ye':'ㅖ',
            'yq':'ㅒ','ya':'ㅑ','yv':'ㅕ','yu':'ㅠ','yo':'ㅛ',
            'wi':'ㅟ','wo':'ㅚ','wq':'ㅙ','we':'ㅞ','wa':'ㅘ',
            'wv':'ㅝ','xi':'ㅢ'}


from jamo import j2h as wrap

def prono2kor(prono):
    prono_list = prono.split(' ')
    p4wrap = []
    for p in prono_list:
        p4wrap.append(e2k_dict[p])
    p4wrap = ''.join(p4wrap)
    # wrapped = wrap(p4wrap)
    print(p4wrap)

def runKoG2P(graph, rulebook):
    [rule_in, rule_out] = readRules(rulebook)
    prono = graph2prono(str(graph), rule_in, rule_out)
    print(f'the type of prono is: {type(prono)}')
    print(prono)
    prono2kor(prono)




def runTest(rulebook, testset):
    print('[ G2P Performance Test ]')
    beg = dt.datetime.now()
    
    testG2P(rulebook, testset)
    
    end = dt.datetime.now()
    print('Total time: ')
    print(end - beg)



# Usage:
if __name__ == '__main__':
    while True:
        my_word = input('enter korean word or test in english:')

        if my_word == 'test':   # G2P Performance Test
            runTest('rulebook.txt', 'testset.txt')

        elif my_word == 'end':
            break
        else:
            graph = my_word
            runKoG2P(graph, 'rulebook.txt')


