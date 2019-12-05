import json
import os
import shutil
from datetime import datetime

from app import config, db
from app.application import (ReportJSONClear, SampleReportClear,
                             insertApplySheet, json_to_xls, query_by_applyer,
                             query_by_manager, query_by_regular, query_users,
                             readTranslate, samplelist2deliever,
                             samplelist2json, samplelist2release,
                             samplelist2sales, translate4web,
                             updateDelieverSheet, updateReleaseSheet, SampleReport,
                             updateSalesSheet, updateSampleBack)
from app.database import Questionnaire, SampleInfo
from app.decorators import (Admin_required, Consultant_required,
                            Manager_required, Production_required,
                            Reporter_required, Samplecenter_required,
                            Warehouse_required)
from flask import (make_response, redirect, render_template, request, url_for,
                   send_from_directory)
from flask_login import current_user, fresh_login_required, login_required
from werkzeug.utils import secure_filename

from . import interface

# from .common import excel_to_json, excel_to_tsv, json_to_tsv

CONF = config['development']
ALLOWED_EXTENSIONS = ['xls', 'xlsx', 'csv', 'pdf', 'docx']
SampleInfoEN2ZH = readTranslate(CONF.json4PYSampleStatus)
SampleInfoZH2EN = readTranslate(CONF.json4PYSampleInfo)
QuestionnaireEN2ZH = readTranslate(CONF.json4PYQuestionnaireStatus)
PYFormulaType = readTranslate(CONF.json4PYFormulaType)


def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1] in ALLOWED_EXTENSIONS


# ==============================================================================
# change_authority for Admin by samplelist.html
#      /UserInforPick
#      /UserInforUpload
# ==============================================================================
@interface.route('/UserInforPick', methods=['GET'])
def UserInforPick():
    samples = query_users()
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = sample.UserInfor2dict()
        line += 1
    return json.dumps(sample_list), 200,  {'content-type': 'application/json'}


@interface.route('/UserInforUpload', methods=['GET', 'POST'])
# @login_required
@fresh_login_required
@Admin_required
def UserInforUpload():
    select = request.json
    new_authority = select['Status'][1:]
    authoritys = new_authority.split(',')
    if "7" not in authoritys:
        return False
    else:
        samples = query_users()
        line = 0
        for sample in samples:
            sample.change_authority(authoritys[line])
            line += 1
        return 'success', 200,  {'content-type': 'application/json'}


# ==============================================================================
# samplelist
#     /sampleByDefault
#     /sampleByDetail
# ==============================================================================
@interface.route('/', methods=['POST', 'GET'])
@fresh_login_required
def index():
    return render_template('samplelist.html')


@interface.route('/sampleByDefault', methods=['GET'])
@login_required
def query_sample_by_default():
    samples = query_by_regular('', '', '', '', '','')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/sampleByDetail', methods=['POST'])
@login_required
def query_sample_by_detail():
    select = request.json
    status = select['Status']
    tube_id = select['Tube_ID']
    agent_manager = select['Agent_manager']
    time_start = select['Time_start']
    time_end = select['Time_end']
    print(type(select))
    tag = select['Tag'] if "tag" in select.keys() else None
    print(f"tag:{tag}")
    print(f"tube_id:{tube_id}")
    samples = query_by_regular(
        status, tube_id, agent_manager, time_start, time_end, tag)
    sample_list = {}
    line = 1
    print(f"samples:{samples}")
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


# ==============================================================================
@interface.route('/sampledetail', methods=['POST', 'GET'])
@login_required
def sample_detail():
    return render_template('sampledetail.html')


@interface.route('/sampleByPriSID', methods=['GET'])
@login_required
def query_sample_by_prisid():
    PriSID = request.args.get('key', '')
    sampleinfo = SampleInfo.query.filter_by(PriSID=PriSID).first()
    sampleinfo = translate4web(sampleinfo.SampleInfo2dict(), SampleInfoEN2ZH)
    db.session.close()
    return json.dumps(sampleinfo), 200, {'content-type': 'application/json'}


# ==============================================================================
# releaseapply
#     /applyByDefault
#     /applyByAgent
#     /applyByManager
#     /applyByProject
#     /uploadApplySheet
#     /updateApply
# ==============================================================================
@interface.route('/releaseapply', methods=['POST', 'GET'])
@login_required
@Manager_required
def releaseapply():
    return render_template('releaseapply.html')


@interface.route('/applyByDefault', methods=['GET'])
@login_required
def query_apply_by_default():
    username = current_user.username
    samples = query_by_regular(1, '', '', '', '', '')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_applyer(1, '', username, '', '', '')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/applyByAgent', methods=['GET'])
