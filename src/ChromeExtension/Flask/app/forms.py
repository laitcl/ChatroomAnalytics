from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class information_form(FlaskForm):
    channelname = StringField('Channel Name', validators=[DataRequired()])
    submit = SubmitField('Submit')
