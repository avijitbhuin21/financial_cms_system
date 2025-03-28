from flask import Flask, render_template, request, session, redirect, url_for

#LOCAL IMPORTS
from static.helper_files.supabase_handler import login, signup


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'


@app.route('/')
def login_page():
    """Renders the login page."""
    message = session.pop('error_message', None)  # Get and remove message from session
    return render_template('login.html', message=message)

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles the login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    check = login(username, password)
    if check['status'] == True:
        return {"status": True, "role": check['role'], "team": check['team'], "username": username}
    else:
        session['error_message'] = "Invalid credentials"
        return {"status": False, "message": "Invalid credentials"}


@app.route('/signup', methods=['POST'])
def handle_signup():
    """Handles the signup form submission."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    roleid = request.form.get('roleid')
    teamid = request.form.get('teamid')

    status = signup(first_name, last_name, email, password, phone_number, roleid, teamid)
    if status['status'] == True:
        return {"status": True}
    else:
        return {"status": False, "message": status['message']}

if __name__ == '__main__':
    app.run(debug=True)