#!/usr/bin/env python

import os

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
        if len(qr) != len(ans):
            return False

        #check each tuple
        for j in range(len(qr)):
            #order
            if not order:
                qr.sort()
                ans.sort()
            qrx = list(qr[j])
            ansx = list(ans[j])

            if qrx != ansx:
                if len(qrx) != len(ansx):
                    return False

                #check to see if equal or if floats are very close
                for k in range(len(qrx)):
                    qy = qrx[k]
                    ay = ansx[k]
                    if qy != ay:
                        try:
                            qf = float(qy)
                            af = float(ay)
                            if (abs(qf-af) > .000001):
                                return False
                        except:
                            return False
        return True
    except:
        return False

# get answer from answer file
#   ansfile - answer file
#   qnum - question number
# return:
#   ans - query answer
#   order - whether order matters
def getanswer(ansfile, qnum):
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

    from os.path import exists

    if exists(ansfile):
        (ans, order) = getanswer(ansfile, qnum)
    else:
        qr = 'System Error: Ansfile does not exist'
        ans = ''
        order = ''
        correct = False
        return (correct, qr, ans, order)

    if not exists(dbname):
        qr = 'System Error: DB does not exist'
        correct = False
        return (correct, qr, ans, order)

    if len(userquery) > 1000:
        qr = 'System Error: Please limit submissions to 1000 characters'
        correct = False
        return (correct, qr, ans, order)

    correct = False

    #execute query
    try:
        opensuccess = False #indicates success of creating temp file
        import tempfile, os
        import shutil

        fd, path = tempfile.mkstemp('.db')
        os.close(fd)

        shutil.copy(dbname, path)
        
        import sqlite3
        conn = sqlite3.connect(path)
        c = conn.cursor()

        opensuccess = True

        c.execute(userquery)
        #fetch tuples in query result
        qr = c.fetchall()
    except:
        if opensuccess:
            #print error
            from sys import exc_info
            e = exc_info()
            qr = '<font style="color:red">Query failed to execute: %s</font><br>' % (str(e[0]) + str(e[1]))
        else:
            qr = '<font style="color:red">Error: Could not open DB</font>' 

        return (correct, qr, ans, order)

    finally:
        try:
            os.unlink(path)
        except:
            pass
    

    #see whether query result matches answer
    correct = ansequal(qr, ans, order)

    return (correct, qr, ans, order)

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
                if col is None:
                    retval += '&lt;NULL&gt;'
                else:
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
            qr = 'No query submitted'
            ans = 'Please submit a query to see the expected result'

        if correct:
            scorestr = 'Score: 1'
        else:
            scorestr = 'Score: 0'

        if correct:
            feedbackstr += '<br><font style="color:green; font-weight:bold;">Correct</font><br>'
        else:
            feedbackstr += '<br><font style="color:red; font-weight:bold;">Incorrect</font><br>'

        feedbackstr += '<br>Your Query Result: ' + toTable(qr) + ' '

        if userquery != '' and not isinstance(qr, str):
            feedbackstr += '<br>Expected Query Result: ' + toTable(ans) + ' '
            if order:
                feedbackstr += '<i>(Order matters)</i> '

        print scorestr + ' ' + feedbackstr

    except:
        scorestr = 'Score: 0'
        feedbackstr += 'Error: Could not evaluate query'
        print scorestr + ' ' + feedbackstr
