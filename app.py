from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms import HiddenField
from wtforms.widgets import HiddenInput
from wtforms import RadioField
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
migrate.init_app(app, db)

app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'

with open('data.json', 'r') as f:
    database = json.load(f)

teachers = database["teachers"]
goals = database['goals']
with open('bookings.json', 'r') as f:
    bookings = json.load(f)


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float)
    picture = db.Column(db.String)
    price = db.Column(db.Integer)
    goals = db.Column(db.String)
    schedule = db.Column(db.String)
    booking = db.relationship("Booking",back_populates="teacher")


def update_teachers():
    teachers_entries = []
    for line in database["teachers"]:
        new_entry = Teacher(id=line['id'], name=line['name'], about=line['about'], rating=line['rating'],
                            picture=line['picture'], price=line['price'], goals=",".join(line['goals']), schedule=json.dumps(line['free'])
                            )
        teachers_entries.append(new_entry)


    db.session.add_all(teachers_entries)
    db.session.commit()


#update_teachers()


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    teacher = db.relationship("Teacher", db.ForeignKey('teachers.id'),back_populates="booking")
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String)
    date = db.Column(db.Date)
    time = db.Column(db.Time)


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String)
    goal = db.Column(db.String)
    frequency = db.Column(db.String)


db.create_all()


def create_booking(form):
    record = {'teacher_id': form.teacher_id.data, 'name': form.name.data, 'phone': form.phone.data,
              'time': form.time.data, 'date': form.date.data}
    bookings.append(record)
    with open('bookings.json', "w", encoding='utf-8') as f:
        json.dump(bookings, f,
                  indent=2)


with open('request.json', 'r') as f:
    requests = json.load(f)


def create_request(form):
    record = {"requests": {'name': form.name.data, 'phone': form.phone.data, 'goal': form.goal.data,
                           'frequency': form.frequency.data}}
    requests.append(record)
    with open('request.json', "w", encoding='utf-8') as f:
        json.dump(requests, f,
                  indent=2)


days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота",
        "sun": "Воскресенье"}
frequencies = {"1": "1-2 часа в неделю", "2": "3-5 часов в неделю", "3": "5-7 часов в неделю",
               "4": "7-10 часов в неделю"}


@app.route('/')
def main():
    return render_template('index.html', teachers=random.choices(teachers, k=6), goals=goals)


def get_id_teacher(goal):
    return [k for k in teachers if goal in k["goals"]]


@app.route('/goals/<goal_id>/')
def goal(goal_id):
    goal = goals[goal_id]
    return render_template('goal.html', goal=goal, teachers=get_id_teacher(goal_id))


class RequestForm(FlaskForm):
    name = StringField('Вас зовут')
    phone = StringField('Ваш телефон')
    goal = RadioField(choices=list(zip(goals.keys(), goals.values())))

    frequency = RadioField(
        choices=[("1", "1-2 часа в неделю"), ("2", "3-5 часов в неделю"), ("3", "5-7 часов в неделю"),
                 ("4", "7-10 часов в неделю")])


@app.route('/request/', methods=['GET'])
def request():
    request_form = RequestForm(data={'goal': 'travel', 'frequency': '1'})
    return render_template('request.html', form=request_form)


@app.route('/request_done', methods=['POST'])
def request_done():
    my_request = RequestForm()
    create_request(my_request)
    return render_template('request_done.html', form=my_request, goals=goals, frequencies=frequencies)


@app.route('/profile/<teacher_id>')
def profile(teacher_id):
    teacher = teachers[int(teacher_id)]
    return render_template('profile.html', teacher=teacher, teacher_id=teacher_id, days=days)


class BookingForm(FlaskForm):
    name = StringField('Имя')
    phone = StringField('Телефон')
    date = StringField('date', widget=HiddenInput())
    time = StringField('time', widget=HiddenInput())
    teacher_id = IntegerField('teacher_id', widget=HiddenInput())


@app.route('/booking/<teacher_id>/<day>/<time>/', methods=['GET'])
def booking(teacher_id, day, time):
    teacher_name = teachers[int(teacher_id)]['name']
    booking_form = BookingForm(data={'teacher_id': teacher_id, 'date': day, 'time': time})  # создание инстанса
    return render_template('booking.html', teacher_name=teacher_name, day=day, time=time, form=booking_form)


@app.route('/booking_done', methods=['POST'])
def booking_done():
    my_booking = BookingForm()
    create_booking(my_booking)
    return render_template('booking_done.html', form=my_booking)


if __name__ == '__main__':
    app.run()
