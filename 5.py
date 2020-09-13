import json
from functools import wraps

from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if token == '':
            return {"status": "failed", "error": 'Authorization token is missing.'}
        elif token == 'valid':
            return f({'user': 'admin'}, *args, **kwargs)
        else:
            return {"status": "failed", "error": 'Invalid token.'}
    return decorated


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


class NoteBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(40), nullable=False)
    subject_name = db.Column(db.String(40), nullable=False, default='Default Book')
    completed = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    student = db.relationship('Student', backref='note_books')

    def __init__(self, code, subject_name, completed=False):
        self.code = code
        self.subject_name = subject_name
        self.completed = completed


class NoteBookSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteBook

    id = ma.auto_field()
    code = ma.auto_field()
    subject_name = ma.auto_field()
    completed = ma.auto_field()


class StudentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Student

    id = ma.auto_field()
    name = ma.auto_field()
    city = ma.auto_field()
    addr = ma.auto_field()
    pin = ma.auto_field()
    note_books = ma.List(ma.Nested(NoteBookSchema))


class StudentOnlySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Student

    id = ma.auto_field()
    name = ma.auto_field()
    city = ma.auto_field()
    addr = ma.auto_field()
    pin = ma.auto_field()


class NoteBookOnlySchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteBook

    id = ma.auto_field()
    code = ma.auto_field()
    subject_name = ma.auto_field()
    completed = ma.auto_field()
    student = ma.Nested(StudentOnlySchema)


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


@app.route('/student/<student_id>/add_note_book', methods=['POST'])
@login_required
def student_update_notebook(current_user, student_id):
    print(current_user)
    request_data = json.loads(request.data)
    student = Student.query.get(student_id)
    try:
        code = request_data.get('code', '')
        subject_name = request_data.get('subject_name', '')
        completed = request_data.get('completed', False)
        book = NoteBook(code, subject_name, completed)
        student.note_books.append(book)
        db.session.commit()
        student_schema = NoteBookOnlySchema()
        return jsonify({"status": "success", "data": student_schema.dump(book)})
    except Exception as e:
        return jsonify({"error": e})


if __name__ == '__main__':
    app.run()
