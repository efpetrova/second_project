from flask import Flask, render_template
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms import HiddenField
from wtforms.widgets import HiddenInput


app = Flask(__name__)
app.secret_key = 'my-super-secret-phrase-I-dont-tell-this-to-nobody'

with open('data.json', 'r') as f:
    database = json.load(f)

teachers = database["teachers"]

with open('bookings.json', 'r') as f:
    bookings = json.load(f)

def create_booking(form):
    record = {'teacher_id': form.teacher_id.data, 'name': form.name.data, 'phone': form.phone.data, 'time': form.time.data, 'date':form.date.data }
    bookings.append(record)
    with open('bookings.json', "w", encoding='utf-8') as f:
        json.dump(bookings, f,
                  indent=2)


days = {"mon": "Понедельник", "tue": "Вторник", "wed": "Среда", "thu": "Четверг", "fri": "Пятница", "sat": "Суббота",
        "sun": "Воскресенье"}

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/goals/<goal>/')
def goal(goal):
    return render_template('goal.html')


@app.route('/request/')
def request():
    return render_template('request.html')


@app.route('/profile/<teacher_id>')
def profile(teacher_id):
    teacher = teachers[int(teacher_id)]
    return render_template('profile.html', teacher=teacher,teacher_id=teacher_id,days=days)


@app.route('/request_done/')
def request_done():
    return render_template('request_done.html')


class BookingForm(FlaskForm):
    name = StringField('Имя')
    phone = StringField('Телефон')
    date=StringField('date',widget=HiddenInput())
    time=StringField('time', widget=HiddenInput())
    teacher_id=IntegerField('teacher_id',widget=HiddenInput())


@app.route('/booking/<teacher_id>/<day>/<time>/',methods=['GET'])
def booking(teacher_id,day,time):
    teacher_name=teachers[int(teacher_id)]['name']
    booking_form = BookingForm(data={'teacher_id': teacher_id,'date':day,'time':time})  # создание инстанса
    return render_template('booking.html',teacher_name=teacher_name,day=day,time=time,form=booking_form)


@app.route('/booking_done',methods=['POST'])
def booking_done():
    my_booking=BookingForm()
    create_booking(my_booking)
    return render_template('booking_done.html',form=my_booking)


if __name__ == '__main__':
    app.run()
