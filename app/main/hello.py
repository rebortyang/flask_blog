#-*-coding:utf-8-*-
__author__ = 'yangjiebin'

from flask import Flask
from flask.ext.script import Manager,Shell
from flask import render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask import session,redirect,url_for,flash
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.migrate import Migrate,MigrateCommand
from flask.ext.mail import Mail,Message
from threading import Thread

template_folder = '../templates'
baseidr = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,template_folder=template_folder)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseidr,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWM'] = True

app.config['MAIL_SERVER'] = 'smtp.sohu.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky admin op1616op@sohu.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)


#路由和view
@app.route('/',methods=['GET','POST'])
def index():
    form = NameForms()   #form handle
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'],'NEW USER','mail/new_user',user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        # old_name = session.get('name')     #flash
        # if old_name is not None and old_name != form.name.data:
        #     flash('you have change the name!',category='message')
        # session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'),known=session.get('known',False))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    render_template('500.html'),500

#  form
class NameForms(Form):

    name = StringField('what is your name?',validators=[Required()])
    submit = SubmitField('Submit')

# model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True,index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role)

# mail
def send_async_email(app,msg):

    with app.app_context(app,msg):
        mail.send(msg)

def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template + '.html',**kwargs)
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return thr

# add data to shell
manager.add_command("shell",Shell( make_context=make_shell_context ))
# migrate
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':

    manager.run()