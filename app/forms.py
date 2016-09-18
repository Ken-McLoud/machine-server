from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from app import models

class SettingsForm(Form):
    machs=models.machines.query.all()
    mach_fields=[]
    for mach in machs:
        this_machine=[]
        this_machine.append(StringField(mach.name,validators=[DataRequired()]))
        this_machine.append(StringField(mach.ident,validators=[DataRequired()]))
        #this_machine.append(StringField(mach.ignore,validators=[DataRequired()]))
        this_machine.append(BooleanField('remove',default=False))
        mach_fields.append(this_machine)
    
    
