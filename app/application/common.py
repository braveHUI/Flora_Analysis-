import json
import os
from datetime import datetime, timedelta

import pandas as pd
import xlwt
from app import config, db
from app.database import SampleInfo, UserInfo

CONF = config['development']


def excel_to_json(src, dest):
    data = pd.read_excel(src, index_col=0)
    temp = data.to_json(orient='index')
    json_data = json.loads(temp)
    for key, value in json_data.items():
        json_data[key]['id'] = key
    f = open(dest, 'w')
    json.dump(json_data, f)
    f.close()


def excel_to_tsv(src, dest):
    if os.path.exists(src) == False:
        raise FileNotFoundError
    data = pd.read_excel(src, index_col=0)
    tsv_data = data.to_csv(sep='\t')
    f = open(dest, 'w')
    f.writelines(tsv_data)
    f.close()


def json_to_tsv(json_data, dest):
    sample_id = list(json_data.keys())
    col_name_list = list(json_data[sample_id[0]].keys())
    col_name_list.remove('id')
    col_name_list.insert(0, '#SampleID')
    f = open(dest, 'w')
    buffer = ['\t'.join(col_name_list) + '\n']
    for pyid, d in json_data.items():
        line = [pyid]
        d.pop('id')
        for key, value in d.items():
            line.append(value)
        line = '\t'.join(line)
        buffer.append(line + '\n')
    f.writelines(buffer)
    f.close()


def json_to_xls(json_data, dest):
    col_name_list = list(json_data[1].keys())
    book = xlwt.Workbook()
    sheet = book.add_sheet('ReleaseUpdate', cell_overwrite_ok=True)
    col = 0
    for i in col_name_list:
        sheet.write(0, col, i)
        col += 1

    for row in json_data:
        col = 0
        for i in col_name_list:
            sheet.write(row, col, json_data[row][i])
            col += 1

    book.save(dest)


def query_users(realname='', username=''):
    if realname == '':
        realname = '%'
    if username == '':
        username = '%'
    users = UserInfo.query.filter(UserInfo.realname.like(realname),
                                  UserInfo.username.like(username))
    return users


