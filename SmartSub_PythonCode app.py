from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import math
import uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# In-Memory Database
class Database:
    def __init__(self):
        self.users = []
        self.teachers = []
        self.substitutes = []
        self.absences = []
        self.cover_plans = []
        
        # Add sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        # Sample admin user
        admin_id = str(uuid.uuid4())
        self.users.append({
            'id': admin_id,
            'name': 'Admin',
            'surname': 'User',
            'email': 'admin@school.edu',
            'password_hash': generate_password_hash('admin123'),
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.now(),
            'last_login': None
        })
        
        # Sample teacher
        teacher_id = str(uuid.uuid4())
        self.users.append({
            'id': teacher_id,
            'name': 'John',
            'surname': 'Smith',
            'email': 'jsmith@school.edu',
            'password_hash': generate_password_hash('teacher123'),
            'role': 'teacher',
            'is_active': True,
            'created_at': datetime.now(),
            'last_login': None
        })
        self.teachers.append({
            'id': str(uuid.uuid4()),
            'user_id': teacher_id,
            'subjects': ['Mathematics', 'Advanced Calculus'],
            'schedule': {
                'Monday': [{'period': '1-2', 'class': 'Grade 11 Math'}],
                'Tuesday': [{'period': '3-4', 'class': 'Grade 12 Calculus'}],
                'Wednesday': [{'period': '2-3', 'class': 'Grade 10 Math'}]
            },
            'contact_number': '+1234567890',
            'profile_picture': None,
            'is_absent': False
        })
        
        # Sample substitutes
        self.substitutes.append({
            'id': str(uuid.uuid4()),
            'name': 'Mr. Davis',
            'email': 'davis@example.com',
            'phone': '+1234567892',
            'subjects': ['Mathematics', 'Physics'],
            'address': '123 School St, City',
            'latitude': 34.052235,
            'longitude': -118.243683,
            'is_available': True,
            'rating': 4.5,
            'max_distance': 20
        })

db = Database()

# Helper functions
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) * math.sin(dlat/2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        
        user = next((u for u in db.users if u['id'] == session['user_id']), None)
        if not user or user['role'] not in ['admin', 'principal', 'hod']:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = next((u for u in db.users if u['email'] == email), None)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            user['last_login'] = datetime.now()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template_string('''
        <!-- Your login form HTML here -->
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        
        # Validate password
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        # Check if email exists
        if any(u['email'] == email for u in db.users):
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        # Create user
        user = {
            'id': str(uuid.uuid4()),
            'name': name,
            'surname': surname,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': 'teacher',
            'is_active': True,
            'created_at': datetime.now(),
            'last_login': None
        }
        db.users.append(user)
        
        # Create teacher profile
        teacher = {
            'id': str(uuid.uuid4()),
            'user_id': user['id'],
            'subjects': [],
            'schedule': {},
            'contact_number': '',
            'profile_picture': None,
            'is_absent': False
        }
        db.teachers.append(teacher)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template_string('''
        <!-- Your registration form HTML here -->
    ''')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get stats for dashboard
    absent_teachers = sum(1 for t in db.teachers if t['is_absent'])
    pending_covers = sum(1 for c in db.cover_plans if c['status'] == 'draft')
    available_subs = sum(1 for s in db.substitutes if s['is_available'])
    
    # Get today's absences
    today = datetime.now().date()
    absences = [
        a for a in db.absences
        if datetime.strptime(a['start_date'], '%Y-%m-%d').date() <= today <= datetime.strptime(a['end_date'], '%Y-%m-%d').date()
    ]
    
    return render_template_string('''
        <!-- Your dashboard HTML here -->
    ''', absent_teachers=absent_teachers, pending_covers=pending_covers, 
        available_subs=available_subs, absences=absences)

@app.route('/teachers')
@login_required
def teachers():
    teachers = []
    for teacher in db.teachers:
        user = next((u for u in db.users if u['id'] == teacher['user_id']), None)
        if user:
            teachers.append({
                'name': f"{user['name']} {user['surname']}",
                'subjects': teacher['subjects'],
                'schedule': teacher['schedule']
            })
    
    return render_template_string('''
        <!-- Your teachers HTML here -->
    ''', teachers=teachers)

@app.route('/substitutes')
@login_required
def substitutes():
    subject_filter = request.args.get('subject', '')
    distance_filter = int(request.args.get('distance', 20))
    
    school_lat = 34.052235
    school_lon = -118.243683
    
    filtered_subs = []
    for sub in db.substitutes:
        if sub['is_available']:
            # Subject filter
            if subject_filter and subject_filter not in sub['subjects']:
                continue
                
            # Distance filter
            if sub['latitude'] and sub['longitude']:
                distance = calculate_distance(
                    school_lat, school_lon,
                    sub['latitude'], sub['longitude']
                )
                if distance <= distance_filter:
                    sub_copy = dict(sub)
                    sub_copy['distance'] = round(distance, 1)
                    filtered_subs.append(sub_copy)
    
    filtered_subs.sort(key=lambda x: x['distance'])
    
    return render_template_string('''
        <!-- Your substitutes HTML here -->
    ''', substitutes=filtered_subs, subject_filter=subject_filter, 
        distance_filter=distance_filter)

@app.route('/reports')
@login_required
def reports():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department', '')
    
    report_data = []
    subjects = ['Mathematics', 'Science', 'English', 'History']
    absences_data = [12, 8, 5, 3]  # Sample data
    
    return render_template_string('''
        <!-- Your reports HTML here -->
    ''', report_data=report_data, subjects=subjects, 
        absences_data=absences_data, start_date=start_date,
        end_date=end_date, department=department)

# API Endpoints
@app.route('/api/mark_absent/<teacher_id>', methods=['POST'])
@admin_required
def mark_absent(teacher_id):
    teacher = next((t for t in db.teachers if t['id'] == teacher_id), None)
    if not teacher:
        return jsonify({'error': 'Teacher not found'}), 404
    
    teacher['is_absent'] = True
    
    # Create absence record
    absence = {
        'id': str(uuid.uuid4()),
        'teacher_id': teacher_id,
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d'),
        'is_emergency': False,
        'reason': '',
        'created_by': session['user_id'],
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    db.absences.append(absence)
    
    return jsonify({'success': True})

@app.route('/api/assign_substitute', methods=['POST'])
@admin_required
def assign_substitute():
    data = request.get_json()
    
    cover_plan = {
        'id': str(uuid.uuid4()),
        'absence_id': data['absence_id'],
        'substitute_id': data['substitute_id'],
        'lesson_outline': '',
        'resource_links': [],
        'status': 'approved',
        'created_by': session['user_id'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'sent_at': None,
        'completed_at': None
    }
    db.cover_plans.append(cover_plan)
    
    # Update absence status
    absence = next((a for a in db.absences if a['id'] == data['absence_id']), None)
    if absence:
        absence['status'] = 'covered'
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)