@login_required
def query_apply_by_agent():
    Agent = request.args.get('key', '')
    samples = SampleInfo.query.filter_by(Agent_name=Agent, Status=1).all()
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    db.session.close()
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/applyByManager', methods=['GET'])
@login_required
def query_apply_by_manager():
    Manager = request.args.get('key', '')
    samples = SampleInfo.query.filter_by(Agent_manager=Manager, Status=1).all()
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = sample.SampleInfo2dict()
        line += 1
    db.session.close()
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/applyByProject', methods=['GET'])
@login_required
def query_apply_by_project():
    Project = request.args.get('key', '')
    samples = SampleInfo.query.filter_by(Project_name=Project, Status=1).all()
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    db.session.close()
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


# upload excel file, which include apply informations.
@interface.route('/uploadApplySheet', methods=['POST'])
@fresh_login_required
def upload_apply_sheet():
    username = current_user.realname
    f = request.files['file']
    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)
        suffix = f.filename.split('.')[-1]
        dest_path = os.path.join(
            CONF.PYSamplesheet, "releaseapplysheet" + '.' + suffix)
        shutil.move(upload_path, dest_path)
        if insertApplySheet(dest_path, username):
            return 'success', 200
        else:
            return 'failed', 0


# ==============================================================================
# releaseupdate
#     /updateRelease
#     /download_releaseupdate
#     /upload_releaseupdate
# ==============================================================================
@interface.route('/releaseupdate', methods=['POST', 'GET'])
@login_required
@Warehouse_required
def releaseupdate():
    return render_template('releaseupdate.html')


@interface.route('/updateRelease', methods=['POST'])
@fresh_login_required
def update_release():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    print(f"sample: {sample}")
    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).order_by(SampleInfo.Status).first()
    if 'Tube_ID' not in sample:
        db.session.close()
        return 'empty', 300
    if 'Tube_expiry_date' not in sample:
        db.session.close()
        return 'empty', 405
    samplerepeat = SampleInfo.query.filter_by(
        Tube_ID=sample['Tube_ID']).filter(SampleInfo.Status != 8).first()
    print(f"samplerepeat: {samplerepeat}")
    if None != samplerepeat:
        db.session.close()
        return 'repeat', 300
    sampleinfo.Tube_ID = sample['Tube_ID']
    sampleinfo.Tube_out_express_ID = sample['Tube_out_express_ID']
    sampleinfo.Status = 2
    sampleinfo.Release_date = today
    sampleinfo.Tube_expiry_date = sample['Tube_expiry_date']
    sampleinfo.Release_user = username
    db.session.commit()
    db.session.close()
    return 'success', 200


@interface.route('/download_releaseupdate', methods=['POST'])
@fresh_login_required
def download_releaseupdate():
    samplelist = samplelist2release(request.json, SampleInfoEN2ZH)
    if 1 > len(list(samplelist.keys())):
        return 'empty', 300, {'content-type': 'application/json'}
    releasesheet = os.path.join(CONF.PYTemplate, "PYReleaseUpdate.xls")
    json_to_xls(samplelist, releasesheet)
    return 'success', 200, {'content-type': 'application/json'}


@interface.route('/uploadReleaseUpdate', methods=['POST'])
@fresh_login_required
def upload_releaseupdate():
    username = current_user.realname
    f = request.files['file']
    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)
        suffix = f.filename.split('.')[-1]
        dest_path = os.path.join(
            CONF.PYSamplesheet, "releaseupdate" + '.' + suffix)
        shutil.move(upload_path, dest_path)
        if updateReleaseSheet(dest_path, username):
            return 'success', 200
        else:
            return 'failed', 0


# ==============================================================================
# sampleback
#     /backByDefault
#     /uploadSampleBack
#     /invalidSampleBack
# ==============================================================================
@interface.route('/sampleback', methods=['POST', 'GET'])
@login_required
@Samplecenter_required
def sampleback():
    return render_template('sampleback.html')


@interface.route('/backByDefault', methods=['GET'])
@login_required
def query_back_by_default():
    samples = query_by_regular(2, '', '', '', '','')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_regular(3, '', '', '', '','')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/uploadSampleBack', methods=['POST'])
@fresh_login_required
def upload_sample_back():
    username = current_user.realname
    f = request.files['file']
    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)
        suffix = f.filename.split('.')[-1]
        dest_path = os.path.join(
            CONF.PYSamplesheet, "samplebacksheet" + '.' + suffix)
        shutil.move(upload_path, dest_path)

        if updateSampleBack(dest_path, username):
            return 'success', 200
        else:
            return 'failed', 0


