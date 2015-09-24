from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required,current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegisterationForm,ChangePasswordForm,ResetRequestForm,ResetPasswordForm,ChangeEmailForm
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.' + ' ')
    return render_template('auth/login.html', form=form,current_user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

# @csrf.error_handler
# def csrf_error(reason):
#     return render_template('auth/csrf_error.html',reason=reason),400

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email,'confirm the account','auth/email/confirm',user=user,token=token)
        flash('a confirm mail has been sent to by email')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('you have confirm your account.thanks!')
    else:
        flash('the confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))


@auth.before_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed \
        and request.endpoint[:5] !='auth.' and request.endpoint != 'static':
        return render_template(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,'confirm your account','auth/email/confirm',user=current_user,token=token)
    flash('a new confirm email has been sent to you by mail.')
    return redirect(url_for('main.index'))

@auth.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('you have change your passeord')
            return redirect(url_for('main.index'))
        else:
            flash('Invaild password')
    return render_template('auth/change_password.html',form=form)

#   reset password
#       chick a link -> input your email ->if exist : send mail to reset password -> chick a link -> table
#                                           else: raise error                                           |
#                                                                                                input psd -> msg:successful

@auth.route('/reset_request',methods=['POST','GET'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(form.email.data,'reset your password','auth/email/reset_password',user=user,token=token,\
                       next=request.args.get('next'))
            flash('a new confirm email has been sent to you by mail.')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html',form=form)

@auth.route('/reset_password/<token>',methods=['POST','GET'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash('you have change you password successful.')
            return redirect(url_for('auth.login'))
        else:
            flash('change you password failed')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)



#                   change email                    #
#   login-in -> change_email -> page to sure change (table submit)                                                  #
#                                ->sent mail(token) -> link chick to a page ->input new email
#                                   ->sent mail check ->update email                   #
#                                                   #

@auth.route('/change_email_request',methods=['POST','GET'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            token = current_user.generate_change_email_token(new_email=form.new_email.data)
            send_email(form.email.data,'change your email address','auth/email/change_email',token=token,user=current_user)
            flash('we have sent a mail to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html',form=form)

@auth.route('/change_email/<token>',methods=['POST','GET'])
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('you have change your email.')
    else:
        flash('Invaild request...--')
    return redirect(url_for('main.index'))


