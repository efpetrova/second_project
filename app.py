import json
import random
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField
from wtforms.validators import Length
from wtforms.widgets import HiddenInput
from models import Teacher, Booking, Request

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'

with open('data.json', 'r') as f:
    database = json.load(f)
    goals = database['goals']
    days = database['days']
    frequencies = database['frequencies']


def get_id_teachers(goal):
    return db.session.query(Teacher).filter(Teacher.goals.contains(goal)).order_by(Teacher.rating).all()


@app.route('/')
def main():
    teachers_ = db.session.query(Teacher).all()
    return render_template('index.html', teachers=random.choices(teachers_, k=6), goals=goals)


@app.route('/goals/<goal_id>/')
def goal(goal_id):
    goal = goals[goal_id]
    return render_template('goal.html', goal=goal, teachers=get_id_teachers(goal_id))


class RequestForm(FlaskForm):
    name = StringField('Вас зовут', [Length(min=3)])
    phone = StringField('Ваш телефон', [Length(min=9)])
    goal = RadioField(choices=list(zip(goals.keys(), goals.values())))

    frequency = RadioField(
        choices=list(zip(frequencies.keys(), frequencies.values())))


@app.route('/request/', methods=['GET'])
def request():
    request_form = RequestForm(data={'goal': 'travel', 'frequency': '1'})
    return render_template('request.html', form=request_form)


@app.route('/request/create/', methods=['POST'])
def request_create():
    my_req_form = RequestForm()

    def _create_request(form):
        request = Request()
        form.populate_obj(request)
        db.session.add(request)
        db.session.commit()

    if my_req_form.validate_on_submit():
        _create_request(my_req_form)
        return render_template('request_done.html', goals=my_req_form.goal.data, frequencies=my_req_form.frequency.data,
                               form=my_req_form)
    else:
        return render_template('request.html', form=my_req_form)


@app.route('/profile/<teacher_id>')
def profile(teacher_id):
    teacher = db.session.query(Teacher).get_or_404(int(teacher_id))
    return render_template('profile.html', teacher=teacher, teacher_id=teacher_id, days=days)


class BookingForm(FlaskForm):
    name = StringField('Имя', [Length(min=3)])
    phone = StringField('Телефон', [Length(min=9)])
    date = StringField('date', widget=HiddenInput())
    time = StringField('time', widget=HiddenInput())
    teacher_id = IntegerField('teacher_id', widget=HiddenInput())


@app.route('/booking/<teacher_id>/<day>/<time>/', methods=['GET'])
def booking(teacher_id, day, time):
    booking_form = BookingForm(data={'teacher_id': teacher_id, 'date': day, 'time': time})  # создание инстанса
    return render_template('booking.html', form=booking_form)


@app.route('/booking/create/', methods=['POST'])
def booking_create():
    my_booking = BookingForm()

    def _create_booking():
        booking = Booking()
        my_booking.populate_obj(booking)
        db.session.add(booking)
        db.session.commit()

    if my_booking.validate_on_submit():
        _create_booking()
        return render_template('booking_done.html', form=my_booking)
    else:
        return render_template('booking.html', form=my_booking)


if __name__ == '__main__':
    app.run()
