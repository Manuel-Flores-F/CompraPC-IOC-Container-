from wtforms import Form
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Required
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, RadioField, SelectField, FieldList, SubmitField

class pc_form(FlaskForm):
	radio_group_memory = RadioField('Memoria', choices=[('mem_op1','4GB'),('mem_op2','8GB'),('mem_op3','16GB')])
	radio_group_disk = RadioField('Disco', choices=[('disk_op1','HDD'),('disk_op2','SDD')])
	radio_group_video = RadioField('Video', choices=[('disk_op1','Integrada'),('video_op2','Dedicada')])
	submit = SubmitField('Calcular')

