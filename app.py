from flask import Flask, render_template, request, session, redirect, url_for, jsonify

#LOCAL IMPORTS
from static.helper_files.supabase_handler import login, signup


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'


@app.route('/')
def login_page():
    """Renders the login page."""
    if 'username' in session:
        return redirect(url_for('home'))
    message = session.pop('error_message', None)  # Get and remove message from session
    return render_template('login.html', message=message)

@app.route('/home')
def home():
    """Renders the home page."""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('home.html', 
                          username=session['username'], 
                          role=session['role'],
                          team=session['team'])

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles the login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    check = login(username, password)
    if check['status'] == True:
        session['username'] = username
        session['role'] = check['role']
        session['team'] = check['team']
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
    roleid = request.form.get('role')
    teamid = request.form.get('team')

    status = signup(first_name, last_name, email, password, phone_number, roleid, teamid)
    if status['status'] == True:
        return {"status": True}
    else:
        return {"status": False, "message": status['message']}

@app.route('/logout')
def logout():
    """Handles user logout."""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/add-client', methods=['POST'])
def add_client():
    """Handles adding a new client to the database."""
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    
    try:
        # --- DEBUG LOGGING START ---
        print(f"--- Request Headers ---")
        print(request.headers)
        print(f"--- Request Raw Data ---")
        print(request.data) # Log raw data bytes
        print(f"--- Attempting request.json ---")
        # --- DEBUG LOGGING END ---

        # Get client data from request
        client_data = request.json # This line will likely fail if Content-Type is wrong

        # Basic validation
        required_fields = ['name', 'emailid', 'mobile', 'pan']
        for field in required_fields:
            if not client_data.get(field):
                return jsonify({"success": False, "message": f"Missing required field: {field}"})
        
        # Here you would add your Supabase code to insert into the clients table
        # For example:
        # from supabase import create_client
        # supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # result = supabase.table('clients').insert(client_data).execute()
        
        # This is a placeholder - replace with your actual Supabase code
        # Assuming you have a function in your supabase_handler.py like:
        from static.helper_files.supabase_handler import add_client_to_db
        result = add_client_to_db(client_data)
        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": result.get('message', 'Database error')})
            
    except Exception as e:
        print(f"Error adding client: {str(e)}")
        return jsonify({"success": False, "message": "Server error"})

if __name__ == '__main__':
    app.run(debug=True, port=5005)