def query_by_regular(status, tube_id, agent_manager, time_start, time_end, tag):
    print("query_by_regular is running")
    today = datetime.now()
    if '' == status:
        status = '%'
    if '' == agent_manager:
        agent_manager = '%'
    if '' == time_start:
        time_start = 0

    if '' == time_end:
        time_end = today
    else:
        time_end = datetime.strptime(time_end, "%Y-%m-%d")
        time_end += timedelta(days=1)
    if '' == tube_id:
        samples = SampleInfo.query.filter(
            SampleInfo.Status.like(status),
            SampleInfo.Tag.like('%' + tag + '%') if tag else '',
            SampleInfo.Agent_manager.like('%' + agent_manager + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()
    else:
        samples = SampleInfo.query.filter(
            SampleInfo.Status.like(status),
            SampleInfo.Tag.like('%' + tag + '%')if tag else '',
            SampleInfo.Tube_ID.like('%' + tube_id + '%'),
            SampleInfo.Agent_manager.like('%' + agent_manager + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()
    print(f"samples:{samples}")
    db.session.close()
    return samples


def query_by_manager(status, tube_id, agent_manager, agent_contacts,
                     time_start, time_end):
    today = datetime.now()
    if '' == status:
        status = '%'
    if '' == agent_contacts:
        agent_contacts = '%'
    if '' == time_start:
        time_start = 0
    if '' == time_end:
        time_end = today
    else:
        time_end = datetime.strptime(time_end, "%Y-%m-%d")
        time_end += timedelta(days=1)

    # print(status, "\t", tube_id, "\t", agent_manager, "\t",
    #       agent_contacts, "\t", time_start, "\t", time_end)

    if '' == tube_id:
        samples = SampleInfo.query.filter_by(
            Agent_manager=agent_manager).filter(
            SampleInfo.Status.like(status),
            SampleInfo.Agent_contacts.like('%' + agent_contacts + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()
    else:
        samples = SampleInfo.query.filter_by(
            Agent_manager=agent_manager).filter(
            SampleInfo.Status.like(status),
            SampleInfo.Tube_ID.like('%' + tube_id + '%'),
            SampleInfo.Agent_contacts.like('%' + agent_contacts + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()

    db.session.close()
    return samples


def query_by_applyer(status, tube_id, apply_user, agent_contacts,
                     time_start, time_end):
    today = datetime.now()
    if '' == status:
        status = '%'
    if '' == agent_contacts:
        agent_contacts = '%'
    if '' == time_start:
        time_start = 0
    if '' == time_end:
        time_end = today
    else:
        time_end = datetime.strptime(time_end, "%Y-%m-%d")
        time_end += timedelta(days=1)

    # print(status, "\t", tube_id, "\t", agent_manager, "\t",
    #       agent_contacts, "\t", time_start, "\t", time_end)

    if '' == tube_id:
        samples = SampleInfo.query.filter_by(
            Release_apply_user=apply_user).filter(
            SampleInfo.Status.like(status),
            SampleInfo.Agent_manager != apply_user,
            SampleInfo.Agent_contacts.like('%' + agent_contacts + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()
    else:
        samples = SampleInfo.query.filter_by(
            Release_apply_user=apply_user).filter(
            SampleInfo.Agent_manager != apply_user,
            SampleInfo.Status.like(status),
            SampleInfo.Tube_ID.like('%' + tube_id + '%'),
            SampleInfo.Agent_contacts.like('%' + agent_contacts + '%'),
            SampleInfo.PYFormula_update_date > time_start,
            SampleInfo.PYFormula_update_date <= time_end).order_by(
            SampleInfo.Status, -SampleInfo.PriSID).all()

    db.session.close()
    return samples


def samplelist2json(samplelist):
    data = {}
    for sample in samplelist:
        sampleinfo = SampleInfo.query.filter_by(PriSID=sample).first()
        data[sampleinfo.PriSID] = sampleinfo.SampleInfo2dict()

    db.session.close()
    return data


def samplelist2release(samplelist, SampleInfoEN2ZH):
    data = {}
    line = 1
    for sample in samplelist:
        sampleinfo = SampleInfo.query.filter_by(PriSID=sample).first()
        data[line] = translate4xls(
            sampleinfo.SampleInfo2release(), SampleInfoEN2ZH)
        line += 1

    db.session.close()
    return data


def samplelist2deliever(samplelist, SampleInfoEN2ZH):
    data = {}
    line = 1
    for sample in samplelist:
        sampleinfo = SampleInfo.query.filter_by(PriSID=sample).first()
        data[line] = translate4xls(
            sampleinfo.SampleInfo2deliever(), SampleInfoEN2ZH)
        line += 1

    db.session.close()
    return data


def samplelist2sales(samplelist, SampleInfoEN2ZH):
    data = {}
    line = 1
    for sample in samplelist:
        sampleinfo = SampleInfo.query.filter(
            SampleInfo.Status > 2).filter_by(PriSID=sample).first()
        if None == sampleinfo:
            continue
        data[line] = translate4xls(
            sampleinfo.SampleInfo2sales(), SampleInfoEN2ZH)
        line += 1

    db.session.close()
    return data


def readTranslate(translate):
    with open(translate, 'r', encoding="UTF-8") as trans:
        en2zh = json.load(trans)
        return en2zh
    return False


def translate4db(sampleinfo, zh2en):
    data = {}
    for col in sampleinfo:
        if col not in zh2en['translate4db']:
            continue
        column = zh2en['translate4db'][col]['Translate']
        if pd.isnull(sampleinfo[col]):
            continue
        if 'Value' in zh2en['translate4db'][col]:
            info = sampleinfo[col].split(u'|')
            vector = []
            for key in info:
                if key in zh2en['translate4db'][col]['Value']:
                    vector.append(str(zh2en['translate4db']
                                      [col]['Value'][key]))
                else:
                    vector.append(str(key))
            data[column] = "; ".join(vector)
        else:
            data[column] = sampleinfo[col]

    return data


def translate4web(sampleinfo, en2zh):
    data = {}
    for col in sampleinfo:
        if None == sampleinfo[col]:
            data[col] = ''
            continue
        if col in en2zh['translate4web'] \
                and 'Value' in en2zh['translate4web'][col]:
            info = str(sampleinfo[col]).split("; ")
            vector = []
            for key in info:
                if key in en2zh['translate4web'][col]['Value']:
                    vector.append(en2zh['translate4web']
                                  [col]['Value'][key])
                else:
                    vector.append(key)

            data[col] = "|".join(vector)

        else:
            data[col] = sampleinfo[col]

    return data


def translate4xls(sampleinfo, en2zh):
    data = {}
    for col in sampleinfo:
        if None == sampleinfo[col]:
            if col in en2zh['translate4web']:
                data[en2zh['translate4web'][col]['Translate']] = ""
            else:
                data[col] = ""

        elif col in en2zh['translate4web'] \
                and 'Value' in en2zh['translate4web'][col]:
            info = str(sampleinfo[col]).split("; ")
            vector = []
            for key in info:
                if key in en2zh['translate4web'][col]['Value']:
                    vector.append(en2zh['translate4web']
                                  [col]['Value'][key])
                else:
                    vector.append(key)

            data[en2zh['translate4web'][col]['Translate']] = "|".join(vector)

        elif col in en2zh['translate4web']:
            data[en2zh['translate4web'][col]['Translate']] = sampleinfo[col]
        else:
            data[col] = sampleinfo[col]

    return data
