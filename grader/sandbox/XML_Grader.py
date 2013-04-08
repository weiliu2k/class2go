#!/usr/bin/python
import subprocess
import re
import shlex

# get answer from answer file
#   ansfile - answer file
#   qnum - question number
# return:
#   ans - query answer
#   order - whether order matters
#   xtype - whether to run XPath, XQuery, or XSLT
def getanswer(ansfile, qnum):
    #index i is one less than qnum since we start at 0
    i = qnum - 1
    xtype = 'bad'

    #open ansfile
    try:
        ansf = open(ansfile)

        anstext = '\n'.join(ansf.readlines())
        ansf.close()
    except:
        ans = 'Error w reading answer file'
        order = False

    #read ansarray from trusted file
    try:
        #TODO: would prefer to use ast.literal_eval if python2.6
        ansarray = eval(anstext)

        ans = ansarray[i][0]
        xtype = ansarray[i][1]
        ans = '<?xml version="1.0" encoding="UTF-8"?>' + ans

        order = False
    except:
        ans = 'Error w parsing' + anstext
        order = False

    return (ans, order, xtype)

def runxquery(sub):
    abort = False

    retval = 129

    path = 'path not set'
    qr = ''
    try:
        opensuccess = False # indicates success of creating temp file
        import tempfile, os

        fd, path = tempfile.mkstemp('.xq')
        os.close(fd)

        f = open(path, 'w')
        f.write(sub)
        f.close()

        opensuccess = True

        cmd = 'java -classpath /home/sandbox/saxon9he.jar net.sf.saxon.Query %s' % path

        args = shlex.split(cmd)

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        qr = p.stdout.readlines()
        qr = ''.join(qr)
        retval = p.wait()
    except:
        if opensuccess:
            qr = str(args) + '<font style="color:red">Query failed to execute</font>'
            abort = True
        else:
            qr = '<font style="color:red">Could not open temp file: %s</font>' % path
            abort = True
    finally:
        try:
            os.unlink(path)
        except:
            qr += '<br/><font style="color:red">Error during unlink: %s</font>' % path
            abort = True
            
    return (qr, abort, retval)

def runxslt(sub, dbname):
    abort = False

    retval = 129
    try:
        sub = sub.strip()
        opensuccess = False # indicates success of creating temp file
        import tempfile, os

        fd, path = tempfile.mkstemp('.xml')
        os.close(fd)

        f = open(path, 'w')
        f.write(sub)
        f.close()

        opensuccess = True

        cmd = 'java -classpath /home/sandbox/saxon9he.jar net.sf.saxon.Transform %s %s' % (dbname, path)
        args = shlex.split(cmd)

        p = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        qr = p.stdout.readlines()
        qr = ''.join(qr)
        retval = p.wait()
    except:
        if opensuccess:
            qr = str(args) + '<font style="color:red">Query failed to execute</font>'
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

        if exists(ansfile):
            (ans, order, xtype) = getanswer(ansfile, qnum)
        else:
            qr = 'System Error: Ansfile does not exist'
            ans = ''
            order = ''
            correct = False
            return (correct, qr, ans, order, runerror)

        if len(userquery) > 1000:
            qr = 'System Error: Please limit submission to 1000 characters'
            ans = ''
            order = ''
            correct = False
            return (correct, qr, ans, order, runerror)

        correct = False

        try:
            if xtype == 'XPath' or xtype == 'XQuery':
                (qr, abort, runerror) = runxquery(userquery)
            elif xtype == 'XSLT':
                (qr, abort, runerror) = runxslt(userquery, dbname)
            else:
                qr = 'Error: no xtype'
                abort = True
        except:
            qr = 'Error: bad run'
            abort = True

        qc = qr
        qc = re.sub(r'\s', '', qc)

        ac = ans
        ac = re.sub(r'\s', '', ac)

        rqc = removeXMLDec(qc)
        rac = removeXMLDec(ac)

        if rqc == rac:
            correct = True
        else:
            try:
                #additional check with display values
                pqr = toDisplay(qr, 0)
                pans = toDisplay(ans, 0)
                spqr = re.sub(r'\s', '', pqr)
                spans = re.sub(r'\s', '', pans)
                if spqr == spans:
                    correct = True
            except:
                correct = False

        #ans = '(Debug)rqc: ' + rqc + 'rac: ' + rac

        return (correct, qr, ans, order, runerror)
    except:
        return (False, qr, 'error in answer verification', False, runerror)

