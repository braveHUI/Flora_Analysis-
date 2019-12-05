from datetime import datetime

from app import db
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import (CHAR, DATE, DATETIME, FLOAT, INTEGER,
                                       JSON, SMALLINT, TINYINT, VARCHAR, YEAR)


class Questionnaire(db.Model):
    __tablename__ = 'Questionnaire'
    Tube_ID = db.Column(db.VARCHAR(30), primary_key=True, nullable=False)
    Sample_ID = db.Column(db.VARCHAR(30))
    Living_city = db.Column(db.VARCHAR(20))
    Gender = db.Column(db.SMALLINT())
    Age = db.Column(db.FLOAT())
    Height = db.Column(db.FLOAT())
    Weight = db.Column(db.FLOAT())
    Sampling_date = db.Column(db.DATETIME())
    Questionnaire_date = db.Column(db.DATETIME())
    Questionnaire_status = db.Column(db.SMALLINT(), default=0)
    Stool_shape = db.Column(db.SMALLINT())
    Defecation_pattern = db.Column(db.SMALLINT())
    Defecation_regular = db.Column(db.SMALLINT())
    Defecation_period = db.Column(db.SMALLINT())
    Alcohol = db.Column(db.SMALLINT())
    Smoking = db.Column(db.SMALLINT())
    Meat_product = db.Column(db.SMALLINT())
    Fresh_vegetables = db.Column(db.SMALLINT())
    Dietary_preference = db.Column(db.SMALLINT())
    Dietary_preference_text = db.Column(db.VARCHAR(30))
    Past_medical_history = db.Column(db.VARCHAR(60))
    Family_history = db.Column(db.VARCHAR(40))
    Subhealth_state = db.Column(db.SMALLINT())
    Subhealth_state_text = db.Column(db.VARCHAR(200))
    Breakfasts_weekly = db.Column(db.SMALLINT())
    Supper_weekly = db.Column(db.SMALLINT())
    Water_daily = db.Column(db.SMALLINT())
    Drinks_preference = db.Column(db.VARCHAR(20))
    Sleeping_time = db.Column(db.SMALLINT())
    Insomnia_pattern = db.Column(db.SMALLINT())
    Nap_pattern = db.Column(db.SMALLINT())
    Fasting_blood_glucose = db.Column(db.FLOAT())
    Medicine = db.Column(db.VARCHAR(40))
    Health_product = db.Column(db.VARCHAR(40))
    Triglyceride = db.Column(db.FLOAT())
    Total_cholesterol = db.Column(db.FLOAT())
    High_density_lipoprotein = db.Column(db.FLOAT())
    Low_density_lipoprotein = db.Column(db.FLOAT())
    Way_of_birth = db.Column(db.SMALLINT())
    Breastfeeding = db.Column(db.SMALLINT())
    Medical_examination = db.Column(db.SMALLINT())
    Spend_on_MH = db.Column(db.SMALLINT())
    Remarks = db.Column(db.VARCHAR(30))
    BMI = db.Column(db.FLOAT())
    Status = db.Column(db.SMALLINT(), default=2)

    def Questionnaire2dict(self):
        data = {
            'Sample_ID': self.Sample_ID,
            'Tube_ID': self.Tube_ID,
            'Living_city': self.Living_city,
            'Gender': self.Gender,
            'Age': self.Age,
            'Height': self.Height,
            'Weight': self.Weight,
            'Sampling_date': self.Sampling_date,
            'Questionnaire_date': self.Questionnaire_date,
            'Questionnaire_status': self.Questionnaire_status,
            'Stool_shape': self.Stool_shape,
            'Defecation_pattern': self.Defecation_pattern,
            'Defecation_regular': self.Defecation_regular,
            'Defecation_period': self.Defecation_period,
            'Alcohol': self.Alcohol,
            'Smoking': self.Smoking,
            'Meat_product': self.Meat_product,
            'Fresh_vegetables': self.Fresh_vegetables,
            'Dietary_preference': self.Dietary_preference,
            'Dietary_preference_text': self.Dietary_preference_text,
            'Past_medical_history': self.Past_medical_history,
            'Family_history': self.Family_history,
            'Subhealth_state_text': self.Subhealth_state_text,
            'Breakfasts_weekly': self.Breakfasts_weekly,
            'Supper_weekly': self.Supper_weekly,
            'Water_daily': self.Water_daily,
            'Drinks_preference': self.Drinks_preference,
            'Sleeping_time': self.Sleeping_time,
            'Insomnia_pattern': self.Insomnia_pattern,
            'Nap_pattern': self.Nap_pattern,
            'Fasting_blood_glucose': self.Fasting_blood_glucose,
            'Medicine': self.Medicine,
            'Health_product': self.Health_product,
            'Triglyceride': self.Triglyceride,
            'Total_cholesterol': self.Total_cholesterol,
            'High_density_lipoprotein': self.High_density_lipoprotein,
            'Low_density_lipoprotein': self.Low_density_lipoprotein,
            'Way_of_birth': self.Way_of_birth,
            'Breastfeeding': self.Breastfeeding,
            'Medical_examination': self.Medical_examination,
            'Spend_on_MH': self.Spend_on_MH,
            'Remarks': self.Remarks,
            'BMI': self.BMI,
            'Status': self.Status
        }
        if None != data['Sampling_date']:
            data['Sampling_date'] = data['Sampling_date'].strftime(
                "%Y-%m-%d %H:%M:%S")
        if None != data['Questionnaire_date']:
            data['Questionnaire_date'] = data['Questionnaire_date'].strftime(
                "%Y-%m-%d %H:%M:%S")
        return data

    def Questionnaire2insert(self, data):
        if 'Tube_ID' in data:
            self.Tube_ID = data['Tube_ID']
        if 'Sample_ID' in data:
            self.Sample_ID = data['Sample_ID']

    def Questionnaire2update(self, data):
        if 'Sample_ID' in data:
            self.Sample_ID = data['Sample_ID']
        if 'Living_city' in data:
            self.Living_city = data['Living_city']
        if 'Gender' in data:
            self.Gender = data['Gender']
        if 'Age' in data:
            self.Age = data['Age']
        if 'Height' in data:
            self.Height = data['Height']
        if 'Weight' in data:
            self.Weight = data['Weight']
        if 'Sampling_date' in data:
            self.Sampling_date = data['Sampling_date']
        if 'Questionnaire_date' in data:
            self.Questionnaire_date = data['Questionnaire_date']
        if 'Stool_shape' in data:
            self.Stool_shape = data['Stool_shape']
        if 'Defecation_pattern' in data:
            self.Defecation_pattern = data['Defecation_pattern']
        if 'Defecation_regular' in data:
            self.Defecation_regular = data['Defecation_regular']
        if 'Defecation_period' in data and data['Defecation_period'] != '':
            self.Defecation_period = data['Defecation_period']
        if 'Alcohol' in data:
            self.Alcohol = data['Alcohol']
        if 'Smoking' in data:
            self.Smoking = data['Smoking']
        if 'Meat_product' in data:
            self.Meat_product = data['Meat_product']
        if 'Fresh_vegetables' in data:
            self.Fresh_vegetables = data['Fresh_vegetables']
        if 'Dietary_preference' in data:
            self.Dietary_preference = data['Dietary_preference']
        if 'Dietary_preference_text' in data:
            self.Dietary_preference_text = data['Dietary_preference_text']
        if 'Past_medical_history' in data:
            self.Past_medical_history = data['Past_medical_history']
        if 'Family_history' in data:
            self.Family_history = data['Family_history']
        if 'Subhealth_state_text' in data:
            self.Subhealth_state_text = data['Subhealth_state_text']
        if 'Breakfasts_weekly' in data:
            self.Breakfasts_weekly = data['Breakfasts_weekly']
        if 'Supper_weekly' in data:
            self.Supper_weekly = data['Supper_weekly']
        if 'Water_daily' in data:
            self.Water_daily = data['Water_daily']
        if 'Drinks_preference' in data:
            self.Drinks_preference = data['Drinks_preference']
        if 'Sleeping_time' in data:
            self.Sleeping_time = data['Sleeping_time']
        if 'Insomnia_pattern' in data:
            self.Insomnia_pattern = data['Insomnia_pattern']
        if 'Nap_pattern' in data:
            self.Nap_pattern = data['Nap_pattern']
        if 'Fasting_blood_glucose' in data and data['Fasting_blood_glucose'] != '':
            self.Fasting_blood_glucose = data['Fasting_blood_glucose']
        if 'Medicine' in data:
            self.Medicine = data['Medicine']
        if 'Health_product' in data:
            self.Health_product = data['Health_product']
        if 'Triglyceride' in data and data['Triglyceride'] != '':
            self.Triglyceride = data['Triglyceride']
        if 'Total_cholesterol' in data and data['Total_cholesterol'] != '':
            self.Total_cholesterol = data['Total_cholesterol']
        if 'High_density_lipoprotein' in data and data['High_density_lipoprotein'] != '':
            self.High_density_lipoprotein = data['High_density_lipoprotein']
        if 'Low_density_lipoprotein' in data and data['Low_density_lipoprotein'] != '':
            self.Low_density_lipoprotein = data['Low_density_lipoprotein']
        if 'Way_of_birth' in data:
            self.Way_of_birth = data['Way_of_birth']
        if 'Breastfeeding' in data:
            self.Breastfeeding = data['Breastfeeding']
        if 'Medical_examination' in data:
            self.Medical_examination = data['Medical_examination']
        if 'Spend_on_MH' in data:
            self.Spend_on_MH = data['Spend_on_MH']
        if 'Remarks' in data:
            self.Remarks = data['Remarks']
        if 'BMI' in data:
            self.BMI = data['BMI']

        if 'Status' in data:
            # self.Status = data['Status']
            pass
        else:
            self.Status = 2
        if 0 == self.Questionnaire_status:
            self.Questionnaire_status = 1

    def __repr__(self):
        return "<Questionnaire %r>" % self.__tablename__
