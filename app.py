from flask import Flask, render_template, request, session, redirect, url_for, jsonify

#LOCAL IMPORTS
from static.helper_files.supabase_handler import *

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'


@app.route('/')
def login_page():
    if 'username' in session:
        return redirect(url_for('home'))
    message = session.pop('error_message', None)  # Get and remove message from session
    return render_template('login.html', message=message)

@app.route('/home')
def home():
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
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/add-client', methods=['POST'])
def add_client():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    
    try:
        client_data = request.json

        required_fields = ['name', 'emailid', 'mobile', 'pan']
        for field in required_fields:
            if not client_data.get(field):
                return jsonify({"success": False, "message": f"Missing required field: {field}"})
        
        from static.helper_files.supabase_handler import add_client_to_db
        result = add_client_to_db(client_data)
        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": result.get('message', 'Database error')})
            
    except Exception as e:
        print(f"Error adding client: {str(e)}")
        return jsonify({"success": False, "message": "Server error"})


@app.route('/add-lead', methods=['POST'])
def add_lead():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401 # Unauthorized
    try:
        lead_data = request.json
        required_fields = ['leadname', 'leadgenerator', 'leadstatus']
        for field in required_fields:
            if not lead_data.get(field):
                print(f"Missing required lead field: {field}")
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        result = add_lead_to_db(lead_data)
        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            db_message = result.get('message', 'Unknown database error')
            print(f"Database error adding lead: {db_message}")
            return jsonify({"success": False, "message": db_message}), 500 # Internal Server Error
            
    except Exception as e:
        return jsonify({"success": False, "message": "Server error processing request"}), 500 # Internal Server Error


@app.route('/add-product', methods=['POST'])
def add_product_route():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401 # Unauthorized
    try:
        product_data = request.json
        # Ensure required fields based on DB schema and form are present
        required_fields = ['productid', 'productname']
        for field in required_fields:
            if not product_data.get(field):
                print(f"Missing required product field: {field}")
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400 # Bad Request

        # Call the handler function (already imported)
        result = add_product(product_data)

        if result.get('status', False):
            return jsonify({"success": True})
        else:
            db_message = result.get('message', 'Unknown database error')
            print(f"Database error adding product: {db_message}")
            return jsonify({"success": False, "message": db_message}), 500 # Internal Server Error

    except Exception as e:
        print(f"Error in /add-product route: {str(e)}")
        return jsonify({"success": False, "message": "Server error processing request"}), 500 # Internal Server Error

@app.route('/get-roles', methods=['POST'])
def get_roles():
    return jsonify({"success": True, "data": get_roles_from_supabase()})

@app.route('/get-teams', methods=['POST'])
def get_teams():
    data = [i['teamname'] for i in select_data("Teams")]
    return jsonify({"success": True, "data": data})

if __name__ == '__main__':
    app.run(debug=True, port=5005)