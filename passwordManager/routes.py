import base64
import hashlib
from flask import render_template, redirect, url_for, flash, request, session
import requests
from passwordManager import app
from passwordManager.models import Item, User, VM
from passwordManager.forms import VMForm # RegisterForm, LoginForm,
from passwordManager import db
from passwordManager import f
from flask_login import login_user, logout_user, login_required
import secrets
import os

OktaDomain = os.getenv("OktaDomain")
clientId = os.getenv("clientId")
clientSecret = os.getenv("clientSecret")

config = {
    "auth_uri": f"https://{OktaDomain}/oauth2/default/v1/authorize",
    "client_id": f"{clientId}",
    "client_secret": f"{clientSecret}",
    "redirect_uri": "http://localhost:5000/authorization-code/callback",
    "issuer": f"https://{OktaDomain}/oauth2/default",
    "token_uri": f"https://{OktaDomain}/oauth2/default/v1/token",
    "userinfo_uri": f"https://{OktaDomain}/oauth2/default/v1/userinfo",
}

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)

# soft delete to integrate with okta esso.
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    # form = RegisterForm()
    # if form.validate_on_submit():
    #     user_to_create = User(username=form.username.data,
    #                           email_address=form.email_address.data,
    #                           password=form.password1.data)
    #     db.session.add(user_to_create)
    #     db.session.commit()
    #     login_user(user_to_create)
    #     flash(f'Successfully create new user.! You are logged in as: {user_to_create.username}', category='success')
    #     return redirect(url_for('home_page'))
    # if form.errors != {}: #If there are not errors from the validations
    #     for err_msg in form.errors.values():
    #         flash(f'There was an error with creating a user: {err_msg}', category='danger')

    # return render_template('register.html', form=form)
    flash(f'User registration page moved to SSO Okta portal. Please work with Okta Admin.', category='info')
    return redirect(url_for("home_page"))




# @app.route('/login', methods=['GET', 'POST'])
# def login_page():
#     form = LoginForm()
#     if form.validate_on_submit():
#         attempted_user = User.query.filter_by(username=form.username.data).first()
#         if attempted_user and attempted_user.check_password_correction(
#                 attempted_password=form.password.data
#         ):
#             login_user(attempted_user)
#             flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
#             return redirect(url_for('home_page'))
#         else:
#             flash('Username and password are not match! Please try again', category='danger')
#     return render_template('login.html', form=form)


@app.route("/login")
def login_page():
    # store app state and code verifier in session
    session['app_state'] = secrets.token_urlsafe(64)
    session['code_verifier'] = secrets.token_urlsafe(64)

    # calculate code challenge
    hashed = hashlib.sha256(session['code_verifier'].encode('ascii')).digest()
    encoded = base64.urlsafe_b64encode(hashed)
    code_challenge = encoded.decode('ascii').strip('=')

    # get request params
    query_params = {'client_id': config["client_id"],
                    'redirect_uri': config["redirect_uri"],
                    'scope': "openid email profile",
                    'state': session['app_state'],
                    'code_challenge': code_challenge,
                    'code_challenge_method': 'S256',
                    'response_type': 'code',
                    'response_mode': 'query'}

    # build request_uri
    request_uri = "{base_url}?{query_params}".format(
        base_url=config["auth_uri"],
        query_params=requests.compat.urlencode(query_params)
    )

    return redirect(request_uri)

@app.route("/authorization-code/callback")
def callback():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    code = request.args.get("code")
    app_state = request.args.get("state")
    if app_state != session['app_state']:
        return "The app state does not match"
    if not code:
            return "The code was not returned or is not accessible", 403
    query_params = {'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': request.base_url,
                    'code_verifier': session['code_verifier'],
                    }
    query_params = requests.compat.urlencode(query_params)
    exchange = requests.post(
        config["token_uri"],
        headers=headers,
        data=query_params,
        auth=(config["client_id"], config["client_secret"]),
    ).json()

    # Get tokens and validate
    if not exchange.get("token_type"):
            return "Unsupported token type. Should be 'Bearer'.", 403
    access_token = exchange["access_token"]
    id_token = exchange["id_token"]

    # Authorization flow successful, get userinfo and login user
    userinfo_response = requests.get(config["userinfo_uri"],
                                    headers={'Authorization': f'Bearer {access_token}'}).json()
    print("userinfo_response")
    print(userinfo_response.keys())
    print(userinfo_response.values())
    unique_id = userinfo_response["sub"]
    user_email = userinfo_response["email"]
    user_name = userinfo_response["given_name"]

    user = User(
        id_=unique_id, name=user_name, email=user_email
    )

    if not User.get(unique_id):
            User.create(unique_id, user_name, user_email)

    login_user(user)

    flash(f'Success! You are logged in as: {user.name}', category='success')
    return redirect(url_for('home_page'))


@app.route('/logout', methods=['GET'])
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/vm')
@login_required
def vm_page():
    vms = VM.query.limit(100).all()
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
        vm_to_create = VM(hostip=form.hostip.data, username=form.username.data, password=form.password1.data)
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
