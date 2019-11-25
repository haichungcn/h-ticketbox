from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import *
from src import db



event_blueprint = Blueprint('event', __name__, template_folder='../../templates/event')

@event_blueprint.route('/createevent', methods=['GET', 'POST'])
@login_required
def create_event():
    origin=request.args.get('origin')
    if not origin:
        origin='/'
    categories = Category.query.all()
    organizers = Organizer.query.all()
    if request.method == 'POST':
        event = Event()
        name = request.form['name']
        event.check_event(name)
        if event.id:
            flash(f"There's already an event named {name}", "danger")
            return redirect(url_for('event.create_event'))
        org = Organizer(name = request.form['organizer']).check_org()
        if not org:
            flash(f"There's no organizer named {org.name}, please create one by clicking on the '+' button", "warning")
            return redirect(url_for('event.create_event'))
        new_event = Event(
            name = name,
            location = request.form['location']
        )
        new_event.start_date = datetime.strptime(request.form['starting_date'], "%d %B %Y - %H:%M %p")
        new_event.end_date = datetime.strptime(request.form['ending_date'], "%d %B %Y - %H:%M %p")
        category = Category.query.filter_by(name = request.form['category']).first()
        db.session.add(new_event)
        category.events.append(new_event)
        org.events.append(new_event)
        db.session.commit()

        flash(f"successfully created event named {new_event.name}", "success")
        print('success created even', new_event.name, new_event.location, new_event.start_date, new_event.end_date, new_event.organizer_id)
        return redirect(url_for("event.create_event_ticket", id=new_event.id, origin=origin))
    return render_template('createevent.html', categories=categories, organizers=organizers,  origin=origin)

@event_blueprint.route('/createorganizer', methods=['GET', 'POST'])
@login_required
def create_organizer():
    origin=request.args.get('origin')
    if not origin:
        origin='/'
    if request.method =='POST':
        org = Organizer(name = request.form['name']).check_org()
        if org:
            flash(f"There's already an organizer named {org.name}, please choose a different name", "warning")
            return redirect(url_for('event.create_organizer'))
        new_org = Organizer(name = request.form['name'], description = request.form['description'], avatar_url = request.form['avatar_url'])
        db.session.add(new_org)
        db.session.commit()
        flash(f"successfully created organizer: {new_org.name}", "success")
        return redirect(f'/event/{origin}')
    return render_template('createorganizer.html', origin=origin)

@event_blueprint.route('/<id>/createticket', methods=['GET', 'POST'])
@login_required
def create_event_ticket(id):
    origin=request.args.get('origin')
    if not origin:
        origin='/'
    if request.method == 'POST':
        if request.form['name']:
            event = Event.query.get(id)
            if not event:
                flash(f"There's no event with id #{id}", "danger")
                return redirect(url_for('event.create_event', origin = origin))
            new_tickettype = Tickettype(
                name = request.form['name'],
                price = request.form['price'],
                stock = request.form['stock'],
                benefits = request.form['benefits']
            )
            db.session.add(new_tickettype)
            event.tickettypes.append(new_tickettype)
            db.session.commit()
            flash(f"successfully created a ticket type {new_tickettype.name} for event {event.name}", "success")
        else:
            return redirect(url_for('event.create_event_article', id=event.id, origin=origin))
    return render_template('createtickettype.html', id=id, origin=origin)

@event_blueprint.route('/<id>/createarticle', methods=['GET', 'POST'])
@login_required
def create_event_article(id):
    origin=request.args.get('origin')
    if not origin:
        origin='/'
    if request.method == 'POST':
        event = Event.query.get(id)
        if not event:
            flash(f"There's no event with id #{id}", "danger")
            return redirect(url_for('event.create_event', origin = origin))
        new_article = Article(
            title = request.form['title'],
            body = request.form['body']
        )
        db.session.add(new_article)
        event.articles.append(new_article)
        db.session.commit()
        flash(f"successfully created article for event {event.name}", "success")
        return redirect(origin)
    return render_template('createarticle.html', id=id, origin=origin)

@event_blueprint.route('/<id>/addimages', methods=['GET', 'POST'])
@login_required
def add_images(id):
    origin=request.args.get('origin')
    if not origin:
        origin='/'
    if request.method == 'POST':
        event = Event.query.get(id)
        if not event:
            flash("Event ID is invalid", "danger")
            return redirect(url_for("root.home"))
        for i in range(5):
            print('sdfsdfsdfsd', request.form[f"name{i+1}"])
            if request.form[f"name{i+1}"] and request.form[f"url{i+1}"]:
                new_image = Image(
                    image_name = request.form[f"name{i+1}"],
                    image_url = request.form[f"url{i+1}"]
                    )
                db.session.add(new_image)
                event.images.append(new_image)
                db.session.commit()
                flash("Successfully add images", 'success')
                return redirect(url_for("root.home"))
            flash("no image to add", "danger")            
    return render_template('addimages.html', id=id, origin=origin)

@event_blueprint.route('/<id>/', methods=['GET', 'POST'])
def single_event(id):
    event = Event.query.get(id)
    
    return render_template('singleevent.html', id=id, event=event)