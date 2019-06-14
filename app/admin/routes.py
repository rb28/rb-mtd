from flask import flash, render_template, redirect, request, url_for
from werkzeug.urls import url_parse
from flask_login import current_user, login_required
from app import db
from app.admin.forms import Org
from app.admin import bp
from app.models import User, Organisation




def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)


# Department Views


