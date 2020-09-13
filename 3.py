import json

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Student(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))
    pin = db.Column(db.Integer())

    def __init__(self, name, city, addr, pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin


@app.route('/student', methods=['POST'])
def student_create():
    request_data = json.loads(request.data)
    name = request_data.get('name', '')
    city = request_data.get('city', '')
    addr = request_data.get('addr', '')
    pin = request_data.get('pin', '')
    try:
        student = Student(name, city, addr, pin)
        db.session.add(student)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({"error": e})


if __name__ == '__main__':
    app.run()
