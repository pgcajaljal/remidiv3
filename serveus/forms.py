#from flask.ext.wtf import Form, TextField, PasswordField
#from flask.ext.wtf import Form
from flask_wtf import Form
from wtforms import TextField, PasswordField
#from flask.ext.wtf import Required
from wtforms.validators import Required

class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    
class RecoveryForm(Form):
    username = TextField('username', validators = [Required()])
    
class ChangePassForm(Form):
    oldpassword = TextField('password', validators = [Required()])
    newpassword = TextField('password')
    confirmpassword = TextField('password')