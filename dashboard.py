#region Imports
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.datastructures import ImmutableMultiDict
from flask_login import login_required, current_user
from datetime import datetime
from PIL import Image

import mysql.connector
import secrets
import calendar as cal
import store
import os

dashboard = Blueprint('dashboard', __name__)

from application import db, app
from models import UpdateUserInfo

#endregion

#region Database

def connect():
    _db = mysql.connector.connect(user=store.user, password=store.password,
                                  host=store.hostname,
                                  database='newschema')
    return _db

def query_db(query):
    _db = connect()
    data = pd.read_sql(query + "\nLimit 1000", _db)
    _db.close()
    return data

def alter_db(query):
    _db = connect()
    _cursor = _db.cursor()
    _cursor.execute(query)
    _cursor.close()
    _db.commit()
    _db.close()

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # resize img
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@dashboard.route('/dashboard/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UpdateUserInfo()
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            current_user.image = picture_name

        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('dashboard.settings'))

    return render_template('dashboard/settings.html', form=form)

@dashboard.route('/dashboard/calendar')
@login_required
def calendar():
    return render_template('dashboard/calendar.html')


@dashboard.route('/404')
def not_found():
    return render_template('404.html')

#endregion