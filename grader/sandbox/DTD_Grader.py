#!/usr/bin/python
import subprocess
import re
#import shlex

def rundtd(sub, dbname):
    abort = False

    retval = 129

    try:
        if len(sub) > 1000:
            qr = '<font style="color:red">Please limit submission to 1000 characters</font>'
            abort = True
            return (qr, abort, retval)
    except:
        qr = '<font style="color:red">Truncate trap %s</font>'
        abort = True
        return (qr, abort, retval)

    try:
        sub = sub.strip()
        opensuccess = False # indicates success of creating temp file
        import tempfile, os

        fd, path = tempfile.mkstemp('.dtd')
        os.close(fd)

        f = open(path, 'w')
        f.write(sub)
        f.close()

        opensuccess = True

        args = ['xmllint', '--dtdvalid', path, '--noout', '/home/sandbox/' + dbname] 

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        qr = p.stdout.readlines()
        qr = '\n'.join(qr)
        retval = p.wait()
    except:
        if opensuccess:
            qr = str(args) + '<font style="color:red">DTD failed to execute</font>'
            abort = True
        else:
            qr = '<font style="color:red">Could not open temp file</font>'
            abort = True
    finally:
        try:
            os.unlink(path)
        except:
            qr = '<font style="color:red">Finally trap %s</font>' % path
            abort = True

    return (qr, abort, retval)

def checkgood(userquery, dbname, ansfile, qnum):
    runerror = 5
    try:
        qr = ''
        correct = False
        
        ###
        ac = ''
        order = ''
        qc = ''
        xtype = 'none'

        from os.path import exists

        ans = ''

        correct = False

        try:
            (qr, abort, runerror) = rundtd(userquery, dbname)
        except:
            qr = 'Error: bad run'
            abort = True

        qc = qr
        qc = re.sub(r'\s', '', qc)

        ac = ans
        ac = re.sub(r'\s', '', ac)

        if qc == ac:
            correct = True
        else:
            correct = False

        return (correct, qr, ans, order, runerror)
    except:
        return (False, qr, 'error in answer verification', False, runerror)

def toDisplay(data, runerror):
    if data.strip() == '':
        return '<i>None</i><br>'

    datastr = str(data)

    if runerror != 0:
        datastr = datastr.replace('\n', '<br/>')
        return '<font style="color:red">' + datastr + '</font>'
    else:
        return datastr

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

    #run query and check answer

    try:
        (correct, qr, ans, order) = checkgood(userquery, dbname, ansfile, qnum)
    except:
        print 'Score: 0 Error: Could not execute query.' + dbname + ansfile
        sys.exit(0)


    #prepare score string and feedback string

    try:
        userquery = userquery.strip()
        if userquery == '':
            qr = 'No DTD submitted'
            ans = 'Please submit a DTD to see the expected result'
        if correct:
            scorestr = 'Score: 1'
        else:
            scorestr = 'Score: 0'
        feedbackstr = ''
        if correct:
            feedbackstr += '<br><font style="color:green; font-weight:bold;">Correct</font><br>'
        else:
            feedbackstr += '<br><font style="color:red; font-weight:bold;">Incorrect</font><br>'
        feedbackstr += '<br>Error messages from xmllint: ' + toDisplay(qr, runerror) + ' '

        print scorestr + ' ' + feedbackstr

    except:
        scorestr = 'Score: 0'
        feedbackstr += 'Error: Could not evaluate DTD'
        print scorestr + ' ' + feedbackstr
