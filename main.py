import datetime

from flask_login import login_user, current_user, LoginManager, login_required, logout_user
from pip._vendor import requests
from flask import Flask, request, render_template
from sqlalchemy import func

from data import db_session
from data.courier import Courier, BASE_COMPLETE_TIME
from data.delivery_hour import DeliveryHour
from forms.couriers_add_form import CourierAddForm
from forms.loginform import LoginForm
from data.order import Order
from data.order_in_progress import OrderInProgress
from data.region import Region
from data.working_hour import WorkingHour
from forms.order_append_form import OrderAppendForm
from forms.order_assign_form import OrderAssignForm
from forms.register import RegisterForm
from utils import make_resp, check_keys, check_all_keys_in_dict, check_time_in_times
from flask import redirect
from data.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flag_is_here'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    now_us = current_user
    if current_user.is_active:
        if current_user.role == 0:
            session = db_session.create_session()
            courier = session.query(Courier).filter(Courier.courier_id == current_user.login).first()
            if courier:
                rating = courier.get_rating(session)
                earning = courier.get_earning(session)
                return render_template('index.html', title='Домашняя страница', rating=rating, earning=earning)
    return render_template('index.html', title='Домашняя страница')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            login=form.login.data,
            password=form.password.data,
            role=2 if form.login.data != 'admin' else 1,
            name=form.name.data,
            surname=form.surname.data,
            phone_number=form.phone_number.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, message="Заполните все поля")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/orders_view/<login>', methods=['POST', 'GET'])
@login_required
def orders_view(login):
    session = db_session.create_session()
    form = OrderAssignForm()
    if current_user.login == 'admin':
        orders = session.query(Order).filter(Order.courier_taken == 0).all()
        return render_template('get_orders.html', orders=orders, form=form)
    else:
        if current_user.role == 0:
            courier = session.query(Courier).filter(Courier.courier_login == login).first()
            if request.method == 'POST' and current_user.role == 0:
                requests.post('http://localhost:8080/orders/assign', json=
                {
                    "courier_id": courier.courier_id
                })

            orders = session.query(OrderInProgress).filter(
                OrderInProgress.courier_id == courier.courier_id, OrderInProgress.duration == 0).all()
            orders = [i.order for i in orders]

            rating = courier.get_rating(session)
            earning = courier.get_earning(session)
        else:
            orders = session.query(OrderInProgress).filter(
                OrderInProgress.customer == login, OrderInProgress.duration == 0).all()
            orders = [i.order for i in orders]
            rating = 0
            earning = 0
            orders_in_queue = session.query(Order).filter(Order.customer == current_user.login,
                                                          Order.courier_taken == 0).all()
            orders = orders + orders_in_queue

    return render_template('get_orders.html', orders=orders, form=form, rating=rating, earning=earning)


@app.route('/order_append', methods=['GET', 'POST'])
@login_required
def order_append():
    form = OrderAppendForm()
    if request.method == 'POST':
        session = db_session.create_session()
        max_id = session.query(func.max(Order.order_id)).scalar()
        if not max_id:
            max_id = 0
        requests.post('http://localhost:8080/orders', json=
        {
            'data':
                [{"order_id": max_id + 1,
                  "weight": int(form.weight.data),
                  "region": int(form.region.data),
                  "delivery_hours": form.delivery_hours.data,
                  "customer": current_user.login,
                  "delivery_address": form.delivery_address.data,
                  "contactless_delivery": form.contactless_delivery.data,
                  "call_after_delivery": form.call_after_delivery.data,
                  "call_before_delivery": form.call_before_delivery.data,
                  "SMS_only": form.SMS_only.data}]

        })
        return render_template('confirm_order.html', order_id=max_id + 1, type='add')
    return render_template('order_append.html', form=form)


@app.route('/order_delete/<int:id>', methods=['GET', 'DELETE'])
@login_required
def order_delete(id):
    if current_user.login == 'admin':
        session = db_session.create_session()
        order = session.query(Order).filter(Order.order_id == id).first()
        session.delete(order)
        session.query(DeliveryHour).filter(DeliveryHour.order_id == None).delete()
        session.query(OrderInProgress).filter(OrderInProgress.order_id == None).delete()
        session.commit()
    return render_template('confirm_order.html', order_id=id, type='delete')


