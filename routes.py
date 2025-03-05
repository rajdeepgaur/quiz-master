from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User, Subject, Chapter, Quiz, Question, QuizAttempt
from datetime import datetime, timedelta
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Root route
@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.user_dashboard'))
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
            # Clear any existing flash messages
            session.pop('_flashes', None)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.user_dashboard'))

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
        return redirect(url_for('user.user_dashboard'))
    subjects = Subject.query.all()

    # Get statistics for admin dashboard
    stats = {
        'total_users': User.query.filter_by(is_admin=False).count(),
        'active_quizzes': Quiz.query.filter(
            Quiz.start_date <= datetime.utcnow(),
            Quiz.end_date >= datetime.utcnow()
        ).count(),
        'completed_attempts': QuizAttempt.query.count(),
        'avg_score': db.session.query(func.avg(QuizAttempt.score)).scalar() or 0
    }

    # Get subject statistics with explicit joins
    subject_stats = db.session.query(
        Subject.name,
        func.count(Quiz.id).label('quiz_count')
    ).select_from(Subject)\
    .outerjoin(Chapter, Chapter.subject_id == Subject.id)\
    .outerjoin(Quiz, Quiz.chapter_id == Chapter.id)\
    .group_by(Subject.name)\
    .all()

    subject_chart_data = {
        'labels': [s[0] for s in subject_stats],
        'data': [s[1] for s in subject_stats]
    }

    return render_template('admin/dashboard.html', 
                         subjects=subjects,
                         stats=stats,
                         subject_chart_data=subject_chart_data)

@admin_bp.route('/subject/add', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    name = request.form.get('name')
    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/chapter/add', methods=['POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
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
        return redirect(url_for('user.user_dashboard'))
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('admin/quiz_management.html', chapter=chapter)

@admin_bp.route('/quiz/add/<int:chapter_id>', methods=['POST'])
@login_required
def add_quiz(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    if request.method == 'POST':
        try:
            # Get quiz details from form
            title = request.form.get('title')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            duration = int(request.form.get('duration'))

            # Set start time to beginning of day and end time to end of day
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = start_date.replace(hour=23, minute=59, second=59)

            # Create quiz
            quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                duration=duration,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(quiz)
            db.session.flush()  # Get quiz.id before committing

            # Process questions
            questions_data = {}
            for key, value in request.form.items():
                if key.startswith('questions['):
                    parts = key.replace('questions[', '').replace(']', ' ').split()
                    idx, field = parts[0], parts[1].replace('[', '').replace(']', '')

                    if idx not in questions_data:
                        questions_data[idx] = {}
                    questions_data[idx][field] = value

            # Create Question objects
            for idx, q_data in questions_data.items():
                if 'text' in q_data:  # Ensure we have complete question data
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_data['text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct']
                    )
                    db.session.add(question)

            db.session.commit()
            flash('Quiz created successfully!')

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}')

        return redirect(url_for('admin.manage_quiz', chapter_id=chapter_id))

@admin_bp.route('/quiz/edit/<int:quiz_id>')
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('admin/edit_quiz.html', quiz=quiz)

@admin_bp.route('/quiz/update/<int:quiz_id>', methods=['POST'])
@login_required
def update_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    quiz = Quiz.query.get_or_404(quiz_id)

    try:
        # Update quiz details
        quiz.title = request.form.get('title')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        quiz.duration = int(request.form.get('duration'))

        # Set start time to beginning of day and end time to end of day
        quiz.start_date = start_date.replace(hour=0, minute=0, second=0)
        quiz.end_date = start_date.replace(hour=23, minute=59, second=59)

        # Process questions
        questions_data = {}
        existing_question_ids = set()

        # Collect form data
        for key, value in request.form.items():
            if key.startswith('questions['):
                parts = key.replace('questions[', '').replace(']', ' ').split()
                idx, field = parts[0], parts[1].replace('[', '').replace(']', '')

                if idx not in questions_data:
                    questions_data[idx] = {}
                questions_data[idx][field] = value

        # Update or create questions
        for idx, q_data in questions_data.items():
            if 'text' in q_data:
                if 'id' in q_data:  # Existing question
                    question = Question.query.get(int(q_data['id']))
                    if question:
                        question.question_text = q_data['text']
                        question.option_a = q_data['option_a']
                        question.option_b = q_data['option_b']
                        question.option_c = q_data['option_c']
                        question.option_d = q_data['option_d']
                        question.correct_answer = q_data['correct']
                        existing_question_ids.add(question.id)
                else:  # New question
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=q_data['text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct']
                    )
                    db.session.add(question)

        db.session.commit()
        flash('Quiz updated successfully!')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating quiz: {str(e)}')

    return redirect(url_for('admin.manage_quiz', chapter_id=quiz.chapter_id))


# User routes
@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    subjects = Subject.query.all()

    # Get user's recent attempts
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id)\
        .order_by(QuizAttempt.completed_at.desc())\
        .limit(5).all()

    # Get subject-wise quiz attempts (for bar chart)
    subject_attempts = db.session.query(
        Subject.name,
        func.count(QuizAttempt.id).label('attempt_count')
    ).select_from(Subject)\
    .join(Chapter)\
    .join(Quiz)\
    .join(QuizAttempt)\
    .filter(QuizAttempt.user_id == current_user.id)\
    .group_by(Subject.name)\
    .all()

    # Prepare data for bar chart
    bar_chart_data = {
        'labels': [s[0] for s in subject_attempts],
        'data': [s[1] for s in subject_attempts]
    }

    # Get monthly quiz attempts (for pie chart)
    if 'sqlite' in str(db.engine.url):
        # SQLite date formatting
        monthly_attempts = db.session.query(
            func.strftime('%Y-%m', QuizAttempt.completed_at).label('month'),
            func.count(QuizAttempt.id).label('attempt_count')
        ).filter(
            QuizAttempt.user_id == current_user.id
        ).group_by('month').all()
    else:
        # PostgreSQL date formatting
        monthly_attempts = db.session.query(
            func.to_char(QuizAttempt.completed_at, 'YYYY-MM').label('month'),
            func.count(QuizAttempt.id).label('attempt_count')
        ).filter(
            QuizAttempt.user_id == current_user.id
        ).group_by('month').all()

    # Prepare data for pie chart
    pie_chart_data = {
        'labels': [datetime.strptime(m[0], '%Y-%m').strftime('%b %Y') for m in monthly_attempts],
        'data': [m[1] for m in monthly_attempts]
    }

    return render_template('user/dashboard.html', 
                         subjects=subjects, 
                         attempts=attempts,
                         bar_chart_data=bar_chart_data,
                         pie_chart_data=pie_chart_data)

@user_bp.route('/quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if datetime.utcnow() < quiz.start_date or datetime.utcnow() > quiz.end_date:
        flash('Quiz is not available at this time')
        return redirect(url_for('user.user_dashboard'))
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
    return redirect(url_for('user.user_dashboard'))

@admin_bp.route('/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {str(e)}')
        return 'Error deleting subject', 500

@admin_bp.route('/chapter/delete/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting chapter: {str(e)}')
        return 'Error deleting chapter', 500

@admin_bp.route('/quiz/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('user.user_dashboard'))

    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully')
        return '', 200
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}')
        return 'Error deleting quiz', 500