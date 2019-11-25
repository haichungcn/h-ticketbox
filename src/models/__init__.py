from src import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User Authentication fields
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime(timezone=True))
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    #relationship
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    events = db.relationship('Event', secondary='attends', backref=db.backref('users', lazy=True))
    orders = db.relationship('Order', backref=db.backref('user', lazy=True))
    # User fields
    avatar_url = db.Column(db.Text)
    active = db.Column(db.Boolean())
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    birthday = db.Column(db.DateTime(timezone=True))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_email(self, email):
        return User.query.filter_by(email = email).first()

    def cart(self):
        order = Order.query.filter_by(client_id = self.id, isPaid = False).first()
        if not order:
            order = Order(client_id=user.id)
            db.session.add(order)
            db.session.commit()
        return order

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', backref=db.backref('role'))

# event models
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizers.id'))
    start_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime)
    end_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime)
    location = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    #event properties
    images = db.relationship('Image', backref='event')
    articles = db.relationship('Article', backref='event')
    tickettypes = db.relationship('Tickettype', backref='event')
    interested_people = db.relationship('User', secondary='interests', backref=db.backref('interested_events', lazy=True))
    categories = db.relationship('Category', secondary='category_events', backref=db.backref('events', lazy=True))

    def check_event(self, name):
        return Event.query.filter_by(name = name).first()

attends = db.Table('attends',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(200))
    image_url = db.Column(db.Text, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.Text, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

class Organizer(db.Model):
    __tablename__ = 'organizers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    avatar_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    events = db.relationship('Event', backref='organizer')
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())
    
    def check_org(self):
        return Organizer.query.filter_by(name = self.name).first()

class Tickettype(db.Model):
    __tablename__ = 'tickettypes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
    #ticket properties:
    orders = db.relationship('Orderitem', backref='tickettype')
    benefits = db.Column(db.Text, nullable=False)
    tickets = db.relationship('Ticket', backref='tickettype')

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    serial = db.Column(db.String, nullable=False, unique=True)
    qrcode = db.Column(db.String, nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)
    tickettype_id = db.Column(db.Integer, db.ForeignKey('tickettypes.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orderitems.id'))    

interests = db.Table('interests',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)

category_events = db.Table('category_events',
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'))
)

# order models:
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    orderitems = db.relationship('Orderitem', backref='order')
    isPaid = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

class Orderitem(db.Model):
    __tablename__ = 'orderitems'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    tickettype_id = db.Column(db.Integer, db.ForeignKey('tickettypes.id'))
    amount = db.Column(db.Integer, nullable=False, default=1)

# date_object = datetime.strptime(date_string, "%H:%M").time()
