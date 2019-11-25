from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import User
from src import db



admin_blueprint = Blueprint('admin', __name__, template_folder='../../templates/admin')


# @admin_blueprint.route('/', methods=['GET'])
# @login_required
# def root():
#     pass

# @admin_blueprint.route('/dashboard', methods=['GET'])
# @login_required
# def dashboard():
#     pass