# ==============================================================================
# dataproduct
#     /productByDefault
# ==============================================================================
@interface.route('/dataproduct', methods=['POST', 'GET'])
@login_required
@Production_required
def dataproduct():
    return render_template('dataproduct.html')


@interface.route('/productByDefault', methods=['GET'])
@login_required
def query_product_by_default():
    samples = query_by_regular(3, '', '', '', '', '')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_regular(4, '', '', '', '', '')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


# ==============================================================================
# delieverupdate
#     /delieverByDefault
#     /updateDeliever
#     /download_delieverupdate
#     /upload_delieverupdate
# ==============================================================================
@interface.route('/delieverupdate', methods=['POST', 'GET'])
@login_required
@Warehouse_required
def delieverupdate():
    return render_template('delieverupdate.html')


@interface.route('/delieverByDefault', methods=['GET'])
@login_required
def query_deliever_by_default():
    samples = query_by_regular(6, '', '', '', '', '')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    # samples = query_by_regular(7, '', '', '', '')
    # for sample in samples:
    #     sample_list[line] = translate4web(
    #         sample.SampleInfo2dict(), SampleInfoEN2ZH)
    #     line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/updateDeliever', methods=['POST'])
@fresh_login_required
def update_deliever():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).order_by(SampleInfo.Status).first()
    sampleinfo.PYFormula_express_ID = sample['PYFormula_express_ID']
    sampleinfo.Status = 7
    sampleinfo.PYFormula_express_date = today
    sampleinfo.PYFormula_express_user = username
    sampleinfo.PYFormula_update_date = today
    db.session.commit()
    return 'success', 200


@interface.route('/download_delieverupdate', methods=['POST'])
@fresh_login_required
def download_delieverupdate():
    samplelist = samplelist2deliever(request.json, SampleInfoEN2ZH)
    if 1 > len(list(samplelist.keys())):
        return 'empty', 500, {'content-type': 'application/json'}
    releasesheet = os.path.join(CONF.PYTemplate, "PYDelieverUpdate.xls")
    json_to_xls(samplelist, releasesheet)
    return 'success', 200, {'content-type': 'application/json'}


@interface.route('/uploadDelieverUpdate', methods=['POST'])
@fresh_login_required
def upload_delieverupdate():
    username = current_user.realname
    f = request.files['file']
    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)
        suffix = f.filename.split('.')[-1]
        dest_path = os.path.join(
            CONF.PYSamplesheet, "delieverupdate" + '.' + suffix)
        shutil.move(upload_path, dest_path)
        if updateDelieverSheet(dest_path, username):
            return 'success', 200
        else:
            return 'failed', 0


# ==============================================================================
# mysamples
#     /mysamplesByDefault
#     /download_salesupdate
#     /uploadSalesSheet
#     /mysampleByDetail
#     /detailsales
#     /invalidSample
#     /updateMySample
#     /createMySample
# ==============================================================================
@interface.route('/mysamples', methods=['POST', 'GET'])
@login_required
@Manager_required
def showmysamples():
    return render_template('mysamples.html')


@interface.route('/mysamplesByDefault', methods=['GET'])
@login_required
def query_mysamples_by_default():
    username = current_user.realname
    samples = query_by_manager('', '', username, '', '', '')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_applyer('', '', username, '', '', '')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/download_salesupdate', methods=['POST'])
@fresh_login_required
def download_salesupdate():
    samplelist = samplelist2sales(request.json, SampleInfoEN2ZH)
    if 1 > len(list(samplelist.keys())):
        return 'empty', 300, {'content-type': 'application/json'}
    releasesheet = os.path.join(CONF.PYTemplate, "PYSalesUpdate.xls")
    json_to_xls(samplelist, releasesheet)
    return 'success', 200, {'content-type': 'application/json'}


@interface.route('/uploadSalesSheet', methods=['POST'])
@fresh_login_required
def upload_sales_sheet():
    username = current_user.realname
    f = request.files['file']
    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)
        suffix = f.filename.split('.')[-1]
        dest_path = os.path.join(
            CONF.PYSamplesheet, "updatesalessheet" + '.' + suffix)
        shutil.move(upload_path, dest_path)
        if updateSalesSheet(dest_path, username):
            return 'success', 200
        else:
            return 'failed', 0


@interface.route('/mysampleByDetail', methods=['POST'])
@login_required
def query_mysample_by_detail():
    username = current_user.realname
    select = request.json
    status = select['Status']
    tube_id = select['Tube_ID']
    agent_contacts = select['Agent_contacts']
    time_start = select['Time_start']
    time_end = select['Time_end']

    samples = query_by_manager(
        status, tube_id, username, agent_contacts, time_start, time_end)
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_applyer(
        status, tube_id, username, agent_contacts, time_start, time_end)
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/detailsales', methods=['POST', 'GET'])
@login_required
@Manager_required
def sample_detail_sales():
    return render_template('detailsales.html')


