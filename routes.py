from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Root route
@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard' if user.is_admin else 'user.dashboard'))
        flash('Invalid username or password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        # Set first user as admin
        if User.query.count() == 0:
            user.is_admin = True

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Admin routes
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    subjects = Subject.query.all()
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/dashboard.html', subjects=subjects, users=users)

@admin_bp.route('/subject/add', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    name = request.form.get('name')
    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/chapter/add', methods=['POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    name = request.form.get('name')
    subject_id = request.form.get('subject_id')
    chapter = Chapter(name=name, subject_id=subject_id)
    db.session.add(chapter)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/quiz/manage/<int:chapter_id>')
@login_required
def manage_quiz(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/quiz_management.html', chapter=chapter)

# User routes
@user_bp.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.all()
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', subjects=subjects, attempts=attempts)

@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if datetime.utcnow() < quiz.start_date or datetime.utcnow() > quiz.end_date:
        flash('Quiz is not available at this time')
        return redirect(url_for('user.dashboard'))
    return render_template('user/quiz.html', quiz=quiz)

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = 0
    for question in quiz.questions:
        answer = request.form.get(f'question_{question.id}')
        if answer == question.correct_answer:
            score += 1

    attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz_id, score=score)
    db.session.add(attempt)
    db.session.commit()
    flash(f'Quiz submitted! Your score: {score}/{len(quiz.questions)}')
    return redirect(url_for('user.dashboard'))