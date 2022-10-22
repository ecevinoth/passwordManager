from flask import render_template, redirect, url_for, flash, request
from passwordManager import app
from passwordManager.models import Item, User, VM
from passwordManager.forms import RegisterForm, LoginForm, VMForm
from passwordManager import db
from passwordManager import f
from flask_login import login_user, logout_user, login_required

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
@login_required
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
        login_user(user_to_create)
        flash(f'Successfully create new user.! You are logged in as: {user_to_create.username}', category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/vm')
@login_required
def vm_page():
    vms = VM.query.all()
    for vm in vms:
        vm.password_dec=vm.password_decryption(password_enc=vm.password_hash).decode("utf8")
    return render_template('asset_manage.html', vms=vms)

@app.route('/vm_search')
@login_required
def vm_search():
    return render_template('asset_search.html')

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

@app.route('/api/data')
def data():
    query = VM.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            VM.hostip.like(f'%{search}%'),
            VM.username.like(f'%{search}%')
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['id', 'hostip', 'username']:
            col_name = 'id'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(VM, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [vm.to_dict() for vm in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': VM.query.count(),
        'draw': request.args.get('draw', type=int),
    }
