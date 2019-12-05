# ==============================================================================
#
#         FILE: scheduleTask.py
#
#        USAGE: ./scheduleTask.py
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
#      CREATED: Wed May 16 15:45:28 CST 2018
#     REVISION: 2018.May22-16.14
# ==============================================================================
import json
import os
from datetime import datetime
from time import sleep

import requests

from app import celery, db
from app.application import (ReportJSON, ReportJSONSuccess, SampleReport,
                             SampleReportSuccess, readTranslate, probioticReport)
from app.config import config,DevelopmentConfig
from app.database import Questionnaire, SampleInfo

CONF = config['development']
en2zh = readTranslate(CONF.json4PYSampleStatus)
zh2en = readTranslate(CONF.json4PYSampleInfo)


@celery.task()
def syncQuestionnaireStatus():
    today = datetime.now()
    print("调试1：{}".format("*" * 100))
    sampleinfo = SampleInfo.query.filter(
        SampleInfo.Status > 1, SampleInfo.Status < 4).order_by(
        SampleInfo.PriSID).all()
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        print("调试2：{}".format("*"*100))
        for sample in sampleinfo:
            print("sample.Tube_ID:{}".format(sample.Tube_ID))
            question = Questionnaire.query.filter_by(
                Tube_ID=sample.Tube_ID).first()
            if None == question:
                question = Questionnaire()
                question.Questionnaire2insert(
                    sample.SampleInfo2Questionnaire())
                db.session.add(question)
                db.session.commit()

            elif 0 < question.Questionnaire_status:
                sample.Questionnaire_status = question.Questionnaire_status
                db.session.commit()
                if 3 == sample.Status:
                    sample.Status = 4
                    sample.Receive_date = today
                    sample.PYFormula_update_date = today
                    db.session.commit()

            if 3 == sample.Status and None == question.Sample_ID:
                question.Sample_ID = sample.Sample_ID
                db.session.commit()

        db.session.close()
        return True


@celery.task()
def syncQuestionnaireSheet():
    sampleinfo = SampleInfo.query.filter(
        SampleInfo.Status > 1, SampleInfo.Status < 4).order_by(
        SampleInfo.PriSID).all()
    print(f"sampleinfo: {sampleinfo}")
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        samplelist = {}
        line = 1
        for sample in sampleinfo:
            tubeinfo = sample.SampleInfo2Questionnaire()
            question = Questionnaire.query.filter_by(
                Tube_ID=tubeinfo['Tube_ID']).first()
            if None != question:
                samplelist[line] = tubeinfo
                line += 1

        if 0 == len(samplelist):
            db.session.close()
            return False
    print(f"samplelist: {samplelist}")
    syncjson = {}
    # syncjson['auth'] = CONF.syncauth
    # syncjson['samples'] = json.dumps(samplelist)
    syncjson = json.dumps(samplelist)
    print("CONF.syncurl:{}".format(CONF.syncurl))
    request = requests.post(
        url=CONF.syncurl, data=syncjson, headers=CONF.synchead)
    print(f"request: {request}")
    statuscode = request.status_code
    if 200 == statuscode:
        samplejson = json.loads(json.dumps(request.json()))
        if 0 == len(samplejson):
            db.session.close()
            return False
        for sample in samplejson:
            print(f"{samplejson[sample]['Sample_ID']}Questionnaire_status:{samplejson[sample]['Questionnaire_status']}")
            if 0 == samplejson[sample]['Questionnaire_status']:
                continue
            question = Questionnaire.query.filter_by(
                Tube_ID=samplejson[sample]['Tube_ID']).first()
            if None == question:
                db.session.rollback()
                db.session.close()
                return False
            else:

                print(f"调试1：{'*'*200}")
                question.Questionnaire2update(samplejson[sample])
                s = SampleInfo.query.filter_by(Tube_ID = samplejson[sample]['Tube_ID']).first()
                s.insert_name(samplejson[sample])
        db.session.commit()
        db.session.close()
    else:
        print(statuscode, syncjson)
        db.session.close()
        return False


@celery.task()
def autoJSONReport():
    print("autoJSONReport is running")
    sampleinfo = SampleInfo.query.filter_by(
        Status=4).order_by(
        SampleInfo.PriSID).group_by(
        SampleInfo.Tube_ID).all()
    # SampleInfo.Tube_ID).limit(10)
    # SampleInfo.PriSID).all()
    print("autoJSONReport  sampleinfo: {sampleinfo}")
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        update_result_file = os.path.join(DevelopmentConfig.base_path, 'static',
                                          "IDS_cannot_run.txt")  # DevelopmentConfig
        print("update_result_file:{}".format(update_result_file))
        failure_samples = ''
        if os.path.exists(update_result_file):
            with open(update_result_file,'r') as f:
                failure_samples = f.read()
        print(f"failure_samples:{failure_samples}")
        for sample in sampleinfo:
            if sample.Project_name == "probiotics":
                probioticReport.delay(sample.Tube_ID, sample.PriSID)
            elif sample.Tube_ID not in failure_samples:
                print(f"sample.Tube_ID:{sample.Tube_ID}")
                ReportJSON.delay(sample.Tube_ID, sample.PriSID)


        db.session.close()
        return True


@celery.task()
def autoJSONStatus():
    print("celery autoJSONStatus is running")
    sampleinfo = SampleInfo.query.filter_by(
        Status=4).order_by(
        SampleInfo.PriSID).all()
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        for sample in sampleinfo:
            if True == ReportJSONSuccess(sample.Tube_ID, sample.PriSID):
                print(f"{sample.Tube_ID} json 文件生成成功")
                today = datetime.now()
                sample.Status = 5
                sample.JSON_date = today
                sample.PYFormula_update_date = today
                db.session.commit()

        db.session.close()
        return True


@celery.task()
def autoSampleReport():
    print("autoSampleReport is running")
    sampleinfo = SampleInfo.query.filter_by(
        Status=5).filter(
        SampleInfo.Project_name.in_(
            ['tiyan', 'quanjian', 'medicine', 'infant-nu', 'tumour_medicine'])).order_by(
        SampleInfo.PriSID).group_by(
        SampleInfo.Tube_ID).limit(10)
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        pass
    print(f"测试生成pdf:{'*'*200}")
    for sample in sampleinfo:
        if sample.Project_name in zh2en['translate4db']['Project_name']['Value']:
            sample.Project_name = \
                zh2en['translate4db']['Project_name']['Value'][
                    sample.Project_name]
            today = datetime.now()
            sample.Report_date = today
            db.session.commit()
        if SampleReport(
            sample.Tube_ID, sample.PriSID, sample.Project_name):
            print(f"pdf生成成功:{'*'*200}")
    db.session.close()
    return True


@celery.task()
def autoSampleStatus():
    print("celery autoSampleStatus is running")
    sampleinfo = SampleInfo.query.filter_by(
        Status=5).filter(
        SampleInfo.Project_name.in_(
            ['tiyan', 'quanjian', 'medicine', 'infant-nu', 'probiotics', 'tumour_medicine'])).order_by(
        SampleInfo.PriSID).all()
    if None == sampleinfo:
        db.session.close()
        return True
    else:
        for sample in sampleinfo:
            if True == SampleReportSuccess(
                sample.Tube_ID, sample.PriSID, sample.Project_name,
                    en2zh['translate4web']['Project_name']['suffix'][
                    sample.Project_name]):
                print(f"{sample.Tube_ID} 报告生成成功")
                today = datetime.now()
                sample.Status = 6
                sample.PYFormula_update_date = today
                db.session.commit()

        db.session.close()
        return True
