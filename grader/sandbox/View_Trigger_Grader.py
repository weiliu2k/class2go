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
    checkquery = ansarray[i][2]
    checkmod = ansarray[i][3]
    moddesc = ansarray[i][4]
    viewquery = ansarray[i][5]

    return (ans, order, checkquery, checkmod, moddesc, viewquery)

'''
# get answer from answer file
#   ansfile - answer file
#   qnum - question number
# return:
#   ans - query answer
#   order - whether order matters
def getanswermod(ansfile, qnum, dbname):
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
    ansquery = ansarray[i][0]

    #second entry in answer is whether order matters
    order = ansarray[i][1]

    checkquery = ansarray[i][2]

    try:
        ans = runmod(ansquery, dbname, checkquery)
    except:
        ans = 'error running answer query'

    return (ans, order, checkquery)

def runquery(usertrig, dbname):
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

        c.execute(usertrig)
        #fetch tuples in query result
        qr = c.fetchall()
        return qr
    except:
        if opensuccess:
            #print error
            from sys import exc_info
            e = exc_info()
            qr = '<font style="color:red">Query failed to execute: %s</font><br>' % (str(e[0]) + str(e[1]))
        else:
            qr = '<font style="color:red">Error: Could not open DB</font>' 

        return qr

    finally:
        try:
            os.unlink(path)
        except:
            pass
'''

def runtrigger(usertrig, dbname, checkquery, checkmod, viewquery):
    #execute query
    currcmd = 'error'
    trigsuccess = False
    modsuccess = False
    vr = 'error'
    try:
        opensuccess = False #indicates success of creating temp file
        import tempfile, os
        import shutil

        fd, path = tempfile.mkstemp('.db')
        os.close(fd)

        shutil.copy(dbname, path)
        
        import sqlite3
        #conn = sqlite3.connect(path, autocommit=0)
        conn = sqlite3.connect(path, isolation_level = "DEFERRED")
        c = conn.cursor()

        opensuccess = True

        c.execute("pragma recursive_triggers = off")

        #trigs = usertrig.split('|')
        #for trig in trigs:
        #    currcmd = trig
        #    c.execute(trig)

        currcmd = usertrig
        c.execute(usertrig)

        #fetch tuples in query result
        qr_dummy = c.fetchall()

        trigsuccess = True 

        conn.isolation_level = "DEFERRED"

        mods = checkmod.split(';')
        c.execute('begin')
        for mod in mods:
            currcmd = mod
            c.execute(mod)
        #c.execute('commit')
        conn.commit()
        #conn.rollback()
        #fetch tuples in query result
        #qr_dummy2 = c.fetchall()

        modsuccess = True

        currcmd = checkquery
        c.execute(checkquery)
        #fetch tuples in query result
        qr = c.fetchall()

        currcmd = viewquery
        c.execute(viewquery)
        #fetch tuples in query result
        vr = c.fetchall()

        return (qr, trigsuccess, modsuccess, vr)
    except:
        if opensuccess:
            #print error
            from sys import exc_info
            e = exc_info()
            qr = '<font style="color:red">Failed command: %s<br/>Error from SQLite: %s</font><br>' % (currcmd, str(e[0]) + str(e[1]))
        else:
            qr = '<font style="color:red">Error: Could not open DB</font>' 

        return (qr, trigsuccess, modsuccess, vr)

    finally:
        try:
            os.unlink(path)
        except:
            pass

