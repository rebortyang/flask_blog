__author__ = 'yangjiebin'
from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,EqualTo,Regexp
from wtforms import ValidationError
from ..models import User
from flask.ext.login import current_user

class LoginForm(Form):

    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log in')



class RegisterationForm(Form):

    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    username = StringField('Username',validators=[Required(),Length(1,64),
                                                  Regexp('^[A-Za-z][A-Za-z0-9._]*$',0,'usernamess must have the only letters')])
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='password must match')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self,filed):
        if User.query.filter_by(email=filed.data).first():
            raise ValidationError(message='Email already registered.')

    def validate_username(self,filed):
        if User.query.filter_by(username=filed.data).first():
            raise ValidationError(message='username already in use.')

class ChangePasswordForm(Form):

    old_password = PasswordField('old password',validators=[Required()])
    new_password = PasswordField('new password',validators=[Required(),EqualTo('password2',message='password2 is not match newPwd')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Change password')