@interface.route('/check_samples', methods=['POST', 'GET'])
@login_required
def check_samples():
    update_result_file = os.path.join(CONF.base_path, 'static', "IDS_cannot_run.txt")  # DevelopmentConfig
    if os.path.exists(update_result_file):
        with open(update_result_file,'r') as f:
            a = f.readlines()
    else:
        with open(update_result_file,'w') as f:
            f.write('')
        a = []
    a_list = [i.split('\t')[0] for i in a]
    b_list = [i.split('\t')[1] for i in a if len(i.split('\t'))>2]
    context = dict(zip(a_list, b_list))
    return render_template('check_samples.html',con = context)


@interface.route('/remove_stat/<tube_id>', methods=['POST', 'GET'])
@login_required
def remove_stat(tube_id):
    update_result_file = os.path.join(CONF.base_path, 'static', "IDS_cannot_run.txt")  # DevelopmentConfig
    print("update_result_file: {}".format(update_result_file))
    with open(update_result_file,'r') as f:
        a = f.readlines()
    b = a[:]
    for i in a:
        if tube_id in i:
            b.remove(i)
    with open(update_result_file,'w') as g:
        g.writelines(b)
    return redirect('/check_samples')


@interface.route('/invalidSample', methods=['POST'])
@fresh_login_required
def invalid_sample():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    if 'undefined' == sample['Sample_remarks']:
        return 'negative', 405
    if '' == sample['Sample_remarks']:
        return 'negative', 405

    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).filter(SampleInfo.Status < 5).first()
    if None != sampleinfo:
        sampleinfo.Status = 8
        sampleinfo.Sample_invalid_user = username
        sampleinfo.Sample_remarks = sample['Sample_remarks']
        sampleinfo.PYFormula_update_date = today
    else:
        db.session.close()
        return 'negative', 300
    db.session.commit()
    return 'success', 200


@interface.route('/updateTag', methods=['POST'])
@fresh_login_required
def update_tag():
    sample = request.json
    if 'undefined' == sample['Tag']:
        return 'negative', 405
    if '' == sample['Tag']:
        return 'negative', 405
    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).first()
    if None != sampleinfo:
        sampleinfo.Tag = sample["Tag"]
        db.session.commit()
    else:
        db.session.close()
        return 'negative', 300
    return 'success', 200


@interface.route('/updateMySample', methods=['POST'])
@fresh_login_required
def update_sample():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    change = 0
    if 'undefined' == sample['Sample_remarks']:
        return 'negative', 405
    if '' == sample['Sample_remarks']:
        return 'negative', 405

    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).filter(SampleInfo.Status < 8).first()
    if None != sampleinfo:
        if 1 < sampleinfo.Status:
            samplesave = SampleInfo(Tube_ID=sampleinfo.Tube_ID,
                                    Agent_sampleid=sampleinfo.Agent_sampleid,
                                    Agent_manager=sampleinfo.Agent_manager,
                                    Agent_contacts=sampleinfo.Agent_contacts,
                                    Project_name=sampleinfo.Project_name,
                                    PYFormula_status=sampleinfo.PYFormula_status,
                                    Report_type=sampleinfo.Report_type,
                                    Sales_items=sampleinfo.Sales_items,
                                    Sample_remarks="Update from: " +
                                    SampleInfoEN2ZH[
                                        'translate4web']['Status']['Value'][
                                        str(sampleinfo.Status)],
                                    Status=8,
                                    PYFormula_update_date=today,
                                    Sample_invalid_user=username
                                    )

        if sample['Project_name'] in SampleInfoZH2EN[
                'translate4db']['Project_name']['Value']:
            sample['Project_name'] = SampleInfoZH2EN[
                'translate4db']['Project_name']['Value'][sample['Project_name']]
        if sample['Project_name'] != sampleinfo.Project_name:
            sampleinfo.Project_name = sample['Project_name']
            change += 1
        if sample['PYFormula_status'] in SampleInfoZH2EN[
                'translate4db']['PYFormula_status']['Value']:
            sample['PYFormula_status'] = SampleInfoZH2EN[
                'translate4db']['PYFormula_status']['Value'][
                sample['PYFormula_status']]
        if sample['PYFormula_status'] != sampleinfo.PYFormula_status:
            sampleinfo.PYFormula_status = sample['PYFormula_status']
            change += 1
        if sample['Report_type'] in SampleInfoZH2EN[
                'translate4db']['Report_type']['Value']:
            sample['Report_type'] = SampleInfoZH2EN[
                'translate4db']['Report_type']['Value'][
                sample['Report_type']]
        if sample['Report_type'] != sampleinfo.Report_type:
            sampleinfo.Report_type = sample['Report_type']
            change += 1
        if sample['Sample_remarks'] != sampleinfo.Sample_remarks:
            sampleinfo.Sample_remarks = sample['Sample_remarks']
            change += 1

        if 0 < change:
            sampleinfo.PYFormula_update_date = today
            db.session.add(samplesave)

            if 3 < sampleinfo.Status:
                sampleinfo.Status = 3
                question = Questionnaire.query.filter_by(
                    Tube_ID=sampleinfo.Tube_ID).first()
                question.Questionnaire_status = 0
                sampleinfo.Questionnaire_status = 0
                ReportJSONClear(sampleinfo.Tube_ID, sampleinfo.PriSID)
                SampleReportClear(sampleinfo.Tube_ID, sampleinfo.PriSID,
                                  sampleinfo.Project_name,
                                  SampleInfoEN2ZH[
                                      'translate4web']['Project_name'][
                                      'suffix'][sampleinfo.Project_name])
        else:
            return 'nothing', 100
    else:
        db.session.close()
        return 'negative', 300
    db.session.commit()
    return 'success', 200