@app.route('/couriers_view/<int:id>', methods=['GET', 'DELETE'])
@login_required
def courier_delete(id):
    if current_user.login == 'admin':
        session = db_session.create_session()
        courier = session.query(Courier).filter(Courier.courier_id == id).first()
        session.delete(courier)
        session.query(WorkingHour).filter(WorkingHour.courier_id == None).delete()
        session.query(Region).filter(Region.courier_id == None).delete()
        session.query(User).filter(User.login == id).delete()
        session.commit()
    return render_template('confirm_courier.html', courier_id=id, type='delete')


@app.route('/courier_update/<int:id>', methods=['GET', 'POST'])
@login_required
def courier_update(id):
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    form = CourierAddForm()
    if current_user.login == 'admin':
        if request.method == 'POST':
            requests.patch(f'http://localhost:8080/couriers/{id}', json=
            {
                'courier_id': courier.courier_id,
                'courier_type': form.type.data,
                "regions": list(map(int, form.regions.data)),
                "working_hours": form.working_hours.data
            })
            return render_template('confirm_courier.html', type='update', courier_id=courier.courier_id)
    return render_template('courier_add.html', form=form, type='update', id=courier.courier_id)


@app.route('/courier_add/', methods=['GET', 'POST'])
@login_required
def courier_add():
    form = CourierAddForm()
    session = db_session.create_session()
    max_id = session.query(func.max(Courier.courier_id)).scalar()
    if not max_id:
        max_id = 0
    if request.method == 'POST':
        requests.post('http://localhost:8080/couriers', json=
        {
            'data':
                [{"courier_id": max_id + 1,
                  "courier_type": form.type.data,
                  "courier_login": form.login.data,
                  "regions": list(map(int, form.regions.data)),
                  "working_hours": form.working_hours.data,
                  "name": form.name.data,
                  "surname": form.surname.data,
                  "password": form.password.data}]

        })
        return render_template('confirm_courier.html', courier_id=max_id + 1, type='add')
    return render_template('courier_add.html', form=form)


@app.route('/couriers_view/', methods=['POST', 'GET'])
@login_required
def couriers_view():
    session = db_session.create_session()
    couriers = session.query(Courier).all()
    users = []
    for courier in couriers:
        user = session.query(User).filter(User.login == courier.courier_login).first()
        if user:
            users.append(
                {
                    'courier': courier,
                    'name': user.name,
                    'surname': user.surname
                }
            )
        else:
            users.append({
                'courier': courier,
                'name': 'Не',
                'surname': 'зарегистрирован'
            })
    return render_template('get_couriers.html', users=users)


