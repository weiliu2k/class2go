# Create your views here.
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
import subprocess, StringIO
from django.utils import simplejson
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

def test_query(request):
    return render(request, 'test_query.html', {})


def escapeshellarg(arg):
    return "\\'".join("'" + p + "'" for p in arg.split("'"))

@csrf_exempt
def grade_query(request):

    grader_name   = request.POST['grader_name']
    selectDict   = request.POST['select_dict']
    quiz_dir = settings.SANDBOX_DIR

    # name of dbfile to test query on
    if grader_name == 'Octave_Grader':
        dbname = '%s/answers/%s' % (quiz_dir, request.POST['database-file'])
        dbname = escapeshellarg(dbname)
    else:
        dbname = '%s/data/%s' % (quiz_dir, request.POST['database-file'])
        dbname = escapeshellarg(dbname)

    # name of file containing correct query results
    ansfile = '%s/answers/%s' % (quiz_dir, request.POST['answer-file'])
    ansfile = escapeshellarg(ansfile)

    # question number used as index when reading ansfile
    qnum = escapeshellarg(request.POST['params[qnum]'])

    # query provided by user
    userans = escapeshellarg(request.POST['student_input'])

    # execute query userans on database using Python script

    grader = ''

    if (grader_name == 'DTD_Grader'):
        grader = 'DTD_Grader.py'
    elif grader_name == 'RA_Grader':
        grader = 'RA_Grader.py'
    elif grader_name == 'SQL_Grader':
        grader = 'SQL_Grader.py'
    elif grader_name == 'Data_Mod_Grader':
        grader = 'Data_Mod_Grader.py'
    elif grader_name == 'XML_Grader':
        grader = 'XML_Grader.py'
    elif grader_name == 'Trigger_Grader':
        grader = 'Trigger_Grader.py'
    elif grader_name == 'View_Trigger_Grader':
        grader = 'View_Trigger_Grader.py'
    elif grader_name == 'Octave_Grader':
        grader = 'Octave_Grader.py'



    innercmd = '%s -d %s -a %s -q %s -u %s' % ('python ' + settings.SANDBOX_DIR + '/' + grader, dbname, ansfile, qnum, userans)

    if settings.USE_CHROOT:
        ulimitcmd = "ulimit -t 10 -f 1000 " + innercmd
        esccmd = escapeshellarg(ulimitcmd)
        totalesccmd = "schroot -c sandbox -d /tmp -- bash -c " + esccmd
    else:
        esccmd = escapeshellarg(innercmd)
        totalesccmd = "bash -c " + esccmd


    process  = subprocess.Popen(totalesccmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    print out
    start = out.find('<score>')
    end = out.find('</score>')

    score = out[start + 7:end]

    if not score:
        score = '0';

    feedback = {'user_answer': userans,
                'score' : score,
                'explanation': out[end + 8:]}

    grade = {'score': score,
             'maximum-score': 1.0,
             'feedback': feedback}

    return  HttpResponse(simplejson.dumps(grade))


