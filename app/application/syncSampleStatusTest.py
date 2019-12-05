# ==============================================================================
#
#         FILE: syncSampleStatus.py
#
#        USAGE: ./syncSampleStatus.py
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
import base64
import hashlib
import json

import requests

from urllib import parse


class syncConfig:
    # API账户，非真实账户
    api_user = "prome"
    # APIKey，非真实Key。请妥善保管，不能告知他人。
    api_key = "2837176c146a3d18db8e978fb697550f"
    syncurl = "https://api.promegene.com/prome/samplingtube/add/"
    #synchead = {'content-type': 'application/json'}
    synchead = {}


syncConfigAPI = {'syncConfig': syncConfig}


def syncSampleStatus():

    samplelist = [{'distributor': 1, 'code': 'F1803513', 'exam_item': '4', 'bind_num': 1}, {'distributor': 1, 'code': '1000008400', 'exam_item': '4', 'bind_num': 1}, {'distributor': 1, 'code': '5100004254', 'exam_item': '4', 'bind_num': 1}]
    request_data_json = json.dumps(samplelist)
    print (samplelist)
    print (request_data_json)

    md5 = hashlib.md5()
    md5.update((request_data_json + syncConfig.api_key).encode("utf-8"))
    data_sign = base64.b64encode(md5.hexdigest().encode("utf-8"))
    data_json = forSyncAPI(request_data_json, data_sign, syncConfig.api_user)

    print(data_json)

    request = requests.post(
        url=syncConfig.syncurl, data=data_json, headers=syncConfig.synchead)

    statuscode = request.status_code
    print (statuscode)
    return True


def forSyncAPI(request_data, data_sign, api_user):
    json = {
        'request_data': parse.quote(request_data),
        'data_sign': parse.quote(data_sign),
        'api_user': api_user
        }
    return json


def forSyncStatus(self):
    data = {
        'distributor': 1,
        'code': self.Tube_ID,
        'exam_item': '4',
        'bind_num': 1
    }
    return data


syncSampleStatus()