@interface.route('/createMySample', methods=['POST'])
@fresh_login_required
def create_sample():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    change = 0
    if 'undefined' == sample['Sample_remarks']:
        return 'negative', 400
    if '' == sample['Sample_remarks']:
        return 'negative', 400

    sampleinfo = SampleInfo.query.filter_by(
        PriSID=sample['PriSID']).filter(
        SampleInfo.Status > 2, SampleInfo.Status < 8).first()
    if None == sampleinfo:
        db.session.close()  # sample was invalided or sample is not back
        return 'negative', 300

    if sampleinfo.Project_name in SampleInfoZH2EN[
            'translate4db']['Project_name']['Value']:
        sampleinfo.Project_name = SampleInfoZH2EN[
            'translate4db']['Project_name']['Value'][sampleinfo.Project_name]
        db.session.commit()  # translate2db

    if sample['Project_name'] in SampleInfoZH2EN[
            'translate4db']['Project_name']['Value']:
        sample['Project_name'] = SampleInfoZH2EN[
            'translate4db']['Project_name']['Value'][sample['Project_name']]
    if sample['Project_name'] == sampleinfo.Project_name:
        db.session.close()
        return 'negative', 405  # report not changed

    sampleexist = SampleInfo.query.filter_by(
        Tube_ID=sampleinfo.Tube_ID,
        Project_name=sample['Project_name']).filter(
        SampleInfo.Status > 2, SampleInfo.Status < 8).first()
    if None != sampleexist:
        db.session.close()
        return 'negative', 405  # report duplicated

    if sample['PYFormula_status'] in SampleInfoZH2EN[
            'translate4db']['PYFormula_status']['Value']:
        sample['PYFormula_status'] = SampleInfoZH2EN[
            'translate4db']['PYFormula_status']['Value'][
            sample['PYFormula_status']]
    if sample['Report_type'] in SampleInfoZH2EN[
            'translate4db']['Report_type']['Value']:
        sample['Report_type'] = SampleInfoZH2EN[
            'translate4db']['Report_type']['Value'][
            sample['Report_type']]

    samplesave = SampleInfo(Tube_ID=sampleinfo.Tube_ID,
                            Sample_ID=sampleinfo.Sample_ID,
                            Agent_sampleid=sampleinfo.Agent_sampleid,
                            Agent_name=sampleinfo.Agent_name,
                            Agent_manager=sampleinfo.Agent_manager,
                            Agent_contacts=sampleinfo.Agent_contacts,
                            Agent_phone=sampleinfo.Agent_phone,
                            Agent_email=sampleinfo.Agent_email,
                            Agent_address=sampleinfo.Agent_address,
                            Status=3,
                            Sample_back_date=SampleInfo.Sample_back_date,
                            Release_apply_date=today,
                            Release_apply_user=username,
                            PYFormula_update_date=today
                            )
    samplesave.Project_name = sample['Project_name']
    samplesave.PYFormula_status = sample['PYFormula_status']
    samplesave.Report_type = sample['Report_type']
    samplesave.Sample_remarks = sample['Sample_remarks']

    db.session.add(samplesave)

    db.session.commit()
    return 'success', 200


# ==============================================================================
# agentdetail
#     /agentByPriSID
# ==============================================================================
@interface.route('/agentdetail', methods=['POST', 'GET'])
@login_required
@Manager_required
def agent_detail():
    return render_template('agentdetail.html')