# check whether user query returns correct answer
#   usertrig - user trigger
#   dbname - filename of db
#   ansfile - answer file
#   qnum - question number
# return:
#   correct - whether answer is correct
#   qr - result returned by user query
#   ans - correct query result
#   order - whether order matters
def checkgood(usertrig, dbname, ansfile, qnum):
    qr = ''
    correct = False
    checkquery = 'error'
    checkmod = 'error'
    moddesc = 'error'
    trigsuccess = False
    modsuccess = False

    viewquery = 'error'
    vr = ''

    from os.path import exists

    try:
        if exists(ansfile):
            (ans, order, checkquery, checkmod, moddesc, viewquery) = getanswer(ansfile, qnum, dbname)
        else:
            qr = 'System Error: Ansfile does not exist'
            ans = ''
            order = ''
            correct = False
            return (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr)

        if not exists(dbname):
            qr = 'System Error: DB does not exist'
            correct = False
            return (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr)
    except:
        qr = 'System Error: could not get answer'
        ans = ''
        order = ''
        correct = False
        return (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr)

    if len(usertrig) > 1000:
        qr = 'System Error: Please limit submissions to 1000 characters'
        ans = ''
        order = ''
        correct = False
        return (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr)

    correct = False

    (qr, trigsuccess, modsuccess, vr) = runtrigger(usertrig, dbname, checkquery, checkmod, viewquery)

    #see whether query result matches answer
    correct = ansequal(qr, ans, order)

    return (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr)

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
        (correct, qr, ans, order, checkquery, checkmod, trigsuccess, modsuccess, moddesc, viewquery, vr) = checkgood(usertrig, dbname, ansfile, qnum)
    except:
        from sys import exc_info
        e = exc_info()
        scorestr = 'Score: 0'
        feedbackstr = '<font style="color:red">Error: Could not execute command: %s</font><br/>' % (str(e[0]) + str(e[1]))
        print scorestr + ' ' + feedbackstr
        sys.exit(0)

    #prepare score string and feedback string

    try:
        usertrig = usertrig.strip()
            '''
            if usertrig == '':
                qr = 'No trigger submitted'
                ans = 'Please submit a trigger to see the expected result'
            '''
        if correct:
            scorestr = 'Score: 1'
        else:
            scorestr = 'Score: 0'
        feedbackstr = ''
        if correct:
            feedbackstr += '<br><font style="color:green; font-weight:bold;">Correct</font><br>'
        else:
            feedbackstr += '<br><font style="color:red; font-weight:bold;">Incorrect</font><br>'
        if usertrig != '':
            if trigsuccess:

                feedbackstr += '<br/>Trigger command was executed.<br/>'

                if modsuccess:
                #if usertrig != '' and not isinstance(qr, str):
                    feedbackstr += '<br/>To check your trigger, we first ran the following data modification statement(s): <i>%s</i>. ' % checkmod
                    if moddesc != '':
                        feedbackstr += '<br/>English description of modifications: ' + moddesc + ' '

                    feedbackstr += '<br/><br/>We then queried the view: <i>%s</i>' % viewquery
                    feedbackstr += '<br/>View Result: ' + toTable(vr) + ' '

                    feedbackstr += '<br/>We then ran the following query: <i>%s</i><br/>' % (checkquery)
                    feedbackstr += 'Your Query Result: ' + toTable(qr) + ' '

                    if usertrig != '' and not isinstance(qr, str):
                        feedbackstr += '<br>Expected Query Result: ' + toTable(ans) + ' '
                else:
                    feedbackstr += '<br/>To check your trigger, we tried to run the following data modification statement(s): <i>%s</i>. <br/>' % (checkmod)
                    if moddesc != '':
                        feedbackstr += '<br/>English description of modifications: ' + moddesc + ' '
                    feedbackstr += '<br/>' + str(qr) + ' '
            else:
                feedbackstr += '<br/>' + str(qr) + ' '
        else:
            feedbackstr += 'No trigger submitted'

            #feedbackstr += '<br>(Debug)Your Query Result: ' + str(qr) + ' '
            #feedbackstr += '<br>(Debug)Expected Query Result: ' + str(ans) + ' '

        print scorestr + ' ' + feedbackstr

    except:
        scorestr = 'Score: 0'
        feedbackstr += 'Error: Could not evaluate command'
        print scorestr + ' ' + feedbackstr
