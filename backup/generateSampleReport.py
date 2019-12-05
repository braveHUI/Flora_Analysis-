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

from .generateSampleJson import SampleJSON
from .PYSeqInfo import PYSeqConfig, PYSeqInfo


class PYScriptPath:
    condapath = "/work/instal/miniconda2/bin/"
    PYReportPdf = "/work/instal/miniconda2/envs/json_generate_report/"
    samplereport = "/home/instal/biosoft/pg/json_generate_report/people_generate_report.py"


PYReportCONF = config['development']
PYReportType = {
    'tiyan',
    'quanjian'
}


def SampleReportSuccess(Tube_ID, PriSID, ReportType):
    if ReportType not in PYReportType:
        return False

    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    path4pdf = os.path.join(path2sample, Tube_ID +
                            "_" + ReportType + ".pdf")
    if os.path.exists(path4pdf):
        return True
    else:
        return False


@celery.task()
def SampleReport(Tube_ID, PriSID, ReportType):
    if ReportType not in PYReportType:
        return False

    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    exeshell = os.path.join(path2sample, "samplereport.sh")
    logshell = os.path.join(path2sample, "samplereport.log")
    errshell = os.path.join(path2sample, "samplereport.err")
    with open(exeshell, 'w') as save:
        print("export PATH=" + PYScriptPath.condapath +
              ":/usr/local/bin:/usr/bin:/bin:$PATH", file=save)
        print("source activate " + PYScriptPath.PYReportPdf, file=save)
        print("echo $PATH", file=save)
        print("conda info --envs", file=save)
        print("python", PYScriptPath.samplereport,
              "-i", path2sample, "-b", ReportType, file=save)
    try:
        os.system("sh " + exeshell + " 1>" + logshell + " 2>" + errshell)
    except:
        return False

    return True


def SampleReportClear(Tube_ID, PriSID, ReportType):

    if ReportType not in PYReportType:
        return False

    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    path4report = os.path.join(path2sample, Tube_ID +
                               "_" + ReportType + ".pdf")
    if os.path.exists(path4report):
        os.remove(path4report)

    return True
