# ==============================================================================
#
#         FILE: updateSampleBack.py
#
#        USAGE: ./updateSampleBack.py
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
#      CREATED: Thu Apr 19 15:16:16 CST 2018
#     REVISION: 2018.Apr24-09.53
# ==============================================================================
import argparse
import codecs
import json
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from app import celery, db
from app.config import config
from app.database import SampleInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .common import translate4db

CONFIG = config['development']


def readTranslate(translate):
    with open(translate, 'r', encoding="UTF-8") as trans:
        zh2en = json.load(trans)
        return zh2en
    return False


def updateSampleBack(sampleback, username):
    dfinfo = pd.read_excel(sampleback, encoding="UTF-8", dtype=str)
    translate2db = CONFIG.json4PYSampleInfo
    zh2en = readTranslate(translate2db)
    samplelist = {}

    for col in dfinfo:
        line = 1
        for row in dfinfo[col]:
            if pd.isnull(row):
                continue
            if line in samplelist:
                pass
            else:
                samplelist[line] = {}
            samplelist[line][col] = row
            line += 1

    today = datetime.now()
    for sample in samplelist:
        tubeinfo = translate4db(samplelist[sample],
                                zh2en)

        if 'Tube_ID' not in tubeinfo:
            db.session.close()
            return False
        else:
            tubeinfo['Tube_ID'] = str(tubeinfo['Tube_ID'])

        if 'Sample_ID' not in tubeinfo:
            db.session.close()
            return False
        else:
            tubeinfo['Sample_ID'] = str(tubeinfo['Sample_ID'])

        if 'Sample_status' not in tubeinfo:
            db.session.close()
            return False

        sampleinfo = SampleInfo.query.filter(
            SampleInfo.Tube_ID == tubeinfo['Tube_ID'],
            SampleInfo.Status < 8).first()
        if None == sampleinfo:
            db.session.rollback()
            db.session.close()
        else:
            sampleinfo.Sample_ID = tubeinfo['Sample_ID']
            if '1' == tubeinfo['Sample_status']:
                sampleinfo.Status = 8
                sampleinfo.Sample_status = 1
            elif 0 < sampleinfo.Questionnaire_status:
                sampleinfo.Status = 4
                sampleinfo.Sample_status = 0
            else:
                sampleinfo.Status = 3
                sampleinfo.Sample_status = 0

            if "Sample_back_date" in tubeinfo:
                try:
                    sampleinfo.Sample_back_date = datetime.strptime(tubeinfo["Sample_back_date"], "%Y-%m-%d")
                except ValueError:
                    sampleinfo.Sample_back_date = datetime.strptime(tubeinfo["Sample_back_date"], "%Y-%m-%d %H:%M:%S")
            else:
                sampleinfo.Sample_back_date = today
            sampleinfo.Sample_back_user = username
            sampleinfo.PYFormula_update_date = today
            if 'Sample_back_express_ID' in tubeinfo:
                sampleinfo.Sample_back_express_ID = \
                    str(tubeinfo['Sample_back_express_ID'])

    db.session.commit()
    db.session.close()
    return True
