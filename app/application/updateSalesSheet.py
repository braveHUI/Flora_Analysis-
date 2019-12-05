# ==============================================================================
#
#         FILE: updateSalesSheet.py
#
#        USAGE: ./updateSalesSheet.py
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


def updateSalesSheet(salessheet, username):
    dfinfo = pd.read_excel(salessheet, encoding="UTF-8", dtype=str)
    translate2db = CONFIG.json4PYSampleInfo
    zh2en = readTranslate(translate2db)
    samplelist = {}

    for col in dfinfo:
        line = 1
        for row in dfinfo[col]:
            if pd.isnull(row):
                continue
            elif 'nan' == row:
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

        if 'PriSID' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            return False
        if 'Sales_PYID' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            return False
        if 'Tube_ID' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            return False
        else:
            tubeinfo['Tube_ID'] = str(tubeinfo['Tube_ID'])
        if 'Sales_items' not in tubeinfo:
            db.session.rollback()
            db.session.close()
            return False
        if 'Sales_record_date' not in tubeinfo:
            tubeinfo['Sales_record_date'] = today
        elif isinstance(tubeinfo['Sales_record_date'], str):
            tubeinfo['Sales_record_date'] = datetime.strptime(
                tubeinfo['Sales_record_date'], "%Y-%m-%d %H:%M:%S")
        else:
            tubeinfo['Sales_record_date'] = \
                tubeinfo['Sales_record_date'].to_pydatetime()

        sampleinfo = SampleInfo.query.filter_by(
            PriSID=int(tubeinfo['PriSID'])).filter(
            SampleInfo.Tube_ID == tubeinfo['Tube_ID'],
            SampleInfo.Status < 8).first()
        if None == sampleinfo:
            db.session.rollback()
            db.session.close()
            return False
        else:
            sampleinfo.Sales_PYID = tubeinfo['Sales_PYID']
            sampleinfo.Sales_items = tubeinfo['Sales_items']
            sampleinfo.Sales_record_date = tubeinfo['Sales_record_date']
            if 'Report_name' in tubeinfo:
                sampleinfo.Report_name = tubeinfo['Report_name']
            if 'Report_phone' in tubeinfo:
                sampleinfo.Report_phone = str(tubeinfo['Report_phone'])
            db.session.commit()

    db.session.commit()
    db.session.close()
    return True
