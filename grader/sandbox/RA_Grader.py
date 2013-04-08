#!/usr/bin/env python

import os
import subprocess

###
# Python helper script used to evaluate SQL exercises
###

# ansequal - check correctness of query result
#   qr - query result
#   ans - correct query result (read from answer file)
#   order - whether order matters
#           (if false, we can sort before checking)
#   return correct - whether query gives correct answer
def ansequal(qr, ans, order):
    try:
        correct = True
        if len(qr) == len(ans):
            #print 'number of tuples is correct'
            #check each tuple
            for j in range(len(qr)):
                #order
                if not order:
                    qr.sort()
                    ans.sort()
                if qr[j] != ans[j]:
                    correct = False
        else:
            #print 'number of tuples is wrong'
            correct = False
        return correct
    except:
        return False

# get answer from answer file
#   ansfile - answer file
#   qnum - question number
# return:
#   ans - query answer
#   order - whether order matters
def getanswer(ansfile, qnum, dbname):
    #index i is one less than qnum since we start at 0
    i = qnum - 1

    #open ansfile
    ansf = open(ansfile)

    anstext = ' '.join(ansf.readlines())
    ansf.close()

    #read ansarray from trusted file
    #TODO: would prefer to use ast.literal_eval if python2.6
    ansarray = eval(anstext)

    #first entry in answer is expected query result
    ans = ansarray[i][0]

    #second entry in answer is whether order matters
    order = ansarray[i][1]

    return (ans, order)


def runra(sub, dbname):
    abort = False
    args = []
    raerror = False

    retval = 129

    try:
        if len(sub) > 1000:
            qr = '<font style="color:red">Please limit submission to 1000 characters</font>'
            raerror = True
            return (qr, raerror)
    except:
        qr = '<font style="color:red">Truncate trap %s</font>'
        raerror = True
        return (qr, raerror)

    try:
        sub = sub.strip()
        opensuccess = False # indicates success of creating temp file
        import tempfile, os

        fd, path = tempfile.mkstemp('.ra')
        os.close(fd)

        f = open(path, 'w')
        f.write(sub)
        if ';' not in sub:
            f.write(';')
        f.write('\n')
        f.close()

        import shutil
        fd3, path3 = tempfile.mkstemp('.db')
        os.close(fd3)

        shutil.copy(dbname, path3)
        shutil.copymode(dbname, path3)

        fd2, path2 = tempfile.mkstemp('.properties')
        os.close(fd)

        f = open(path2, 'w')
        f.write('url:jdbc:sqlite:' + path3)
        f.write('\n')
        f.close()

        opensuccess = True

        #path = '/home/sandbox/ra/temp.ra'

        #cmd = 'java -classpath /home/sandbox/saxon9he.jar net.sf.saxon.Transform %s %s' % (dbname, path)
        #cmd = 'java -ea -jar /home/sandbox/ra/ra.jar'
        #args = ['java', '-ea', '-jar', '/home/sandbox/ra/ra.jar', '/home/sandbox/ra/sample.properties', '-i', path]
        args = ['java', '-ea', '-jar', '/home/sandbox/ra/ra.jar', path2, '-i', path]
        #args = shlex.split(cmd)

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        qr = p.stdout.readlines()
        i = -1 
        j = -1
        schema = ''
        
        for num in range(len(qr)):
            line = qr[num]
            if line.find('Output schema') > -1:
                i = num
            if line.find('Total number of rows') > -1:
                j = num
        if i > -1 and j > -1:
            schema = qr[i]
            rawdata = qr[i+2:j-1]
            data = []
            for line in rawdata:
                data.append(line.split('|'))
            return (data, False)
        else:        
            qr = '\n'.join(qr)
            qr = qr.replace('\n\nRA: an interactive relational algebra interpreter\n\nVersion 2.1b by Jun Yang (junyang@cs.duke.edu)\n\nType "\\help;" for help\n\n\n\n', '')
            qr = qr.replace('Bye!\n', '')
            qr = '<font style="color:red">%s</font><br>' % qr
            raerror = True
        retval = p.wait()
    except:
        if opensuccess:
            #print error
            from sys import exc_info
            e = exc_info()
            qr = str(args) + '<font style="color:red">Query failed to execute: %s</font><br>' % (str(e[0]) + str(e[1]))
            #qr = str(args) + '<font style="color:red">Query failed to execute</font>'
            abort = True
        else:
            qr = '<font style="color:red">Could not open temp file</font>'
            abort = True
    finally:
        try:
            #TODO: drop all temp files
            os.unlink(path)
            os.unlink(path2)
            os.unlink(path3)
        except:
            qr = '<font style="color:red">Finally trap %s</font>' % path
            abort = True

    #return (qr, abort, retval)
    #TODO: figure this out
    return (qr, raerror)

