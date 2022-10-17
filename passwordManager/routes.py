from passwordManager import app
from flask import render_template, redirect, url_for, flash
from passwordManager.models import Item, User, VM
from passwordManager.forms import RegisterForm, LoginForm, VMForm
from passwordManager import db

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('market_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/vm')
def vm_page():
    vms = VM.query.all()
    return render_template('vm.html', vms=vms)

@app.route('/VMadd', methods=['GET', 'POST'])
def vmadd_page():
    form = VMForm()

    if form.validate_on_submit():
        vm_to_create = VM(hostip=form.hostip.data,
                              username=form.username.data,
                              password=form.password1.data)
        db.session.add(vm_to_create)
        db.session.commit()
        return redirect(url_for('vm_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('vmadd.html', form=form)