@interface.route('/agentByPriSID', methods=['GET'])
@login_required
def query_agent_by_prisid():
    prisid = request.args.get('key', '')
    sampleinfo = SampleInfo.query.filter_by(PriSID=prisid).first()
    sampleinfo = sampleinfo.SampleInfo2agent()
    db.session.close()
    return json.dumps(sampleinfo), 200, {'content-type': 'application/json'}


# ==============================================================================
# sampleadmin
#     /detailadmin
#     /adminupdate
# ==============================================================================
@interface.route('/sampleadmin', methods=['POST', 'GET'])
@login_required
@Admin_required
def sample_list_admin():
    return render_template('sampleadmin.html')


@interface.route('/detailadmin', methods=['POST', 'GET'])
@login_required
@Manager_required
def sample_detail_admin():
    return render_template('detailadmin.html')


@interface.route('/adminupdate', methods=['POST', 'GET'])
# @login_required
@fresh_login_required
@Admin_required
def admin_update_manager():
    today = datetime.now()
    sampleupdate = request.json
    if 1 > len(sampleupdate['samplelist']):
        return 'negative', 100
    if '' == sampleupdate['Agent_manager']:
        return 'negative', 100
    if '' == sampleupdate['Release_apply_user']:
        return 'negative', 100

    for sample in sampleupdate['samplelist']:
        sampleinfo = SampleInfo.query.filter_by(PriSID=sample).first()
        if None == sampleinfo:
            return 'error', 500
        else:
            sampleinfo.Agent_manager = sampleupdate['Agent_manager']
            sampleinfo.Release_apply_user = sampleupdate['Release_apply_user']
            sampleinfo.PYFormula_update_date = today

    db.session.commit()
    db.session.close()
    return 'success', 200


# ==============================================================================
# reportlist
#     /reportByDefault
#     /detailreport
#     /reportByPriSID
# ==============================================================================
@interface.route('/reportlist', methods=['POST', 'GET'])
@login_required
@Consultant_required
def overview_report():
    return render_template('reportlist.html')


@interface.route('/reportByDefault', methods=['GET'])
@login_required
def query_repory_by_default():
    samples = query_by_regular(5, '', '', '', '', '')
    sample_list = {}
    line = 1
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_regular(6, '', '', '', '', '')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    samples = query_by_regular(7, '', '', '', '', '')
    for sample in samples:
        sample_list[line] = translate4web(
            sample.SampleInfo2dict(), SampleInfoEN2ZH)
        line += 1
    return json.dumps(sample_list), 200, {'content-type': 'application/json'}


@interface.route('/detailreport', methods=['POST', 'GET'])
@login_required
@Consultant_required
def sample_detail_report():
    return render_template('detailreport.html')


@interface.route('/report_again/<PriSID>', methods=['POST', 'GET'])
@login_required
@Consultant_required
def report_again(PriSID):
    sampleinfo = SampleInfo.query.filter_by(PriSID=PriSID).first()
    SampleReport(sampleinfo.Tube_ID, sampleinfo.PriSID, sampleinfo.Project_name)
    return 'success', 200


@interface.route('/reportByPriSID', methods=['POST', 'GET'])
@login_required
@Reporter_required
def query_report_by_prisid():
    prisid = request.args.get('key', '')
    sampleinfo = SampleInfo.query.filter_by(PriSID=prisid).first()
    if None == sampleinfo:
        db.session.close()
        return 'False', 500, {'content-type': 'application/json'}
    elif None == sampleinfo.Tube_ID:
        db.session.close()
        return 'Tube_ID not ready', 300, {'content-type': 'application/json'}
    elif 6 > sampleinfo.Status or 7 < sampleinfo.Status:
        db.session.close()
        return 'Status not ready', 300, {'content-type': 'application/json'}
    else:
        subfolder = str(int(sampleinfo.PriSID / 1000))
        subpath = os.path.join(CONF.PYReport, subfolder, sampleinfo.Tube_ID)

    if not os.path.exists(subpath):
        db.session.close()
        return 'Status not ready', 300, {'content-type': 'application/json'}
    else:
        pass

    if sampleinfo.Project_name in SampleInfoEN2ZH['translate4web'][
            'Project_name']['suffix']:
        suffix = SampleInfoEN2ZH['translate4web'][
            'Project_name']['suffix'][sampleinfo.Project_name]
    else:
        suffix = '.pdf'

    filename = sampleinfo.Tube_ID + suffix
    srcpath = os.path.join(subpath, filename)

    if os.path.exists(srcpath):
        samplereport = {}
        samplereport["subfolder"] = subfolder
        samplereport["tubeID"] = sampleinfo.Tube_ID
        samplereport["filename"] = filename
        db.session.close()
        return json.dumps(samplereport), 200, {'content-type': 'application/json'}
    else:
        db.session.close()
        return 'False', 500, {'content-type': 'application/json'}


