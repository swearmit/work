"""
A module to parse downloaded AIME page from https://artofproblemsolving.com
For example https://artofproblemsolving.com/wiki/index.php?title=2017_AIME_I_Problems
"""
import os
import re
import pdb
import traceback
from StringIO import StringIO

class AIME_Parser(object):
    def __init__(self, fname=None, url=None):
        # set default parameters
        self._result = []
        self._fname = None
        self._url = "https://artofproblemsolving.com"

        # update file name for aime problems
        if fname and isinstance(fname, StringIO):
            self._fname = fname
        elif fname and isinstance(fname, basestring) and os.path.exists(fname):
            self._fname = open(fname,'r')
        else:
            print "'fname' must be a file or a stream."

        # update url if given
        if url and isinstance(url, basestring) and 'http' in url.lower():
            self._url = url

    def __call__(self):
        if self._url and self._fname:
            answer = ''
            problem = ''
            start = False

            # loop through each line
            for ii, line in enumerate(self._fname):
                # find problem start
                if re.search('id=\"Problem.*\>Problem.*', line):
                    start = True
                    #title = line
                    continue

                # go to next line if current line is empty or not start
                if not (line and start): continue

                # fetch problems
                if 'Solution' in line:
                    answer = re.sub('/wiki', "%s/wiki"%self._url, line)
                    title = re.search('title="(.*)"',line).group(1)
                    self._result.append([title, problem, answer])
                    problem, answer, title = '','', ''
                    start = False
                else:
                    if '//wiki-images.' in line:
                        line = re.sub('//wiki-images.', "https://wiki-images.", line)
                    if '/wiki/' in line:
                        line = re.sub('/wiki/', "%s/wiki/"%self._url, line)
                    problem += re.sub('src="//latex.','src="https://latex.',line)


        return self._result
if __name__ == "__main__":
    aa = AIME_Parser('test.txt')
    bb = aa()
    print bb
    with open('test0.html', 'w') as fp:
        for line in bb:
            fp.write(line[0])
            fp.write("<p>")
            fp.write(line[1])
            fp.write(line[2])
            fp.write("<p>")
            fp.write("<p>")            
