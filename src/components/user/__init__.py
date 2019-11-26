from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import *
from src import db
from itsdangerous import URLSafeTimedSerializer
import requests
from sqlalchemy.sql import func



user_blueprint = Blueprint('user', __name__, template_folder='../../templates/user')

def send_email(token, email, content):
    url="https://api.mailgun.net/v3/mg.haifly.dev/messages"
    try:
        response = requests.post(url,
                auth=('api', app.config['EMAIL_API']),
                data={'from': 'THE HIGHTABLE OF HTICKETBOX <admin@hticketbox.com>',
                'to': [email],
                'subject': 'HTicketBox Reset Password',
                'text': [content]}
            )
        response.raise_for_status()
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')

@user_blueprint.route('/', methods=['GET'])
@login_required
def root():
    return render_template('index.html')

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User()
        user = user.check_email(request.form['email'])
        if not user:
            flash("Can not find user", "danger")
            redirect(url_for("user.login"))
        if not user.check_password(request.form['password']):
            flash("Invalid password", "danger")
            redirect(url_for("user.login"))
        login_user(user)
        # current_user.order_amount = 0
        # if len(current_user.orders) > 0 and current_user.orders[-1].isPaid == False:
        #     for item in current_user.orders[-1].orderitems:
        #         current_user.order_amount += item.amount
        #     print(current_user.order_amount)
        return redirect(url_for("root.home"))
    return render_template('login.html')

@user_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User()
        user = user.check_email(request.form['email'])
        if not user:
            new_user = User(
                username = request.form['username'],
                email = request.form['email'],
                avatar_url = request.form['avatar_url'],
                active = True
                )
            if request.form['birthday']:
                new_user.birthday = request.form['birthday']
            if request.form['first_name']:
                new_user.first_name = request.form['first_name'],
            if request.form['last_name']:
                new_user.last_name = request.form['last_name'],
            new_user.set_password(request.form['password'])
            client_role = Role.query.get(2)
            client_role.users.append(new_user)
            db.session.add(new_user)
            db.session.commit()
            flash("successfully added user {0}".format(new_user.username), "success")
            return redirect(url_for('user.login'))
        else:
            flash("Username is already exist", "warning")
    return render_template('signup.html')

@user_blueprint.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for('root.home'))

@user_blueprint.route('/forgetpassword', methods=['GET', 'POST'])
def forgetpassword():
    if current_user.is_authenticated:
        return redirect(url_for('root.home'))
    if request.method == 'POST':
        user = User(email = request.form['email']).check_email(request.form['email'])
        if not user:
            flash('Invalid Email', 'danger')
            return redirect(url_for('user.forgetpassword'))
        s = URLSafeTimedSerializer(app.secret_key)
        token = s.dumps(user.email, salt="RESET_PASSWORD")
        content = f"""Hi {user.username}, pleaser click on this link to create new password:\nhttps://localhost:5000/resetpassword/{token} \n This link only valid for 15 minutes so please hurry!"""
        send_email(token, user.email, content)
        flash('Thank you for submit, Please check your email box (or spam box) within 15 minutes.', 'success')
        return redirect(url_for('user.login'))
    return render_template('forgetpassword.html')

@user_blueprint.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    s = URLSafeTimedSerializer(app.secret_key)
    email = s.loads(token, salt="RESET_PASSWORD", max_age=900)
    user = User(email = email).check_email(email)
    if not user:
        flash('Invalid link, please try again', 'danger')
        return redirect(url_for('user.forgetpassword'))
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm']:
            flash('Please enter the right confirm password', 'danger')
            return redirect(url_for('user.resetpassword', token=token))
        user.set_password(request.form['password'])
        db.session.commit()
        flash('successfully create new password', 'success')
        content = f"""Hi {user.username}, Your password has been changed, please visit <a href='https://h-ticketbox.herokuapp.com/user/login'>this page</a> to log in."""
        send_email(token, user.email, content)
    return render_template('resetpassword.html')

@user_blueprint.route('/addtocart/<id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(id):
    event = Event.query.get(id)
    if request.method == 'POST':
        order = Order.query.filter_by(client_id = current_user.id, isPaid = False).first()
        if not order:
            order = Order(client_id=current_user.id)
            db.session.add(order)
            db.session.commit()
        amount =  int(request.form['amount'])
        tickettype = Tickettype.query.get(request.args.get('tickettype_id'))
        print('user order: ', tickettype.id, amount)
        item = Orderitem.query.filter_by(tickettype_id = tickettype.id, order_id = order.id).first()
        if item:
            item.amount += amount
        else:
            orderitem = Orderitem(
                order_id = order.id,
                tickettype_id = tickettype.id,
                amount = amount
            )
            db.session.add(orderitem)
        tickettype.stock = tickettype.stock - amount
        db.session.commit()
        print('added to order', orderitem.order_id, orderitem.tickettype_id, orderitem.amount)
        flash("Successfully added to cart", "success")
    return render_template("singleevent.html", id=id, event=event)

@user_blueprint.route('/<id>/cart/', methods=['GET', 'POST'])
@login_required
def cart(id):
    order = Order.query.filter_by(client_id = current_user.id, isPaid = False).first()
    if not order:
        order = Order(client_id=current_user.id)
        db.session.add(order)
        db.session.commit()
    total_amount = 0
    item_price = 0
    for item in order.orderitems:
        item_price = item.amount * item.tickettype.price
        total_amount = total_amount + item_price
    return render_template('cart.html', order=order, user=current_user, total=total_amount)

@user_blueprint.route('/<id>/cart/updatecart', methods=['GET', 'POST'])
@login_required
def update_cart(id):
    order = Order.query.filter_by(client_id = current_user.id, isPaid = False).first()
    if request.method == "POST":
        update_list = request.form.to_dict(flat=True)

        for index, item in enumerate(order.orderitems):
            new_amount = int(update_list[f'amount_{index+1}'])
            change = new_amount - item.amount
            if change > 0:
                if item.tickettype.stock >= change:
                    item.tickettype.stock -= change
                    item.amount = new_amount
                else:
                    flash(f"We dont have enough ticket type {item.tickettype.name}", 'warning')
                    return redirect(url_for('user.cart', id=id))
            elif change = 0:
                db.session.delete(item)
            else:
                item.tickettype.stock += change
                item.amount = new_amount

        db.session.commit()
        print("successfully update")
        flash('successfully update cart', "success")
        return redirect(url_for('user.cart', id=id))
    return redirect(url_for('user.cart', id=id))

@user_blueprint.route('/<id>/cart/checkout', methods=['GET', 'POST'])
@login_required
def checkout(id):
    order = Order.query.filter_by(client_id = current_user.id, isPaid = False).first()
    if not order:
        order = Order(client_id=current_user.id)
        db.session.add(order)
        db.session.commit()
    if request.method == "POST":
        update_list = request.form.to_dict(flat=True)

        for index, item in enumerate(order.orderitems):
            new_amount = int(update_list[f'amount_{index+1}'])
            change = new_amount - item.amount
            if change >= 0:
                if item.tickettype.stock >= change:
                    item.tickettype.stock -= change
                    item.amount = new_amount
                else:
                    flash(f"We dont have enough ticket type {item.tickettype.name}", 'warning')
                    return redirect(url_for('user.cart', id=id))
            else:
                item.tickettype.stock += change
                item.amount = new_amount

        order.isPaid = True
        db.session.commit()
        flash('successfully checked out', "success")
        return redirect(url_for('root.home', id=id))
    return redirect(url_for('user.cart', id=id))