@interface.route('/detailformula', methods=['POST', 'GET'])
@login_required
@Consultant_required
def sample_detail_formula():
    return render_template('detailformula.html')


@interface.route('/pyformulaByPriSID', methods=['POST', 'GET'])
# @login_required
@fresh_login_required
@Reporter_required
def formula_by_prisid():
    prisid = request.args.get('key', '')
    sampleinfo = SampleInfo.query.filter_by(PriSID=prisid).first()
    if None == sampleinfo:
        db.session.close()
        return 'False', 500, {'content-type': 'application/json'}

    formula = {}
    Others = []
    if None == sampleinfo.PYFormula_release_record:
        db.session.close()
        for key in PYFormulaType[CONF.PYFormulaVersion]['PYFormula2web'].keys():
            formula[key] = 0
        formula['PYF-Others'] = "| ".join(Others)
        return json.dumps(formula), 200, {'content-type': 'application/json'}
    else:
        pass

    for key in sampleinfo.PYFormula_release_record.split('; '):
        info = key.split(' * ')
        if len(info) > 1 and int(info[1]) > 0:
            if info[0] in PYFormulaType[CONF.PYFormulaVersion]['PYFormula2db']:
                formula[PYFormulaType[CONF.PYFormulaVersion][
                    'PYFormula2db'][info[0]]] = info[1]
        else:
            Others.append(key)
    formula['PYF-Others'] = "; ".join(Others)

    db.session.close()

    for key in PYFormulaType[CONF.PYFormulaVersion]['PYFormula2web'].keys():
        if key not in formula:
            formula[key] = 0

    return json.dumps(formula), 200, {'content-type': 'application/json'}


@interface.route('/updatePYFormula', methods=['POST', 'GET'])
# @login_required
@fresh_login_required
@Reporter_required
def update_formula():
    username = current_user.realname
    today = datetime.now()
    sample = request.json
    sampleinfo = SampleInfo.query.filter_by(PriSID=sample['PriSID']).first()
    if None == sampleinfo:
        db.session.close()
        return 'False', 500, {'content-type': 'application/json'}
    elif 7 == sampleinfo.Status:
        db.session.close()
        return 'negative', 300, {'content-type': 'application/json'}

    formula = {}
    Others = []
    for key in PYFormulaType[CONF.PYFormulaVersion]['PYFormula2web'].keys():
        if 0 != int(sample[key]):
            formula[key] = PYFormulaType[
                CONF.PYFormulaVersion]['PYFormula2web'][key] + " * " + sample[key]

    if '' != sample['PYF-Others']:
        formula['PYF-Others'] = sample['PYF-Others']
    sampleinfo.PYFormula_release_record = "; ".join(formula.values())
    sampleinfo.Report_user = username
    sampleinfo.Report_date = today
    sampleinfo.PYFormula_update_date = today
    db.session.commit()
    db.session.close()
    return 'success', 200, {'content-type': 'application/json'}


# ==============================================================================
# /questionnairedetail
#     /questionByPriSID
# ==============================================================================
@interface.route('/questdetail', methods=['POST', 'GET'])
@login_required
@Reporter_required
def show_question():
    return render_template('questiondetail.html')


@interface.route('/questByPriSID', methods=['GET'])
@login_required
def query_quest_by_prisid():
    prisid = request.args.get('key', '')
    sampleinfo = SampleInfo.query.filter_by(PriSID=prisid).first()
    if None == sampleinfo:
        db.session.close()
        return 'failed', 500, {'content-type': 'application/json'}
    elif None == sampleinfo.Tube_ID:
        db.session.close()
        return 'not ready', 300, {'content-type': 'application/json'}

    question = Questionnaire.query.filter_by(
        Tube_ID=sampleinfo.Tube_ID).first()
    if None == question:
        db.session.close()
        return 'failed', 500, {'content-type': 'application/json'}
    else:
        questionjson = translate4web(
            question.Questionnaire2dict(), QuestionnaireEN2ZH)
        db.session.close()
        return json.dumps(questionjson), 200, {'content-type': 'application/json'}


