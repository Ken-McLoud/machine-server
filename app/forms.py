from flask_wtf import Form
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from app import models

class Cell_info_form(Form):
    cell_name = StringField('name',validators=[DataRequired()])
    cell_takt = IntegerField('takt',validators=[DataRequired()])

class Shift_info_form(Form):
    start=StringField('start',validators=[DataRequired()])
    end=StringField('end',validators=[DataRequired()])

class Break_info_form(Form):
    start=StringField('start',validators=[DataRequired()])
    end=StringField('end',validators=[DataRequired()])
    

    
    
