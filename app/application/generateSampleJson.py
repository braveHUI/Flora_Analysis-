# ==============================================================================
#
#         FILE: generateSampleJson.py
#
#        USAGE: ./generateSampleJson.py
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
import os
import sys
from datetime import datetime

from app import db
from app.database import Questionnaire, SampleInfo


def SampleJSON(Tube_ID):
    print("SampleJSON is running")
    sampleinfo = SampleInfo.query.filter_by(
        Tube_ID=Tube_ID).filter(
        SampleInfo.Status != 8, SampleInfo.Questionnaire_status > 0).first()
    question = Questionnaire.query.filter_by(Tube_ID=Tube_ID).first()
    if None == sampleinfo:
        db.session.close()
        return False
    elif None == question:
        db.session.close()
        return False
    else:
        today = datetime.now()
        samplejson = {}
        if None == sampleinfo.Production_date:
            sampleinfo.Production_date = today
        sampleinfo.Report_date = today
        db.session.commit()
        samplejson['UserInfo'] = sampleinfo.SampleInfo2reportJSON()
        samplejson['Questionnaire'] = question.Questionnaire2dict()
        if None == samplejson['Questionnaire']['BMI']:
            samplejson['Questionnaire']['BMI'] = 22
        db.session.close()
        return samplejson
