#!/usr/bin/python
import os
import re
import pdb
import pickle
import random
import urllib2
from StringIO import StringIO

from aime_parser import AIME_Parser
from math_cfg import config

class Math_Online(object):

    def __init__(self, cfg=None, lib=None):
        self._cfg = None

        if cfg is None:
            cfg = config

        if cfg and isinstance(cfg, dict):
            required_keys = ['url', 'start', 'end', 'pages']
            valid = True
            for kk, vv in cfg.iteritems():
                for key in required_keys:
                    if not key in vv:
                        valid = False
                        break
            if valid:
                self._cfg = cfg

        # update self._lib 
        if lib is None:
            lib = 'mathlib.lib'
        if lib and isinstance(lib, basestring):
            self._lib = lib

        # buffer to store problems
        self._data = {}

        # set default max number of problems in a test.
        self._max = 15

        # set url base
        self._url = None

    def _write_lib(self):
        # update lib
        lib = self._lib

        # write data
        if lib and self._data:

            data0 ={}
            # check if lib already exists
            if os.path.exists(lib):
                with open(lib, 'rb') as fd:
                    data0 = pickle.load(fd)

            # update the data and write to the lib file
            data0.update(self._data)
            with open(lib, 'wb') as fd:
                pickle.dump(data0, fd)

    def create_lib(self):
        cfg = self._cfg

        if cfg and isinstance(cfg, dict):

            # loop each type of tests 
            for tt, vv in cfg.iteritems():
                self._url = vv['url'].rsplit('/',2)[0]
                if not tt in self._data:
                    self._data[tt] = [[],[],[],[],[]]

                print "Working on %s, wait..."%tt.upper()
                response = urllib2.urlopen(vv['url'])
                htmls = response.read().replace('\t','').split('\n')

                work_start = False
                start = vv['start']
                end   = vv['end']

                for ii, line in enumerate(htmls):

                    if (not start in line) and (not work_start):
                        continue
                    elif not work_start:
                        work_start = True
                        #print "%s Start: %s, %d"%(tt.upper(), start, ii)
                        #print "line: %s"%line

                    if end in line and work_start:
                        #print "%s End: %s, %d"%(tt.upper(), end, ii)
                        #print "line: %s"%line
                        break

                    if (not 'href' in line):
                        continue

                    if work_start:
                        try:
                            href = re.search('<a href="(.*?)"',line)
                            if not href:
                                continue
                            url = self._url + href.group(1)
                        except:
                            continue

                        data = self.get_pages(url=url, test=tt)
                        if data:
                            ndata = len(data)
                            ntype = int(ndata/5)
                            if tt in self._data:
                                tmp = self._data[tt]
                                for kk in range(5):
                                    tmp[kk].extend(data[kk*ntype:(kk+1)*ntype])
                                self._data[tt] = tmp
                            else:
                                self._data[tt] = [data[kk*ntype:(kk+1)*ntype] for kk in range(5)]
        self._write_lib()

    def get_pages(self, url=None, test=None):
        response = urllib2.urlopen(url)
        title = url.split('title=')[1].replace('_', ' ')
        htmls = response.read().replace('\t','').split('\n')

        # if pages have (), replace it with title
        pages = self._cfg[test]['pages'][:]
        for ii, page in enumerate(pages):
            if '()' in page:
                page = re.sub('\(\)', title, page)
                pages[ii] = page

        result = []
        for ii, line in enumerate(htmls):
            data = []
            answer = None

            for page in pages:
                if page in line:
                    href = re.search('<a href="(.*?)"',line)
                    if not href:
                        continue
                    url = self._url + href.group(1)
                    if not 'answer' in url.lower():
                        data = self.parse_page(url)
                    else:
                        answer = urllib2.urlopen(url).read()

                    # append all answer page on each problem
                    if answer and data:
                        for kk, vv in enumerate(data):
                            vv.append(anser)
                            data[kk] = vv

                    # update the result
                    if data:
                        result = data
        return result

    def parse_page(self, url=None):
        response = urllib2.urlopen(url)
        #data = response.read().replace('\t','').split("\n")
        data = StringIO(response.read().replace('\t',''))
        aime = AIME_Parser(data)
        return aime()

    def create_html(self, test=None, html=None, maxn=15):
        # check if the library file exists
        if not os.path.exists(self._lib):
            print 'No math library found.'
            return

        # load the math problems
        with open(self._lib, 'rb') as fd:
            self._data = pickle.load(fd)

        # set default test type
        if test is None:
            test = 'aime'

        # check if we have problems for the given test type
        if not test in self._data:
            print "No problems found for %s"%test
            return

        if html is None:
            html = 'test1.html'

        # validate html
        if not (html and isinstance(html, basestring) and 'html' in html.lower()):
            print 'Invalid html'
            return

        # attach the test type in the htnl filename
        tmp = list(os.path.splitext(html))
        if not test in tmp[0]:
            tmp[0] += "_%s"%test
        html = ''.join(tmp)

        # automatically change the filename if the given exists
        while os.path.exists(html):
            num = re.search('(\D*(\d*)\D*)?',html).group(2)
            if not num:
                tmp = list(os.path.splitext(html))
                tmp[0] += '0'
                html = ''.join(tmp)
            else:
                num1 = str(int(num) + 1)
                html = re.sub(num, num1, html, 1)


        if isinstance(maxn, int) and maxn>0:
            self._max = maxn
        else:
            maxn = self._max


        n_per_difficulty = int(maxn/5)
        for kk in range(5):
            data = self._data[test][kk]
            self._write_html(data,n_per_difficulty,html, kk*n_per_difficulty)


    def _write_html(self, data=None, maxn=None, html=None, nstart=None):
        # select problems randomly if the number of problems is greater than 15
        ndata = len(data)
        if ndata <= maxn:
            nproblems = range(ndata)
        else:
            nproblems = [random.randint(0,ndata-1) for p in range(0,maxn)]

        # generate the html file
        with open(html, 'a+') as fp:
            for kk, vv in enumerate(nproblems):
                line = data[vv]
                line0 = "<h2><span class=\"mw-headline\" id=\"%s\">%d: %s</span></h2>"%(line[0], 
                    nstart+kk+1, line[0])
                fp.write(line0)
                fp.write(line[1])
                fp.write(line[2])
                fp.write("<p> </p>")
 

if __name__ == "__main__":
    csv = 'math_lib.csv'
    types = config.keys()
    print "Available tests: %s"%types
    test = raw_input('Please chhoose one[aime]: ') or 'aime'
    num = raw_input('Please choose the number of problems in your test[15]: ') or '15'
    num = int(num)
    aa = Math_Online(lib=csv)
    if not os.path.exists(csv):
        aa.create_lib()
    aa.create_html(test=test, maxn=num)