def toPrettyXml(rootdata):
    prettyXml = 'error in printing xml'
    try:
        import xml.dom.minidom
        import re
        rootdata = '<rootroot>' + rootdata + '</rootroot>'
        xml = xml.dom.minidom.parseString(rootdata)
        uglyXml = xml.toprettyxml(indent='  ')
        text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
        prettyXml = text_re.sub('>\g<1></', uglyXml)
        prettyXml = prettyXml.replace('<rootroot>\n', '')
        prettyXml = prettyXml.replace('</rootroot>\n', '')
        prettyXml = prettyXml.replace('<rootroot/>\n', '')
        prettyXml = prettyXml.replace('<?xml version="1.0" ?>\n', '')
        prettyXml = prettyXml.replace('<', '&lt;')
        prettyXml = prettyXml.replace('>', '&gt;')
        lines = prettyXml.split('\n')
        retval = ''
        for line in lines:
            if line.strip() == '':
                pass
            else:
                retval += line
                retval += '\n'
                
        return retval
    except:
        from sys import exc_info
        e = exc_info()
        return str(rootdata) + str(e[0]) + str(e[1]) + prettyXml

def removeXMLDec(data):
    try:
        data = removestr(data, '<?xml version="1.0" encoding="UTF-8"?>')
        data = removestr(data, '<?xmlversion="1.0"encoding="UTF-8"?>')
        return data
    except:
        return data

def removestr(data, badstr):
    try:
        xmlloc = data.find(badstr)
        lenxmldec = len(badstr)
        if xmlloc > -1:
            return data[xmlloc+lenxmldec:]
        else:
            return data[:]
    except:
        return data[:]

def toDisplay(data, runerror):
    rootdata = ''
    xmlloc = -5
    import re

    if runerror != 0:
        datastr = str(data)
        datastr = datastr.replace('\n', '<br/>')
        return '<font style="color:red">' + datastr + '</font>'

    rootdata = data
    rootdata = rootdata.replace('\n', '')
    xmlloc = rootdata.find('<?xml version="1.0" encoding="UTF-8"?>')
    lenxmldec = len('<?xml version="1.0" encoding="UTF-8"?>')
    if xmlloc > -1:
        rootdata = rootdata[xmlloc+lenxmldec:]
    else:
        pass
        #return str(data)
    #rootdata = re.sub(r'\s', '', rootdata)
    if rootdata.strip() == '':
        return '<i>Empty result</i><br>'
    try:
        retval = ''
        retval += '<font style="font-size:90%;">'
        retval += '<pre/>'
        prettyXml = toPrettyXml(rootdata)
        retval += prettyXml
        retval += '</pre>'
        retval += '</font>'
        return retval
    except:
        from sys import exc_info
        e = exc_info()
        return str(data) + str(e[0]) + str(e[1])

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
        (correct, qr, ans, order, runerror) = checkgood(userquery, dbname, ansfile, qnum)
    except:
        scorestr = 'Score: 0'
        feedbackstr = 'Error: Could not execute query'
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
        feedbackstr += '<br>Your Query Result: ' + toDisplay(qr, runerror) + ' '
            #feedbackstr += '<br>(Debug)Expected Query Result: ' + str(ans) + ' '
        if userquery != '' and not runerror:
            feedbackstr += '<br>Expected Query Result: ' + toDisplay(ans, runerror) + ' '
            if order:
                feedbackstr += '<i>(Order matters)</i> '

        print scorestr + ' ' + feedbackstr

    except:
        scorestr = 'Score: 0'
        feedbackstr += 'Error: Could not evaluate query'
        print scorestr + ' ' + feedbackstr
