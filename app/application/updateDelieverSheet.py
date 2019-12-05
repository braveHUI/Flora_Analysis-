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
#      CREATED: Tue May 29 10:26:44 CST 2018
#     REVISION: 2018.Jun22-18.01
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

from .common import readTranslate, translate4db

CONFIG = config['development']


def updateDelieverSheet(sampleback, username):
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

        if 'PriSID' not in tubeinfo:
            db.session.close()
            return False

        sampleinfo = SampleInfo.query.filter_by(
            PriSID=int(tubeinfo['PriSID']),
            Tube_ID=tubeinfo['Tube_ID']).first()
        if None == sampleinfo:
            db.session.rollback()
            db.session.close()
            return False
        elif 6 != sampleinfo.Status:
            continue
        else:
            sampleinfo.Status = 7
            if 'PYFormula_express_ID' in tubeinfo:
                sampleinfo.PYFormula_express_ID = \
                    str(tubeinfo['PYFormula_express_ID'])

            sampleinfo.PYFormula_express_date = today
            sampleinfo.PYFormula_express_user = username
            sampleinfo.PYFormula_update_date = today

    db.session.commit()
    db.session.close()
    return True
