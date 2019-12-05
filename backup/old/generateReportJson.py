# ==============================================================================
#
#         FILE: generateReportJson.py
#
#        USAGE: ./generateReportJson.py
#
#  DESCRIPTION:
#
#      OPTIONS: ---
# REQUIREMENTS: ---
#         BUGS: ---
#        NOTES: ---
#       AUTHOR: ZHOU Yuanjie (ZHOU YJ), libranjie@gmail.com
# ORGANIZATION: R & D Department
#      VERSION: 1.0
#      CREATED: Tue May 22 16:14:31 CST 2018
#     REVISION: 2018.May22-16.14
# ==============================================================================
import json
import os
import re
import sys
from datetime import datetime

from app import celery, config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .generateSampleBiom import SampleBIOM
from .generateSampleJson import SampleJSON
from .PYSeqInfo import PYSeqConfig, PYSeqInfo

PYSeqCONF = PYSeqConfig['PYSeqConfig']

PYSeq_engine = create_engine(PYSeqCONF.DBURL, poolclass=NullPool)
DBSession = sessionmaker(bind=PYSeq_engine)
PYSeqSession = DBSession()


class PYScriptPath:
    condapath = "/work/instal/miniconda2/bin" 
    PYReportJson = "/work/instal/miniconda2/envs/PYbiom_generate_bigjson"
    samplejson = "/home/instal/biosoft/pg/biom_generate_bigjson/Run_bigjson.py"


PYReportCONF = config['development']


def ReportJSONSuccess(Tube_ID, PriSID):
    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    path4json = os.path.join(path2sample, "bigfile.json")
    if os.path.exists(path4json):
        return True
    else:
        return False


@celery.task()
def ReportJSON(Tube_ID, PriSID):
    if False == SampleBIOM(Tube_ID, PriSID):
        return False

    samplejson = SampleJSON(Tube_ID)
    if False == samplejson:
        return False

    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    savejson = os.path.join(path2sample, "sampleinfo.json")
    exeshell = os.path.join(path2sample, "samplejson.sh")
    logshell = os.path.join(path2sample, "samplejson.log")
    errshell = os.path.join(path2sample, "samplejson.err")
    bigfilejson = os.path.join(path2sample, "bigfile.json")
    if os.path.exists(bigfilejson):
        return True
    with open(savejson, 'w', encoding="UTF-8") as save:
        json.dump(samplejson, save, ensure_ascii=False,
                  sort_keys=True, indent=4, separators=(',', ': '))
    with open(exeshell, 'w') as save:
        print("export PATH=" + PYScriptPath.condapath +
              ":/usr/local/bin:/usr/bin:/bin:$PATH", file=save)
        print("source activate " + PYScriptPath.PYReportJson, file=save)
        print("echo $PATH", file=save)
        print("conda info --envs", file=save)
        print("python", PYScriptPath.samplejson,
              "-r -i", path2sample, file=save)
    try:
        os.system("sh " + exeshell + " 1>" + logshell + " 2>" + errshell)
    except:
        return False

    return True


def ReportJSONClear(Tube_ID, PriSID):
    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    savejson = os.path.join(path2sample, "sampleinfo.json")
    if os.path.exists(savejson):
        os.remove(savejson)
    bigfilejson = os.path.join(path2sample, "bigfile.json")
    if os.path.exists(bigfilejson):
        os.remove(bigfilejson)

    return True
