# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import traceback

dProject = {

    'brandfind': 1,
    'mzcbase': 1,
    'mzcziran': 1,
    'intention': 1,
    'tongxin': 1,
    'ip': 1,
    'semeval': 1

}


@csrf_exempt
def guide(request):
    sProject = request.POST.get('project').strip()
    jParam = request.POST.get('param').strip()

    sResult = "bad parameter"
    # parameter check
    if check(sProject, jParam):
        sImport = "intelligent.dm.project.%s.master" % sProject
        stringmodule = __import__(sImport, fromlist=["*"])
        sResult = stringmodule.predict(jParam)

    return HttpResponse(sResult)


def check(sProject, jParam):
    logger = logging.getLogger("errinfo")

    # project check
    if not sProject.strip() in dProject:
        sError = "project parameter error : %s" % sProject
        logger.error(sError)
        return False

    if sProject == 'semeval':
        return True

    # parameter check
    try:
        json.loads(jParam)

    except:
        sError = "no json param : %s   traceback: %s" % (jParam, traceback.format_exc())
        logger.error(sError)
        return False

    return True
