# ==============================================================================
#
#         FILE: insertApplySheet.py
#
#        USAGE: ./insertApplySheet.py
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
#     REVISION: 2018.May7-11.00
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
from app.database import SampleInfo, UserInfo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .common import readTranslate, translate4db

CONFIG = config['development']


def insertApplySheet(applysheet, username):
    dfinfo = pd.read_excel(applysheet, encoding="UTF-8")
    translate2db = CONFIG.json4PYSampleInfo
    zh2en = readTranslate(translate2db)
    samplelist = {}
    print("dfinfo:{}".format(dfinfo))
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
    print("samplelist:{}".format(samplelist))
    today = datetime.now()
    for sample in samplelist:
        print(samplelist[sample])
        tubeinfo = translate4db(samplelist[sample],
                                zh2en)
        print(tubeinfo)
        if 'Agent_manager' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            print('lack Agent_manager')
            return False
        else:
            print(tubeinfo['Agent_manager'])
            user_info = UserInfo.query.filter_by(
                realname=tubeinfo['Agent_manager']).first()
            if None == user_info:
                db.session.rollback()
                db.session.close()
                print("uncorrect Agent_manager")
                return False

        if 'Agent_contacts' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            print("lack Agent_contacts")
            return False

        if 'Agent_sampleid' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            print("lack Agent_sampleid")
            return False
        else:
            tubeinfo['Agent_sampleid'] = str(tubeinfo['Agent_sampleid'])

        if 'Release_apply_date' in tubeinfo:
            tubeinfo['Release_apply_date'] = \
                tubeinfo['Release_apply_date'].to_pydatetime()
        else:
            tubeinfo['Release_apply_date'] = today

        if 'Report_type' in tubeinfo:
            if int != type(int(tubeinfo['Report_type'])):
                db.session.rollback()
                db.session.close()
                print("unright Report_type")
                return False

        if 'PYFormula_status' in tubeinfo:
            if int != type(int(tubeinfo['PYFormula_status'])):
                db.session.rollback()
                db.session.close()
                print("unright PYFormula_status")
                return False
        sampleinfo = SampleInfo.query.filter(
            SampleInfo.Agent_sampleid == str(tubeinfo['Agent_sampleid']),
            SampleInfo.Status < 8).first()
        if None != sampleinfo:
            db.session.rollback()
            db.session.close()
            print("None != sampleinfo")
            return False
        else:
            sampleinfo = SampleInfo(
                Agent_sampleid=str(tubeinfo['Agent_sampleid']))
            sampleinfo.SampleInfo2insert(tubeinfo)
            sampleinfo.Release_apply_user = username
            db.session.add(sampleinfo)
            # print(sampleinfo.SampleInfo2dict())
            db.session.commit()

    db.session.commit()
    db.session.close()
    return True