# ==============================================================================
#     /<path:filename>/report/download
#     /<path:filename>/template/download
#     /<path:PriSID>/uploadReport
# ==============================================================================
@interface.route('/<subfolder>/<tubeID>/<filename>/report/download', methods=['GET'])
# @login_required
@fresh_login_required
@Reporter_required
def download_report(subfolder, tubeID, filename):
    reportDir = os.path.join(CONF.PYReport, subfolder, tubeID)
    report = os.path.join(reportDir, filename)
    if os.path.exists(report):
        report_download = send_from_directory(
            reportDir, filename, as_attachment=False)
        return report_download
    else:
        return render_template('403.html')


@interface.route('/<path:filename>/template/download', methods=['GET'])
@login_required
def download_template(filename):
    if os.path.exists(os.path.join(CONF.PYTemplate, filename)):
        template_download = send_from_directory(
            CONF.PYTemplate, filename, as_attachment=True)
        return template_download
    else:
        return 404


@interface.route('/<path:PriSID>/uploadReport', methods=['POST'])
@fresh_login_required
@Consultant_required
def upload_report(PriSID):
    username = current_user.realname
    today = datetime.now()
    f = request.files['file']
    sampleinfo = SampleInfo.query.filter_by(PriSID=PriSID).first()
    if None == sampleinfo.Tube_ID:
        db.session.close()
        return 'Tube_ID failed', 300
    else:
        subfolder = str(int(sampleinfo.PriSID / 1000))
        filename = sampleinfo.Tube_ID

    if sampleinfo.Project_name in SampleInfoZH2EN[
            'translate4db']['Project_name']['Value']:
        sampleinfo.Project_name = SampleInfoZH2EN[
            'translate4db']['Project_name']['Value'][
            sampleinfo.Project_name]
        db.session.commit()

    if f and allowed_file(f.filename):
        upload_path = os.path.join(
            CONF.PYSamplesheet, secure_filename(f.filename))
        f.save(upload_path)

        if sampleinfo.Project_name in SampleInfoEN2ZH['translate4web'][
                'Project_name']['suffix']:
            suffix = SampleInfoEN2ZH['translate4web'][
                'Project_name']['suffix'][sampleinfo.Project_name]
        else:
            db.session.close()
            return 'failed', 0

        dest_path = os.path.join(
            CONF.PYReport, subfolder, filename, filename + suffix)
        shutil.move(upload_path, dest_path)
        sampleinfo.Status = 6
        sampleinfo.Report_date = today
        sampleinfo.Report_user = username
        sampleinfo.PYFormula_update_date = today

        if os.path.exists(dest_path):
            db.session.commit()
            db.session.close()
            return 'success', 200
        else:
            db.session.rollback()
            db.session.close()
            return 'failed', 500
    else:
        db.session.close()
        return 'failed', 0


# ==============================================================================
# 404.html
# 403.html
# ==============================================================================
@interface.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@interface.errorhandler(403)
def permisson_denied(e):
    return render_template('403.html'), 403


# ==============================================================================
# cachelist
#     /add_cachelist
#     /clear_cachelist
#     /sampleByCache
#     /delete_cachelist
# ==============================================================================
@interface.route('/cachelist', methods=['POST', 'GET'])
def showcachelist():
    return render_template('cachelist.html')


@interface.route('/add_cachelist', methods=['POST'])
def add_cachelist():
    samplelist = samplelist2json(request.json)
    cachejson = CONF.cachelist
    lists = {}
    with open(cachejson, 'r', encoding="UTF-8") as cache:
        lists = json.load(cache)
    for sample in samplelist:
        lists[sample] = samplelist[sample]
    with open(cachejson, 'w', encoding="UTF-8") as cache:
        json.dump(lists, cache)
    return 'success', 200, {'content-type': 'application/json'}


@interface.route('/clear_cachelist', methods=['POST'])
def clear_cachelist():
    cachejson = CONF.cachelist
    lists = {}
    with open(cachejson, 'w', encoding="UTF-8") as cache:
        json.dump(lists, cache)
    return 'success', 200, {'content-type': 'application/json'}


@interface.route('/sampleByCache', methods=['GET'])
def show_by_cachelist():
    cachejson = CONF.cachelist
    lists = {}
    with open(cachejson, 'r', encoding="UTF-8") as cache:
        lists = json.load(cache)
    return json.dumps(lists), 200, {'content-type': 'application/json'}


@interface.route('/delete_cachelist', methods=['POST'])
def delete_cachelist():
    samplelist = samplelist2json(request.json)
    cachejson = CONF.cachelist
    lists = {}
    with open(cachejson, 'r', encoding="UTF-8") as cache:
        lists = json.load(cache)
    for sample in samplelist:
        if sample in lists:
            lists.pop(sample)
    with open(cachejson, 'w', encoding="UTF-8") as cache:
        json.dump(lists, cache)
    return 'success', 200, {'content-type': 'application/json'}
