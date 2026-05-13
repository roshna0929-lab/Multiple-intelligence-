from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurations
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager(app)

# =========================
# DATABASE MODELS
# =========================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SchoolClass(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    subjects = db.relationship(
        'Subject',
        backref='school_class',
        lazy=True
    )


class Subject(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    class_id = db.Column(
        db.Integer,
        db.ForeignKey('school_class.id'),
        nullable=False
    )

    topics = db.relationship(
        'Topic',
        backref='subject',
        lazy=True
    )


class Topic(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey('subject.id'),
        nullable=False
    )

    quizzes = db.relationship(
        'Quiz',
        backref='topic',
        lazy=True
    )


class Quiz(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(db.String(255), nullable=False)

    options = db.Column(db.PickleType, nullable=False)

    answer = db.Column(db.String(100), nullable=False)

    topic_id = db.Column(
        db.Integer,
        db.ForeignKey('topic.id'),
        nullable=False
    )


# =========================
# LOGIN USER LOADER
# =========================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template("index.html")


# =========================
# USER REGISTRATION
# =========================

@app.route('/users/register', methods=['POST'])
def register():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "message": "Username and password required"
        }), 400

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return jsonify({
            "message": "Username already exists"
        }), 400

    new_user = User(username=username)

    new_user.set_password(password)

    db.session.add(new_user)

    db.session.commit()

    return jsonify({
        "message": "User registered successfully"
    }), 201


# =========================
# USER LOGIN
# =========================

@app.route('/users/login', methods=['POST'])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if user and user.check_password(password):

        login_user(user)

        return jsonify({
            "message": "Logged in successfully"
        })

    return jsonify({
        "message": "Invalid username or password"
    }), 401


# =========================
# USER LOGOUT
# =========================

@app.route('/users/logout')
@login_required
def logout():

    logout_user()

    return jsonify({
        "message": "Logged out successfully"
    })


# =========================
# ADD CLASS
# =========================

@app.route('/classes', methods=['POST'])
@login_required
def add_class():

    data = request.get_json()

    class_name = data.get("name")

    new_class = SchoolClass(name=class_name)

    db.session.add(new_class)

    db.session.commit()

    return jsonify({
        "message": "Class added successfully",
        "class_id": new_class.id
    })


# =========================
# GET ALL CLASSES
# =========================

@app.route('/classes', methods=['GET'])
def get_classes():

    classes = SchoolClass.query.all()

    result = []

    for c in classes:
        result.append({
            "id": c.id,
            "name": c.name
        })

    return jsonify(result)


# =========================
# ADD SUBJECT
# =========================

@app.route('/subjects', methods=['POST'])
@login_required
def add_subject():

    data = request.get_json()

    new_subject = Subject(
        name=data.get("name"),
        class_id=data.get("class_id")
    )

    db.session.add(new_subject)

    db.session.commit()

    return jsonify({
        "message": "Subject added successfully",
        "subject_id": new_subject.id
    })


# =========================
# GET SUBJECTS
# =========================

@app.route('/classes/<int:class_id>/subjects', methods=['GET'])
def get_subjects(class_id):

    subjects = Subject.query.filter_by(
        class_id=class_id
    ).all()

    result = []

    for s in subjects:
        result.append({
            "id": s.id,
            "name": s.name
        })

    return jsonify(result)


# =========================
# ADD TOPIC
# =========================

@app.route('/topics', methods=['POST'])
@login_required
def add_topic():

    data = request.get_json()

    new_topic = Topic(
        name=data.get("name"),
        subject_id=data.get("subject_id")
    )

    db.session.add(new_topic)

    db.session.commit()

    return jsonify({
        "message": "Topic added successfully",
        "topic_id": new_topic.id
    })


# =========================
# GET TOPICS
# =========================

@app.route('/subjects/<int:subject_id>/topics', methods=['GET'])
def get_topics(subject_id):

    topics = Topic.query.filter_by(
        subject_id=subject_id
    ).all()

    result = []

    for t in topics:
        result.append({
            "id": t.id,
            "name": t.name
        })

    return jsonify(result)


# =========================
# ADD QUIZ
# =========================

@app.route('/quizzes', methods=['POST'])
@login_required
def add_quiz():

    data = request.get_json()

    new_quiz = Quiz(
        question=data.get("question"),
        options=data.get("options"),
        answer=data.get("answer"),
        topic_id=data.get("topic_id")
    )

    db.session.add(new_quiz)

    db.session.commit()

    return jsonify({
        "message": "Quiz added successfully",
        "quiz_id": new_quiz.id
    })


# =========================
# GET QUIZZES
# =========================

@app.route('/topics/<int:topic_id>/quizzes', methods=['GET'])
def get_quizzes(topic_id):

    quizzes = Quiz.query.filter_by(
        topic_id=topic_id
    ).all()

    result = []

    for q in quizzes:
        result.append({
            "id": q.id,
            "question": q.question,
            "options": q.options,
            "answer": q.answer
        })

    return jsonify(result)


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
