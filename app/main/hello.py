#-*-coding:utf-8-*-
__author__ = 'yangjiebin'

from flask import Flask
from flask.ext.script import Manager
from flask import render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask import session,redirect,url_for,flash


template_folder = '../templates'

app = Flask(__name__,template_folder=template_folder)
app.config['SECRET_KEY'] = 'hard to guess string'
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

#路由和view
@app.route('/',methods=['GET','POST'])
def index():
    form = NameForms()   #form handle
    if form.validate_on_submit():
        old_name = session.get('name')     #flash
        if old_name is not None and old_name != form.name.data:
            flash('you have change the name!',category='message')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html',current_time=datetime.utcnow(),form=form,name=session.get('name'))

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



if __name__ == '__main__':
    #app.run(debug=True)
    manager.run()