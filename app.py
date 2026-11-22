from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import uuid
import os
from flask_babel import Babel

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.secret_key = 'raic_uqu_secret_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

babel = Babel(app)
db = SQLAlchemy(app)
ADMIN_PASSWORD = 'raic2026'

# ── Models ────────────────────────────────────────────────────────────────────

class Member(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    full_name    = db.Column(db.String(120), nullable=False)
    student_id   = db.Column(db.String(20),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    major        = db.Column(db.String(100), nullable=False)
    year         = db.Column(db.String(20),  nullable=False)
    interest     = db.Column(db.String(100), nullable=False)
    points       = db.Column(db.Integer,     default=0)
    badge        = db.Column(db.String(50),  default='Newcomer')
    joined_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    attended     = db.Column(db.Integer,     default=0)

    def __str__(self):
        return self.full_name

class Event(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        nullable=False)
    event_type  = db.Column(db.String(50),  nullable=False)
    date        = db.Column(db.String(50),  nullable=False)
    time        = db.Column(db.String(20),  nullable=False)
    location    = db.Column(db.String(100), nullable=False)
    points      = db.Column(db.Integer,     default=10)
    capacity    = db.Column(db.Integer,     default=50)
    registered  = db.Column(db.Integer,     default=0)

    def __str__(self):
        return self.title

class Feedback(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    category   = db.Column(db.String(50),  nullable=False)
    message    = db.Column(db.Text,        nullable=False)
    rating     = db.Column(db.Integer,     nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

    def __str__(self):
        return f'{self.name} - {self.rating}/5'

class PageView(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    page       = db.Column(db.String(100), nullable=False)
    timestamp  = db.Column(db.DateTime,    default=datetime.utcnow)
    referrer   = db.Column(db.String(200))
    session_id = db.Column(db.String(64))
    duration   = db.Column(db.Integer)

class Goal(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    goal_name  = db.Column(db.String(100), nullable=False)
    page       = db.Column(db.String(100))
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(64))

class Achievement(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        nullable=False)
    image       = db.Column(db.String(200))

    def __str__(self):
        return self.title

# ── Admin setup ───────────────────────────────────────────────────────────────

class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in') == True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

admin = Admin(app, name='RAIC Admin')
admin.add_view(SecureModelView(Member,      db.session, name='Members'))
admin.add_view(SecureModelView(Event,       db.session, name='Events'))
admin.add_view(SecureModelView(Feedback,    db.session, name='Feedback'))
admin.add_view(SecureModelView(Achievement, db.session, name='Achievements'))

# ── Helpers ───────────────────────────────────────────────────────────────────

REGISTRATION_OPEN = True

def calc_badge(points):
    if points >= 200: return 'AI Master'
    if points >= 100: return 'Bot Builder'
    if points >=  50: return 'Circuit Breaker'
    if points >=  20: return 'Data Spark'
    return 'Newcomer'

def seed_events():
    if Event.query.count() == 0:
        sample = [
            Event(title='MRC World Robotics Competition - Greece',
                  description='Team UQUxRAIC competed in the MRC World Robotics Competition in Greece, winning 1st place (Gold) in the Football track 18+, and 2nd place (Silver) in the Marathon track.',
                  event_type='competition', date='2026-04-11', time='9:00 AM',
                  location='Greece - International', points=50, capacity=200, registered=12),
            Event(title='Workshop: Circuit Soldering Basics',
                  description='A hands-on workshop covering the fundamentals of circuit soldering for building tech innovations.',
                  event_type='workshop', date='2026-04-22', time='12:30 PM',
                  location='Activities Building', points=20, capacity=30, registered=28),
            Event(title='Talk: Can Programming Create Consciousness?',
                  description='A deep philosophical and technical journey exploring the limits of AI and machine awareness.',
                  event_type='talk', date='2026-05-04', time='7:00 PM',
                  location='Microsoft Teams', points=15, capacity=300, registered=87),
            Event(title='Artathon Camp - Creativity and Entrepreneurship',
                  description='A camp aimed at developing design skills combining AI tools and creative vision.',
                  event_type='workshop', date='2026-05-15', time='10:00 AM',
                  location='UQU Campus', points=30, capacity=50, registered=45),
            Event(title='Oracle Partnership - Mostaqbali Initiative',
                  description='Guidance session covering 18+ certified professional courses in AI, Data, and Cloud.',
                  event_type='talk', date='2026-03-29', time='8:30 PM',
                  location='Microsoft Teams', points=15, capacity=200, registered=134),
            Event(title='Success Story: Team Ofok from Innovation to Orbit',
                  description='Inspiring session showcasing Team Ofok journey in the SARI competition and Geneva Inventions Exhibition.',
                  event_type='meeting', date='2026-03-31', time='7:45 PM',
                  location='Microsoft Teams', points=10, capacity=300, registered=76),
        ]
        db.session.add_all(sample)
        db.session.commit()

def seed_achievements():
    if Achievement.query.count() == 0:
        sample = [
            Achievement(
                title='1st Place, MRC World Robotics Competition (Greece 2026)',
                description='Gold medal in the Football track (18+) as team UQUxRAIC, representing UQU and Saudi Arabia internationally.'
            ),
            Achievement(
                title='2nd Place, Marathon Track (MRC Greece 2026)',
                description='Silver medal in the advanced marathon track (+18).'
            ),
            Achievement(
                title='2nd Place, Rally Track (MRC Greece 2026)',
                description='Silver medal in the rally for advancement track. Three medals in one competition.'
            ),
            Achievement(
                title='UQU Excellence Award, 1st Place',
                description='Club President Eng. Ahmed Al-Masri ranked 1st in the Learning and Education track (Bachelor/Diploma category).'
            ),
            Achievement(
                title='Geneva International Inventions Exhibition, SARI Competition',
                description='Team Ofok, from a simple idea to an international stage.'
            ),
            Achievement(
                title='Oracle Partnership, Mostaqbali Initiative',
                description='Guidance sessions covering 18+ certified professional courses in AI, Data Science, and Cloud Computing.'
            ),
            Achievement(
                title='Global Robotics Challenge (GRC) - Top 3 Worldwide',
                description='RAIC represented UQU at the Global Robotics Challenge (GRC) and achieved an unprecedented result by winning the top 3 places worldwide in the Line Racer Adult category, in addition to the Best Coding Award.'
            ),
        ]
        db.session.add_all(sample)
        db.session.commit()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db.session.add(PageView(page='home', referrer=request.referrer))
    db.session.commit()
    events  = Event.query.order_by(Event.date).limit(3).all()
    members = Member.query.count()
    return render_template('index.html', events=events,
                           members=members, reg_open=REGISTRATION_OPEN)

@app.route('/events')
def events():
    db.session.add(PageView(page='events', referrer=request.referrer))
    db.session.commit()
    all_events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=all_events)

@app.route('/register', methods=['GET', 'POST'])
def register():
    db.session.add(PageView(page='register', referrer=request.referrer))
    db.session.commit()
    if not REGISTRATION_OPEN:
        return render_template('register.html', reg_open=False)
    if request.method == 'POST':
        data = request.get_json()
        errors = {}
        if not data.get('full_name','').strip():
            errors['full_name'] = 'Name is required.'
        if not data.get('student_id','').strip():
            errors['student_id'] = 'Student ID is required.'
        if not data.get('email','').strip() or '@' not in data.get('email',''):
            errors['email'] = 'Valid email is required.'
        if Member.query.filter_by(student_id=data.get('student_id')).first():
            errors['student_id'] = 'Student ID already registered.'
        if Member.query.filter_by(email=data.get('email')).first():
            errors['email'] = 'Email already registered.'
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        m = Member(
            full_name  = data['full_name'].strip(),
            student_id = data['student_id'].strip(),
            email      = data['email'].strip(),
            major      = data.get('major','').strip(),
            year       = data.get('year','').strip(),
            interest   = data.get('interest','').strip(),
            points     = 10,
        )
        m.badge = calc_badge(m.points)
        db.session.add(m)
        db.session.commit()
        return jsonify({'success': True,
                        'message': f'Welcome to RAIC, {m.full_name}! You earned 10 welcome points!'})
    return render_template('register.html', reg_open=True)

@app.route('/leaderboard')
def leaderboard():
    db.session.add(PageView(page='leaderboard', referrer=request.referrer))
    db.session.commit()
    top = Member.query.order_by(Member.points.desc()).limit(20).all()
    return render_template('leaderboard.html', members=top)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    db.session.add(PageView(page='feedback', referrer=request.referrer))
    db.session.commit()
    if request.method == 'POST':
        data = request.get_json()
        errors = {}
        if not data.get('name','').strip():    errors['name']    = 'Name required.'
        if not data.get('email','').strip():   errors['email']   = 'Email required.'
        if not data.get('message','').strip(): errors['message'] = 'Message required.'
        if not data.get('rating'):             errors['rating']  = 'Rating required.'
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400
        f = Feedback(
            name     = data['name'].strip(),
            email    = data['email'].strip(),
            category = data.get('category','General'),
            message  = data['message'].strip(),
            rating   = int(data['rating']),
        )
        db.session.add(f)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
    return render_template('feedback.html')

@app.route('/achievements')
def achievements():
    db.session.add(PageView(page='achievements', referrer=request.referrer))
    db.session.commit()
    items = Achievement.query.all()
    return render_template('achievements.html', achievements=items)

@app.route('/api/track_duration', methods=['POST'])
def track_duration():
    data = request.get_json()
    sid  = request.cookies.get('raic_sid', '')
    pv   = PageView.query.filter_by(session_id=sid, page=data.get('page','')) \
               .order_by(PageView.id.desc()).first()
    if pv and data.get('seconds'):
        pv.duration = int(data['seconds'])
        db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/track_goal', methods=['POST'])
def track_goal():
    data = request.get_json()
    g = Goal(
        goal_name  = data.get('goal','unknown'),
        page       = data.get('page', request.referrer or ''),
        session_id = request.cookies.get('raic_sid',''),
    )
    db.session.add(g)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/analytics')
def analytics():
    from sqlalchemy import func
    page_counts         = db.session.query(PageView.page, func.count(PageView.id)).group_by(PageView.page).all()
    feedback_avg        = db.session.query(func.avg(Feedback.rating)).scalar() or 0
    members_by_interest = db.session.query(Member.interest, func.count(Member.id)).group_by(Member.interest).all()
    members_by_year     = db.session.query(Member.year, func.count(Member.id)).group_by(Member.year).all()
    all_sessions        = db.session.query(PageView.session_id).filter(PageView.session_id != None).distinct().count()
    single_sessions     = db.session.query(PageView.session_id).filter(PageView.session_id != None).group_by(PageView.session_id).having(func.count(PageView.id) == 1).count()
    bounce_rate         = round((single_sessions / all_sessions * 100), 1) if all_sessions else 0
    avg_duration        = db.session.query(func.avg(PageView.duration)).filter(PageView.duration != None).scalar() or 0
    goal_counts         = db.session.query(Goal.goal_name, func.count(Goal.id)).group_by(Goal.goal_name).all()
    return jsonify({
        'total_members':  Member.query.count(),
        'total_feedback': Feedback.query.count(),
        'avg_rating':     round(float(feedback_avg), 2),
        'page_views':     {p: c for p, c in page_counts},
        'by_interest':    {i: c for i, c in members_by_interest},
        'by_year':        {y: c for y, c in members_by_year},
        'top_members':    [{'name': m.full_name, 'points': m.points, 'badge': calc_badge(m.points)}
                           for m in Member.query.order_by(Member.points.desc()).limit(5).all()],
        'bounce_rate':    bounce_rate,
        'avg_duration':   round(float(avg_duration), 1),
        'goals':          {g: c for g, c in goal_counts},
    })

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        error = 'Wrong password. Try again.'
    return render_template('admin_login.html', error=error)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_events()
        seed_achievements()
    app.run(debug=True)
