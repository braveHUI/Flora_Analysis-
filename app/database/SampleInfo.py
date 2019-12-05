from datetime import datetime

from app import db
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import (CHAR, DATE, DATETIME, FLOAT, INTEGER,
                                       JSON, SMALLINT, TINYINT, VARCHAR, YEAR)


class SampleInfo(db.Model):
    __tablename__ = 'SampleInfo'
    PriSID = db.Column(db.INTEGER(), primary_key=True,
                       autoincrement=True, nullable=False)
    Sample_ID = db.Column(db.VARCHAR(30))
    Tube_ID = db.Column(db.VARCHAR(30))
    Project_name = db.Column(db.VARCHAR(30))
    Report_type = db.Column(db.SMALLINT)
    Report_name = db.Column(VARCHAR(20))
    Report_phone = db.Column(VARCHAR(15))
    Sales_PYID = db.Column(VARCHAR(10))
    Sales_items = db.Column(VARCHAR(30))
    Sales_record_date = db.Column(db.DATETIME)
    Status = db.Column(db.SMALLINT)
    Agent_manager = db.Column(db.VARCHAR(20))
    Agent_name = db.Column(db.VARCHAR(20))
    Agent_sampleid = db.Column(db.VARCHAR(30))
    Agent_contacts = db.Column(db.VARCHAR(20))
    Agent_phone = db.Column(db.VARCHAR(15))
    Agent_email = db.Column(db.VARCHAR(30))
    Agent_address = db.Column(db.VARCHAR(60))
    Release_apply_date = db.Column(db.DATETIME)
    Release_apply_user = db.Column(db.String(64))
    PYFormula_release_ahead = db.Column(db.VARCHAR(120))
    Tube_out_express_ID = db.Column(db.VARCHAR(15))
    Tube_expiry_date = db.Column(db.DATETIME)
    Release_date = db.Column(db.DATETIME)
    Release_user = db.Column(db.String(64))
    Sample_back_express_ID = db.Column(db.VARCHAR(25))
    Sample_back_date = db.Column(db.DATETIME)
    Sample_back_user = db.Column(db.String(64))
    Sample_status = db.Column(db.SMALLINT)
    Sample_invalid_user = db.Column(db.String(64))
    Tag = db.Column(db.String(64))
    Sample_remarks = db.Column(db.VARCHAR(30))
    Questionnaire_status = db.Column(db.SMALLINT, default=0)
    Receive_date = db.Column(db.DATETIME)
    Production_date = db.Column(db.DATETIME)
    JSON_date = db.Column(db.DATETIME)
    Report_date = db.Column(db.DATETIME)
    Report_user = db.Column(db.String(64))
    Report_print = db.Column(db.SMALLINT)
    Report_mail_date = db.Column(db.DATETIME)
    Reprot_receive_date = db.Column(db.DATETIME)
    PYFormula_first_print_date = db.Column(db.DATETIME)
    PYFormula_status = db.Column(db.SMALLINT)
    PYFormula_release_record = db.Column(db.VARCHAR(120))
    PYFormula_express_ID = db.Column(db.VARCHAR(15))
    PYFormula_express_date = db.Column(db.DATETIME)
    PYFormula_express_user = db.Column(db.String(64))
    PYFormula_receive_date = db.Column(db.DATETIME)
    PYFormula_update_date = db.Column(db.DATETIME)

    def SampleInfo2dict(self):
        data = {
            'PriSID': self.PriSID,
            'Sample_ID': self.Sample_ID,
            'Tube_ID': self.Tube_ID,
            'Project_name': self.Project_name,
            'Report_type': self.Report_type,
            'Report_name': self.Report_name,
            'Report_phone': self.Report_phone,
            'Sales_PYID': self.Sales_PYID,
            'Sales_items': self.Sales_items,
            'Sales_record_date': self.Sales_record_date,
            'Status': self.Status,
            'Agent_manager': self.Agent_manager,
            'Agent_name': self.Agent_name,
            'Agent_sampleid': self.Agent_sampleid,
            'Agent_contacts': self.Agent_contacts,
            'Agent_phone': self.Agent_phone,
            'Agent_email': self.Agent_email,
            'Agent_address': self.Agent_address,
            'Release_apply_date': self.Release_apply_date,
            'Release_apply_user': self.Release_apply_user,
            'PYFormula_release_ahead': self.PYFormula_release_ahead,
            'Tube_out_express_ID': self.Tube_out_express_ID,
            'Tube_expiry_date': self.Tube_expiry_date,
            'Release_date': self.Release_date,
            'Release_user': self.Release_user,
            'Sample_back_express_ID': self.Sample_back_express_ID,
            'Sample_back_date': self.Sample_back_date,
            'Sample_back_user': self.Sample_back_user,
            'Sample_status': self.Sample_status,
            'Sample_invalid_user': self.Sample_invalid_user,
            'Tag': self.Tag,
            'Sample_remarks': self.Sample_remarks,
            'Questionnaire_status': self.Questionnaire_status,
            'Receive_date': self.Receive_date,
            'Production_date': self.Production_date,
            'JSON_date': self.JSON_date,
            'Report_date': self.Report_date,
            'Report_user': self.Report_user,
            'Report_print': self.Report_print,
            'Report_mail_date': self.Report_mail_date,
            'Reprot_receive_date': self.Reprot_receive_date,
            'PYFormula_first_print_date': self.PYFormula_first_print_date,
            'PYFormula_status': self.PYFormula_status,
            'PYFormula_release_record': self.PYFormula_release_record,
            'PYFormula_express_ID': self.PYFormula_express_ID,
            'PYFormula_express_date': self.PYFormula_express_date,
            'PYFormula_express_user': self.PYFormula_express_user,
            'PYFormula_receive_date': self.PYFormula_receive_date,
            'PYFormula_update_date': self.PYFormula_update_date
        }
        if None != data['Sales_record_date']:
            data['Sales_record_date'] = \
                data['Sales_record_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Release_apply_date']:
            data['Release_apply_date'] = \
                data['Release_apply_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Tube_expiry_date']:
            if data['Tube_expiry_date'] == "0000-00-00 00:00:00":
                data['Tube_expiry_date'] = "9999-01-01 00:00:00"
            else:
                data['Tube_expiry_date'] = \
                    data['Tube_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Release_date']:
            data['Release_date'] = \
                 data['Release_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Sample_back_date']:
            data['Sample_back_date'] = \
                data['Sample_back_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Receive_date']:
            data['Receive_date'] = \
                data['Receive_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Production_date']:
            data['Production_date'] = \
                data['Production_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['JSON_date']:
            data['JSON_date'] = \
                data['JSON_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Report_date']:
            data['Report_date'] = \
                data['Report_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Report_mail_date']:
            data['Report_mail_date'] = \
                data['Report_mail_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Reprot_receive_date']:
            data['Reprot_receive_date'] = \
                data['Reprot_receive_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['PYFormula_first_print_date']:
            data['PYFormula_first_print_date'] = \
                data['PYFormula_first_print_date'].strftime(
                    "%Y-%m-%d %H:%M:%S")
        if None != data['PYFormula_express_date']:
            data['PYFormula_express_date'] = \
                data['PYFormula_express_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['PYFormula_receive_date']:
            data['PYFormula_receive_date'] = \
                data['PYFormula_receive_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['PYFormula_update_date']:
            data['PYFormula_update_date'] = \
                data['PYFormula_update_date'].strftime("%Y-%m-%d %H:%M:%S")
        return data

    def SampleInfo2insert(self, data):
        if 'Project_name' in data:
            self.Project_name = data['Project_name']
        if 'Agent_name' in data:
            self.Agent_name = data['Agent_name']
        if 'Agent_manager' in data:
            self.Agent_manager = data['Agent_manager']
        if 'Agent_sampleid' in data:
            self.Agent_sampleid = data['Agent_sampleid']
        if 'Release_apply_date' in data:
            self.Release_apply_date = data['Release_apply_date']
        if 'Agent_contacts' in data:
            self.Agent_contacts = data['Agent_contacts']
        if 'Agent_phone' in data:
            self.Agent_phone = str(data['Agent_phone'])
        if 'Agent_email' in data:
            self.Agent_email = data['Agent_email']
        if 'Agent_address' in data:
            self.Agent_address = data['Agent_address']
        if 'Report_name' in data:
            self.Report_name = data['Report_name']
        if 'Report_type' in data:
            self.Report_type = data['Report_type']
        if 'PYFormula_status' in data:
            self.PYFormula_status = data['PYFormula_status']
        if 'PYFormula_release_ahead' in data:
            self.PYFormula_release_ahead = data['PYFormula_release_ahead']
        self.PYFormula_update_date = datetime.now()
        self.Status = 1

    def insert_name(self,data):
        if 'Name' in data:
            self.Report_name = data['Name']
            
    def SampleInfo2Questionnaire(self):
        data = {
            'Tube_ID': self.Tube_ID,
            'Status': self.Status,
            'Agent_manager': self.Agent_manager
        }
        if None != self.Sample_ID:
            data['Sample_ID'] = self.Sample_ID
        return data

    def SampleInfo2reportJSON(self):
        data = {
            'Tube_ID': self.Tube_ID,
            'Sample_ID': self.Sample_ID,
            'Sample_back_date': self.Sample_back_date,
            'Detection_date': self.Production_date,
            'Agent_name': self.Agent_name,
            'Agent_sampleid': self.Agent_sampleid,
            'Report_name': self.Report_name,
            'Report_date': self.Report_date,
            'Phone': self.Report_phone,
            'Remarks': self.Sample_remarks,
            'Status': self.Status
        }
        if None != data['Sample_back_date']:
            data['Sample_back_date'] = \
                data['Sample_back_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Detection_date']:
            data['Detection_date'] = \
                data['Detection_date'].strftime("%Y-%m-%d %H:%M:%S")
        if None != data['Report_date']:
            data['Report_date'] = \
                data['Report_date'].strftime("%Y-%m-%d %H:%M:%S")
        return data

    def SampleInfo2agent(self):
        data = {
            'PriSID': self.PriSID,
            'Tube_ID': self.Tube_ID,
            'Agent_manager': self.Agent_manager,
            'Agent_sampleid': self.Agent_sampleid,
            'Agent_name': self.Agent_name,
            'Agent_contacts': self.Agent_contacts,
            'Agent_phone': self.Agent_phone,
            'Agent_email': self.Agent_email,
            'Agent_address': self.Agent_address
        }
        return data

    def SampleInfo2release(self):
        data = {
            'PriSID': self.PriSID,
            'Tube_ID': self.Tube_ID,
            'Tube_expiry_date': self.Tube_expiry_date,
            'Tube_out_express_ID': self.Tube_out_express_ID,
            'PYFormula_status': self.PYFormula_status,
            'PYFormula_release_ahead': self.PYFormula_release_ahead,
            'Project_name': self.Project_name,
            'Agent_name': self.Agent_name,
            'Agent_manager': self.Agent_manager,
            'Agent_sampleid': self.Agent_sampleid,
            'Agent_contacts': self.Agent_contacts,
            'Agent_phone': self.Agent_phone,
            'Agent_address': self.Agent_address,
        }
        if None != data['Tube_expiry_date']:
            data['Tube_expiry_date'] = \
                data['Tube_expiry_date'].strftime("%Y-%m-%d %H:%M:%S")
        return data

    def SampleInfo2deliever(self):
        data = {
            'PriSID': self.PriSID,
            'Tube_ID': self.Tube_ID,
            'PYFormula_express_ID': self.PYFormula_express_ID,
            'PYFormula_status': self.PYFormula_status,
            'PYFormula_release_record': self.PYFormula_release_record,
            'Report_type': self.Report_type,
            'Report_date': self.Report_date,
            'Agent_manager': self.Agent_manager,
            'Agent_contacts': self.Agent_contacts,
            'Agent_phone': self.Agent_phone,
            'Agent_address': self.Agent_address,
        }
        if None != data['Report_date']:
            data['Report_date'] = \
                data['Report_date'].strftime("%Y-%m-%d %H:%M:%S")
        return data

    def SampleInfo2sales(self):
        data = {
            'PriSID': self.PriSID,
            'Sales_PYID': self.Sales_PYID,
            'Sales_record_date': self.Sales_record_date,
            'Tube_ID': self.Tube_ID,
            'Sales_items': self.Sales_items,
            'Report_name': self.Report_name,
            'Report_phone': self.Report_phone
        }
        if None != data['Sales_record_date']:
            data['Sales_record_date'] = \
                data['Sales_record_date'].strftime("%Y-%m-%d")
        return data

    def __repr__(self):
        return "<SampleInfo %r>" % self.__tablename__
