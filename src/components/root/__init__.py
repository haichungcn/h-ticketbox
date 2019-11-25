from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy import desc
from src.models import *
from src import db
from datetime import datetime


root_blueprint = Blueprint('root', __name__, template_folder='../../templates/root')


@root_blueprint.route('/', methods=['GET'])
def root():
    return redirect(url_for('root.home'))


@root_blueprint.route('/home', methods=['GET', 'POST'])
def home():
    current_datetime = datetime.now()
    events = Event.query.filter(Event.end_date > current_datetime).order_by(desc(Event.timestamp)).all()
    categories = Category.query.all()
    print('hellloooooooooooo', request.args.get('filter'))
    for category in categories:
        if request.args.get('filter') == category.name:
            events = category.events
            events = sorted(category.events, key = lambda i : i.timestamp, reverse = True)

    return render_template('index.html', events=events, categories=categories)