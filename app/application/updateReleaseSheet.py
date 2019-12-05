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

from .common import readTranslate, translate4db

CONFIG = config['development']


def updateReleaseSheet(sampleback, username):
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
        elif 'Tube_expiry_date' not in tubeinfo:
            db.session.close()
            return False
        else:
            tubeinfo['Tube_ID'] = str(tubeinfo['Tube_ID'])

        if 'PriSID' not in tubeinfo:
            db.session.close()
            return False

        if 'Agent_sampleid' not in tubeinfo:
            db.session.close()
            return False
        else:
            tubeinfo['Agent_sampleid'] = str(tubeinfo['Agent_sampleid'])

        sampleinfo = SampleInfo.query.filter_by(
            PriSID=int(tubeinfo['PriSID']),
            Agent_sampleid=tubeinfo['Agent_sampleid']).first()
        if None == sampleinfo:
            db.session.rollback()
            db.session.close()
            return False
        elif 1 != sampleinfo.Status:
            continue
        else:
            sampleinfo.Tube_ID = tubeinfo['Tube_ID']
            sampleinfo.Tube_expiry_date = tubeinfo['Tube_expiry_date']
            sampleinfo.Status = 2
            if 'Tube_out_express_ID' in tubeinfo:
                sampleinfo.Tube_out_express_ID = \
                    str(tubeinfo['Tube_out_express_ID'])

            sampleinfo.Release_date = today
            sampleinfo.Release_user = username
            sampleinfo.PYFormula_update_date = today

    db.session.commit()
    db.session.close()
    return True