# check whether user query returns correct answer
#   userquery - user query
#   dbname - filename of db
#   ansfile - answer file
#   qnum - question number
# return:
#   correct - whether answer is correct
#   qr - result returned by user query
#   ans - correct query result
#   order - whether order matters
def checkgood(userquery, dbname, ansfile, qnum):
    qr = ''
    correct = False
    raerror = False

    from os.path import exists

    try:
        if exists(ansfile):
            (ans, order) = getanswer(ansfile, qnum, dbname)
        else:
            qr = 'System Error: Ansfile does not exist'
            ans = ''
            order = ''
            correct = False
            return (correct, qr, ans, order, raerror)

        if not exists(dbname):
            qr = 'System Error: DB does not exist'
            correct = False
            return (correct, qr, ans, order, raerror)
    except:
        qr = 'System Error: could not get answer'
        ans = ''
        order = ''
        correct = False
        return (correct, qr, ans, order, raerror)


    correct = False

    (qr, raerror) = runra(userquery, dbname)

    #see whether query result matches answer
    correct = ansequal(qr, ans, order)

    return (correct, qr, ans, order, raerror)

def toTable(data):
    if isinstance(data, str):
        return str(data)
    elif isinstance(data, list) and len(data) == 0:
        return '<i>Empty result</i><br>'
    try:
        retval = ''
        retval += '<table border="1" style="font-size:90%; padding: 1px;border-spacing: 0px; border-collapse: separate">'
        for row in data:
            retval += '<tr>'
            for col in row:
                retval += '<td>'
                retval += str(col)
                retval += '</td>'
            retval += '</tr>'
        retval += '</table>'
        return retval
    except:
        return str(data)

#output has two parts:
#(1) scorestr: The string 'Score: ' followed by 0 or 1
#(2) feedbackstr: A second string containing feedback
if __name__ == '__main__':

    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Send an attachment via gmail')
    parser.add_argument('-d','--dbname', dest='dbname', help='Database Name')
    parser.add_argument('-a','--answerfile', dest='answer_file', help='Answer File')
    parser.add_argument('-q','--qnum', dest='qnum', help='Question Number')
    parser.add_argument('-u','--userquery', dest='user_query', help='User Query')

    args = parser.parse_args()

    userquery = ''
    dbname = ''
    qnum = 1
    scorestr = ''
    feedbackstr = ''

    try:
        dbname =  args.dbname
        ansfile = args.answer_file
        qnum = int(args.qnum)
        userquery = args.user_query
    except:
        print 'Score: 0  Error: Could not read query'
        sys.exit(0)


    try:
        (correct, qr, ans, order, raerror) = checkgood(userquery, dbname, ansfile, qnum)
    except:
        from sys import exc_info
        e = exc_info()
        scorestr = 'Score: 0'
        feedbackstr = '<font style="color:red">Error: Could not execute query: %s</font><br/>' % (str(e[0]) + str(e[1]))
        print scorestr + ' ' + feedbackstr
        sys.exit(0)

    #prepare score string and feedback string

    try:
        userquery = userquery.strip()
        if userquery == '':
            qr = 'No query submitted'
            ans = 'Please submit a query to see the expected result'
        if correct:
            scorestr = 'Score: 1'
        else:
            scorestr = 'Score: 0'
        feedbackstr = ''
        if correct:
            feedbackstr += '<br><font style="color:green; font-weight:bold;">Correct</font><br>'
        else:
            feedbackstr += '<br><font style="color:red; font-weight:bold;">Incorrect</font><br>'
        if not raerror or userquery == '':
            feedbackstr += '<br>Your Query Result: ' + toTable(qr) + ' '
        else:
            feedbackstr += '<br>Error from SQLite: ' + toTable(qr) + ' '

        if userquery != '' and not isinstance(qr, str):
            feedbackstr += '<br>Expected Query Result: ' + toTable(ans) + ' '
            if order:
                feedbackstr += '<i>(Order matters)</i> '

        print scorestr + ' ' + feedbackstr

    except:
        scorestr = 'Score: 0'
        feedbackstr += 'Error: Could not evaluate query'
        print scorestr + ' ' + feedbackstr
