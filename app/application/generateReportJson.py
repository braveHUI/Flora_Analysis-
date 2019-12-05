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
from app.config import DevelopmentConfig
from app.application.probiotic_screening1 import ProbioticScreening

PYSeqCONF = PYSeqConfig['PYSeqConfig']

PYSeq_engine = create_engine(PYSeqCONF.DBURL, poolclass=NullPool)
DBSession = sessionmaker(bind=PYSeq_engine)
PYSeqSession = DBSession()


class PYScriptPath:
    # condapath = "/share/data7/opt/miniconda3/bin/"
    # PYReportJson = "/share/data7/opt/miniconda3/envs/PYbiom_generate_bigjson"
    # samplejson = "/share/data7/opt/biom_generate_bigjson/Run_bigjson.py"
    condapath = os.environ.get("condapath")
    PYReportJson = os.environ.get("PYReportJson")
    samplejson = os.environ.get("samplejson")



PYReportCONF = config['development']


def ReportJSONSuccess(Tube_ID, PriSID):
    print("ReportJSONSuccess is running")
    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    path4json = os.path.join(path2sample, "bigfile.json")
    print(f"ReportJSONSuccess  path4json : {path4json}")
    if os.path.exists(path4json):
        return True
    else:
        return False


@celery.task()
def ReportJSON(Tube_ID, PriSID):
    print("celery ReportJSON is running")
    if False == SampleBIOM(Tube_ID, PriSID):   # SampleBIOM 为复制biom文件
        # print("SampleBiom failure!"+Tube_ID)
        update_result_file = os.path.join(DevelopmentConfig.base_path, 'static', "IDS_cannot_run.txt")#DevelopmentConfig
        with open(update_result_file, "a+") as f:
            f.write(Tube_ID+"\tSampleBiom failure!"+"\n")
        return False

    samplejson = SampleJSON(Tube_ID) #生成sampleinfo.json文件
    if False == samplejson:
        print("Don't have "+Tube_ID+":CloseRef.biom!")
        return False

    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    print("path2sample: {}".format(path2sample))
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
    print(f"exeshell: {exeshell}")
    with open(exeshell, 'w') as save:
        # print("export PATH=/share/apps/perl5/bin:$PATH", file=save)
        print("export PATH=/mnt/hegh/Miniconda3/bin/:$PATH", file=save)
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


@celery.task()
def probioticReport(Tube_ID, PriSID):
    print("celery probioticReport is running")
    if False == SampleBIOM(Tube_ID, PriSID):   # SampleBIOM 为复制biom文件
        # print("SampleBiom failure!"+Tube_ID)
        update_result_file = os.path.join(DevelopmentConfig.base_path, 'static', "IDS_cannot_run.txt")#DevelopmentConfig
        with open(update_result_file, "a+") as f:
            f.write(Tube_ID+"\tSampleBiom failure!"+"\n")
        print("update_result_file : {}".format(update_result_file))
    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    print("path2sample: {}".format(path2sample))
    biom_path = os.path.join(path2sample, 'CloseRef.biom')
    out_path = os.path.join(PYReportCONF.PYReport, subfold)
    if not os.path.exists(biom_path):
        return False
    new_biom_path = os.path.join(path2sample, Tube_ID + '.biom')
    os.rename(biom_path, new_biom_path)
    print(f"new_biom_path : {new_biom_path}")
    print(f"Tube_ID:{Tube_ID}")
    ps = ProbioticScreening(Tube_ID, new_biom_path, out_path)
    flag = ps.run()


def ReportJSONClear(Tube_ID, PriSID):
    subfold = str(int(PriSID / 1000))
    path2sample = os.path.join(PYReportCONF.PYReport, subfold, Tube_ID)
    savejson = os.path.join(path2sample, "sampleinfo.json")
    if os.path.exists(savejson):
        os.remove(savejson)
    bigfilejson = os.path.join(path2sample, "bigfile.json")
    if os.path.exists(bigfilejson):
        os.remove(bigfilejson)
    closerefbiom = os.path.join(path2sample, "CloseRef.biom")
    if os.path.exists(closerefbiom):
        os.remove(closerefbiom)

    return True
