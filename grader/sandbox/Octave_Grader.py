#!/usr/bin/env python

import os
from os.path import exists, basename, dirname
import subprocess
import shutil
import tempfile

###
# Python helper script used to evaluate Octave (matlab) exercises
###



def run_octave(user_input, testfile, ansfile):

    error = False
    score = '0'
    feedback = ''
    dest = ''

    try:
        if len(user_input) > 1000:
            feedback = '<font style="color:red">Please limit submission to 1000 characters</font>'
            error = True
            return (score, feedback, error)
    except:
        feedback = '<font style="color:red">Truncate trap %s</font>'
        error = True
        return (score, feedback, error)

    try:
        opensuccess = False # indicates success of creating temp file

        # copy tester to stage and create a temp user_input
        from os.path import exists, basename

        dest = dirname(testfile)+'/../stage/'+basename(testfile)
        shutil.copy(testfile, dest)


        #fd, path_user = tempfile.mkstemp()

        submitted_file = dirname(testfile)+'/../stage/submitted.m'
        f = open(submitted_file, 'w')
        f.write(user_input)
        f.close()

        stage_dir = dirname(testfile)+'/../stage'

        args = '/usr/local/bin/octave --silent --no-window-system --path ' + dirname(testfile) + ' ' + dest + ' ' + submitted_file + ' ' + ansfile

        # print 'Running: ' + args

        import shlex

        p = subprocess.Popen(shlex.split(args), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        qr = p.stdout.readlines()
        start = -1
        end = -1
        feedback = ''

        for num in range(len(qr)):
            line = qr[num]
            if line.find('Start of Feedback') > -1:
                start = num

            if line.find('End of Feedback') > -1:
                end = num

            if (start != -1 and end == -1 and start != num):
                feedback += line

            if line.find('<score>') > -1:
                end_score = line.find('</score>')
                score = line[7:end_score]

        if score == '0':
            error = True

        retval = p.wait()

    except:
        #if opensuccess:
        #print error
        from sys import exc_info
        e = exc_info()
        feedback = str(args) + '<font style="color:red">Code failed to execute: %s</font><br>' % (str(e[0]) + str(e[1]))
        abort = True
        #else:
        #feedback = '<font style="color:red">Could not open temp file</font>'
        abort = True
    finally:
        #try:
        os.unlink(dest)
        os.unlink(submitted_file)
        #except:
        #    feedback = '<font style="color:red">Finally trap </font>'
        abort = True

    return (score, feedback, error)

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
def grade(user_input, testfile, ansfile, qnum):
    score = ''
    feedback = ''
    error = False

    if not exists(ansfile):
        feedback = 'System Error: Answer file does not exist'
        return (score, feedback, error)

    if not exists(testfile):
        feedback = 'System Error: Test file does not exist'
        return (score, feedback, error)

    (score,feedback, error) = run_octave(user_input, testfile, ansfile)

    return (score,feedback, error)



#output has two parts:
#(1) scorestr: The string 'Score: ' followed by 0 or 1
#(2) feedbackstr: A second string containing feedback
if __name__ == '__main__':

    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Send an attachment via gmail')
    parser.add_argument('-d','--testfile', dest='test_file', help='Test File')
    parser.add_argument('-a','--answerfile', dest='answer_file', help='Answer File')
    parser.add_argument('-q','--qnum', dest='qnum', help='Question Number')
    parser.add_argument('-u','--userquery', dest='user_query', help='User Query')

    args = parser.parse_args()


    userquery = ''
    testfile = ''
    qnum = ''
    scorestr = ''
    feedbackstr = ''
    ansfile = ''

    try:
        testfile =  args.test_file
        ansfile = args.answer_file
        qnum = args.qnum
        userquery = args.user_query
    except:
        print '<score>0</score>Error: Could not read query'
        sys.exit(0)

    try:
        (score,feedback, error) = grade(userquery, testfile, ansfile, qnum)
    except:
        from sys import exc_info
        e = exc_info()
        scorestr = '<score>0</score>'
        feedbackstr = '<font style="color:red">Error: Could not execute query: %s</font><br/>' % (str(e[0]) + str(e[1]))
        print scorestr + feedbackstr
        sys.exit(0)

    #prepare score string and feedback string

    try:
        userquery = userquery.strip()
        if userquery == '':
            qr = 'No code submitted'
            ans = 'Please submit an answer to the question'
        scorestr = '<score>%s</score>' % (score)

        feedbackstr = ''

        if not error:
            feedbackstr += '<font style="color:green; font-weight:bold;">Correct</font>'
        else:
            feedbackstr += '<font style="color:red; font-weight:bold;">Incorrect</font>'

        feedbackstr += '<br/><br/>Feedback: ' + feedback + ' '

        print scorestr + feedbackstr

    except:
        scorestr = '<score>0</score>'
        feedbackstr += 'Error: Could not run code'
        print scorestr + feedbackstr