@app.route('/order_done/<int:order_id>', methods=['POST', 'GET'])
@login_required
def order_done(order_id):  # Метод завершает выполнение заказа
    if request.method == 'GET':
        requests.post('http://localhost:8080/orders/complete', json=
        {
            "courier_id": current_user.login,
            "order_id": order_id,
            "complete_time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        })
    return render_template('confirm_order.html', order_id=order_id, type='complete')


@app.route('/couriers', methods=['POST'])  # Метод добавляет курьера в таблицу курьеров и таблицу пользователей
def post_couriers():
    session = db_session.create_session()
    get_data = request.json
    validation_error = []
    ids = []
    for i in get_data['data']:
        if not check_keys(i, (
                'courier_id', 'courier_type', 'regions', 'working_hours', 'courier_login', 'password', 'name',
                'surname')) or \
                not check_all_keys_in_dict(i,
                                           ('courier_id', 'courier_type', 'regions', 'working_hours', 'courier_login',
                                            'password', 'name', 'surname')):
            validation_error.append({"id": i['courier_id']})
        else:
            ids.append({"id": i['courier_id']})
            regions = []
            old_courier = session.query(Courier).filter(Courier.courier_id == i['courier_id']).first()
            if old_courier:
                session.delete(old_courier)
                session.commit()
            for j in i['regions']:
                region = Region(
                    region=j,
                    courier_id=i['courier_id']
                )
                regions.append(region)
            working_hours = []
            for j in i['working_hours']:
                working_hour = WorkingHour(
                    courier_id=i['courier_id']
                )
                working_hour.create_time(j)
                working_hours.append(working_hour)
            courier = Courier(
                courier_id=i['courier_id'],
                courier_type=i['courier_type'],
                courier_login=i['courier_login'],
                regions=regions,
                working_hours=working_hours
            )
            session.add(courier)
            session.commit()
            user = User(
                login=i["courier_login"],
                password=i["password"],
                role=0,
                name=i["name"],
                surname=i["surname"]
            )
            user.set_password(i["password"])
            session.add(user)
            session.commit()
    if validation_error:
        return make_resp(
            {
                'validation_error': {
                    "couriers": validation_error
                }
            }, 400)
    else:
        return make_resp(
            {
                "couriers": ids
            }, 201)


@app.route('/couriers/<int:id>', methods=['PATCH'])
def patch_courier(id):
    session = db_session.create_session()
    get_data = request.json
    if not check_all_keys_in_dict(get_data, ('courier_id', 'courier_type', 'regions', 'working_hours')):
        return make_resp('', 400)
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    if courier:
        if 'courier_type' in get_data.keys():
            session.query(Courier).filter(Courier.courier_id == id).update({
                'courier_type': get_data['courier_type']
            }
            )
        if 'regions' in get_data.keys():
            courier.update_regions(get_data['regions'], session)
        if 'working_hours' in get_data.keys():
            courier.update_working_hours(get_data['working_hours'], session)
        session.commit()
        courier = session.query(Courier).filter(Courier.courier_id == id).first()
        courier_type = courier.courier_type
        regions = [i.region for i in courier.regions]
        working_hours = []
        for i in courier.working_hours:
            working_hours.append(i.get_str_time())
        for i in courier.orders:
            if i.order.region not in regions or not check_time_in_times(courier.working_hours,
                                                                        i.order.delivery_hours[0]):
                i.order.is_taken = False
                session.query(OrderInProgress).filter(OrderInProgress.order_id == i.order_id).delete()
        return make_resp(
            {
                "courier_id": id,
                "courier_type": courier_type,
                "regions": regions,
                "working_hours": working_hours
            }
            , 200)
    else:
        return make_resp('', 400)


@app.route('/orders', methods=['POST'])
def post_orders():
    session = db_session.create_session()
    data = request.json
    validation_error = []
    ids = []
    for i in data['data']:
        if not check_keys(i, (
        'order_id', 'weight', 'region', 'delivery_hours', 'customer', 'delivery_address', 'contactless_delivery',
        'call_before_delivery', 'call_after_delivery', 'SMS_only')) or \
                not check_all_keys_in_dict(i, (
                'order_id', 'weight', 'region', 'delivery_hours', 'customer', 'delivery_address',
                'contactless_delivery', 'call_before_delivery', 'call_after_delivery', 'SMS_only')):
            validation_error.append({"id": i['order_id']})
        else:
            order = session.query(Order).filter(Order.order_id == i['order_id']).first()
            if order:
                session.delete(order)
                session.commit()
            ids.append({"id": i['order_id']})
            delivery_hours = []
            for j in i['delivery_hours']:
                delivery_hour = DeliveryHour(
                    order_id=i['order_id']
                )
                delivery_hour.create_time(j)
                delivery_hours.append(delivery_hour)
            order = Order(
                delivery_address=i['delivery_address'],
                order_id=i['order_id'],
                weight=i['weight'],
                region=i['region'],
                customer=i['customer'],
                delivery_hours=delivery_hours,
                contactless_delivery=i['contactless_delivery'],
                call_before_delivery=i['call_before_delivery'] if not i['SMS_only'] else 0,
                call_after_delivery=i['call_after_delivery'] if not i['SMS_only'] else 0,
                SMS_only=i['SMS_only']
            )
            session.add(order)
            session.commit()
    if validation_error:
        return make_resp(
            {
                'validation_error': {
                    "orders": validation_error
                }
            }, 400)
    else:
        return make_resp(
            {
                "orders": ids
            }, 201)


@app.route("/couriers/<int:id>", methods=["GET"])
def get_courier(id):
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.courier_id == id).first()
    if courier:
        courier_type = courier.courier_type
        regions = [i.region for i in courier.regions]
        working_hours = []
        for i in courier.working_hours:
            working_hours.append(i.get_str_time())
        rating = courier.get_rating(session)
        earnings = courier.get_earning(session)
        return make_resp({"courier_id": id,
                          "courier_type": courier_type,
                          "regions": regions,
                          "working_hours": working_hours,
                          "rating": rating,
                          "earnings": earnings
                          }, 200)
    else:
        return make_resp({'Message': "Courier not found"}, 400)


@app.route("/orders/complete", methods=["POST"])
def orders_complete():
    session = db_session.create_session()
    get_data = request.json
    date_time = datetime.datetime.strptime(get_data['complete_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if not check_all_keys_in_dict(get_data, ('courier_id', 'order_id', 'complete_time')):
        return make_resp('', 400)
    if not check_keys(get_data, ('courier_id', 'order_id', 'complete_time')):
        return make_resp('', 400)
    complete_order = session.query(OrderInProgress).filter(OrderInProgress.courier_id == get_data['courier_id'],
                                                           OrderInProgress.order_id == get_data['order_id']).first()
    if complete_order:
        complete_order.complete_time = date_time
        complete_id = complete_order.order_id
        complete_order.set_duration(session)
        session.merge(complete_order)
        session.commit()
        return make_resp(
            {
                "order_id": complete_id
            },
            200)
    return make_resp('', 400)


@app.route("/orders/assign", methods=["POST"])
def order_assign():
    time_now = datetime.datetime.now()
    session = db_session.create_session()
    get_data = request.json
    courier = session.query(Courier).filter(Courier.courier_id == get_data['courier_id']).first()
    if courier:
        weight = {'foot': 10, 'bike': 15, 'car': 50}
        max_weight = weight[courier.courier_type]
        orders_in_progress = courier.orders
        add_weight = max_weight - sum(
            [i.order.weight for i in orders_in_progress if i.complete_time == BASE_COMPLETE_TIME])
        if not courier.working_hours or not courier.regions:
            return make_resp(
                {
                    "orders": [],
                    "assign_time": time_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                },
                200)
        time_condition = "("
        region_condition = "("
        for hour in courier.working_hours:
            time_condition += f"(dh.start_time <= '{hour.end_time}' and dh.end_time >= '{hour.start_time}') or "
        time_condition = time_condition[:-4]
        time_condition += ")"
        for reg in courier.regions:
            region_condition += f"o.region = {reg.region} or "
        region_condition = region_condition[:-4]
        region_condition += ")"
        res = session.execute("select * from orders o "
                              "join delivery_hours dh on o.order_id = dh.order_id  " +
                              "where o.courier_taken = 0 and " + time_condition + " and " + region_condition +
                              f" and o.weight <= {weight[courier.courier_type]} group by o.order_id limit {add_weight * 100}").fetchall()
        res_ids = [i[0] for i in res]
        orders = session.query(Order).filter(Order.order_id.in_(res_ids)).all()
        courier_orders = []
        for order in orders:
            if add_weight >= order.weight:
                add_weight -= order.weight
                courier_orders.append(order)
            elif not weight:
                break
        for order in courier_orders:
            order_in_progress = OrderInProgress(
                order_id=order.order_id,
                courier_id=courier.courier_id,
                assign_time=time_now,
                complete_time=BASE_COMPLETE_TIME,
                courier_type=courier.courier_type,
                customer=order.customer
            )
            order.courier_taken = True
            session.add(order_in_progress)
            session.commit()
        orders = [i for i in courier.orders if i.complete_time == BASE_COMPLETE_TIME]
        if orders:
            return make_resp(
                {
                    "orders": [{"id": i.order_id} for i in orders if i.complete_time == BASE_COMPLETE_TIME],
                    "assign_time": time_now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                },
                200)
        else:
            return make_resp(
                {
                    "orders": [{"id": i.order_id} for i in orders if i.complete_time == BASE_COMPLETE_TIME]
                },
                200)
    else:
        return make_resp('', 400)


def main():
    db_session.global_init("db/yaschool.sqlite")
    # serve(app, host='0.0.0.0', port=8080)
    app.run(port=8080, host='127.0.0.1')


main()
