import json

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


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


class StudentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Student

    id = ma.auto_field()
    name = ma.auto_field()
    city = ma.auto_field()
    addr = ma.auto_field()
    pin = ma.auto_field()


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
        student_schema = StudentSchema()
        return jsonify({"status": "success", "data": student_schema.dump(student)})
    except Exception as e:
        return jsonify({"error": e})


@app.route('/student/<student_id>', methods=['POST'])
def student_update(student_id):
    request_data = json.loads(request.data)
    try:
        student = Student.query.get(student_id)
        student.name = request_data.get('name', '')
        student.city = request_data.get('city', '')
        student.addr = request_data.get('addr', '')
        student.pin = request_data.get('pin', '')
        db.session.commit()
        student_schema = StudentSchema()
        return jsonify({"status": "success", "data": student_schema.dump(student)})
    except Exception as e:
        return jsonify({"error": e})


@app.route('/student', methods=['GET'])
def student_list():
    try:
        students = Student.query.all()
        student_schema = StudentSchema(many=True)
        return jsonify({"status": "success", "data": student_schema.dump(students)})
    except Exception as e:
        return jsonify({"error": e})


@app.route('/student/<student_id>', methods=['GET'])
def student_get_by_id(student_id):
    try:
        student = Student.query.get(student_id)
        student_schema = StudentSchema()
        return jsonify({"status": "success", "data": student_schema.dump(student)})
    except Exception as e:
        return jsonify({"error": e})


@app.route('/student/<student_id>', methods=['DELETE'])
def student_delete(student_id):
    try:
        Student.query.filter_by(student_id=student_id).delete()
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": e})


if __name__ == '__main__':
    app.run()
