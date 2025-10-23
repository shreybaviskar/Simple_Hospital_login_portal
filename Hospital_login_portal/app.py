from flask import Flask, render_template, request, redirect, session, url_for
import os

app = Flask(__name__)
app.secret_key = 'secretkey_v5'

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory user store
users = []

@app.route('/')
def home():
    return redirect(url_for('signup'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form

        # Password match check
        if data.get('password') != data.get('confirm_password'):
            return render_template('signup.html', error="Passwords do not match!")

        # Age validation
        try:
            age = int(data.get('age') or 0)
            if age < 0:
                return render_template('signup.html', error="Age cannot be negative!")
        except ValueError:
            return render_template('signup.html', error="Invalid age!")

        # Handle profile picture upload
        upload_file = request.files.get('profile_picture')
        if upload_file and upload_file.filename != "":
            filename = upload_file.filename.replace(" ", "_")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            upload_file.save(save_path)
            profile_picture = f"uploads/{filename}"
        else:
            profile_picture = "default_profile.png"

        # Base user data
        user = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'username': data.get('username'),
            'email': data.get('email'),
            'password': data.get('password'),
            'address_line1': data.get('address_line1'),
            'city': data.get('city'),
            'state': data.get('state'),
            'pincode': data.get('pincode'),
            'role': data.get('role'),
            'profile_picture': profile_picture
        }

        # Role-specific fields
        if data.get('role') == 'Patient':
            user.update({
                'age': age,
                'gender': data.get('gender'),
                'blood_group': data.get('blood_group')
            })
        else:
            user.update({
                'specialization': data.get('specialization'),
                'experience': data.get('experience'),
                'clinic': data.get('clinic')
            })

        users.append(user)
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            session['user'] = user
            if user['role'] == 'Patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('doctor_dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password!")
    return render_template('login.html')

@app.route('/patient_dashboard')
def patient_dashboard():
    user = session.get('user')
    if not user or user.get('role') != 'Patient':
        return redirect(url_for('login'))
    return render_template('patient_dashboard.html', user=user)

@app.route('/doctor_dashboard')
def doctor_dashboard():
    user = session.get('user')
    if not user or user.get('role') != 'Doctor':
        return redirect(url_for('login'))
    return render_template('doctor_dashboard.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
