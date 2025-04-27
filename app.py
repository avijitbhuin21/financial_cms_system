import os 
from flask import Flask, render_template, request, session, redirect, url_for, jsonify



from static.helper_files.supabase_handler import (
    login as db_login,
    signup as db_signup,
    add_client_to_db,
    add_lead_to_db,
    add_product as db_add_product,
    get_roles_from_supabase,
    get_teams_from_supabase,
    get_all_users, 
    get_tasks_for_user,
    update_task_status,
    add_task as db_add_task,
    add_user_to_db,
    get_sha256_hash,
    select_data
)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24)) 

ROLES = {"OPERATIONS":1,
         "TEAMLEADER":2,
         "RM":3}
TEAMS = {"management":1,
        "operations":2,
        "rm":3}

#-----------------------------------------------------------#
#                       RENDERING ROUTES                    #
#-----------------------------------------------------------#

@app.route('/')
def login_page():
    if 'username' in session:
        return redirect(url_for('home'))
    message = session.pop('error_message', None)  
    return render_template('login.html', message=message)

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    context = {
        'username': session['username'],
        'role': session['role'],
        'team': session['team'],
        'id': str(session.get('id', ''))  
    }
    return render_template('home.html', **context)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

#-----------------------------------------------------------#
#                   LOGIN/SIGNUP ROUTES                     #
#-----------------------------------------------------------#

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles the login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')
    
    check = db_login(username, password) 
    if check.get('status') == True: 
        session['username'] = username
        session['role'] = check['role']
        session['team'] = check['team']
        session['id'] = str(check['id'])  
        session['name'] = check['username']
        print("Session data after login:", dict(session))
        return {"status": True, "role": check['role'], "team": check['team'], "username": username, "id": check['id']}
    else:
        session['error_message'] = "Invalid credentials"
        return {"status": False, "message": "Invalid credentials"}


@app.route('/signup', methods=['POST'])
def handle_signup():
    try:
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({"status": False, "message": "No data provided"})

        required_fields = ['first_name', 'last_name', 'email', 'password', 'phone_number', 'role', 'team']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"status": False, "message": f"Missing required field: {field}"})
        status = db_signup(
            data['first_name'],
            data['last_name'],
            data['email'],
            data['password'],
            data['phone_number'],
            data['role'],
            data['team']
        )

        return jsonify(status)
    except Exception as e:
        print(f"Error in handle_signup: {str(e)}")
        return jsonify({"status": False, "message": "Server error processing request"})
    
#-----------------------------------------------------------#
#                     GENERAL USE ROUTES                    #
#-----------------------------------------------------------#

@app.route('/get-roles', methods=['POST'])
def get_roles():
    
    result = get_roles_from_supabase()
    return jsonify(result)

@app.route('/get-teams', methods=['POST'])
def get_teams():
    
    result = get_teams_from_supabase()
    return jsonify(result)

@app.route('/get-users', methods=['POST'])
def get_users():
    """Endpoint to fetch all users for dropdowns."""
    if 'id' not in session: 
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    ss = data.get('reference', None)
    if ss is not None:
        xx = get_all_users(search_string=ss)
        return jsonify(xx)
   
    roleID = session['role'] 

    print(f"Route /get-users called with roleID: {roleID}")
    
    result = get_all_users(roleID=roleID)  
    result['data'] = result.get('data', []) + [{'username': session['name'], 'id': session['id']}]
    return jsonify(result)

#-----------------------------------------------------------#
#                       ADD CLIENT CARD                     #
#-----------------------------------------------------------#


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
        
        
        result = add_client_to_db(client_data)

        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": result.get('message', 'Database error')})
            
    except Exception as e:
        print(f"Error adding client: {str(e)}")
        return jsonify({"success": False, "message": "Server error"})

#-----------------------------------------------------------#
#                       ADD LEAD CARD                       #
#-----------------------------------------------------------#

@app.route('/add-lead', methods=['POST'])
def add_lead():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401 
    try:
        lead_data = request.json
        print(f"Received lead data: {lead_data}")
        lead_data['leadgenerator'] = lead_data.get('leadgenerator_search', None)
        del lead_data['leadgenerator_search']
        required_fields = ['leadname', 'leadgenerator', 'leadstatus','leadfeedback','leadMOC']
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
            return jsonify({"success": False, "message": db_message}), 500 
            
    except Exception as e:
        return jsonify({"success": False, "message": "Server error processing request"}), 500 

#-----------------------------------------------------------#
#                      ADD PRODUCT CARD                     #
#-----------------------------------------------------------#

@app.route('/add-product', methods=['POST'])
def add_product_route():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401 
    try:
        product_data = request.json
        
        required_fields = ['productid', 'productname']
        for field in required_fields:
            if not product_data.get(field):
                print(f"Missing required product field: {field}")
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400 

        
        
        result = db_add_product(product_data)

        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            db_message = result.get('message', 'Unknown database error')
            print(f"Database error adding product: {db_message}")
            return jsonify({"success": False, "message": db_message}), 500 

    except Exception as e:
        print(f"Error in /add-product route: {str(e)}")
        return jsonify({"success": False, "message": "Server error processing request"}), 500 
    
#-----------------------------------------------------------#
#                      ADD USERS CARD                       #
#-----------------------------------------------------------#

@app.route('/add-users', methods=['POST'])
def add_usrs_route():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    if str(session['role']) != '0':
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    try:
        user_data = request.json
        user_data['roleid'] = ROLES.get(user_data['roleid'], None)
        user_data['teamid'] = TEAMS.get(user_data['teamid'], None)
        user_data['password'] = get_sha256_hash(user_data['password'])

        print(f"Received user data: {user_data}")
        
        required_fields = ['username', 'emailid', 'password', 'roleid', 'teamid', 'mobile']
        for field in required_fields:
            if not user_data.get(field):
                print(f"Missing required user field: {field}")
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400 
        
        # Import the function at the top of the file if not already imported
        result = add_user_to_db(user_data)
        
        if result.get('status', False):
            return jsonify({"success": True})
        else:
            db_message = result.get('message', 'Unknown database error')
            print(f"Database error adding user: {db_message}")
            return jsonify({"success": False, "message": db_message}), 500 

    except Exception as e:
        print(f"Error in /add-users route: {str(e)}")
        return jsonify({"success": False, "message": "Server error processing request"}), 500 

#-----------------------------------------------------------#
#                      ASSIGN TASKS CARD                    #
#-----------------------------------------------------------#

@app.route('/assign-task', methods=['POST'])
def assign_task_route():
    """Handles assigning a new task."""
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        data = request.get_json()
        print(f"Received task assignment data: {data}")

        required_fields = ['task_title', 'task_description', 'due_date', 'assigned_to'] 
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
            
        task_data = {
            'task_title': data['task_title'],
            'task_description': data['task_description'],
            'due_date': data['due_date'],
            'assigned_to': data['assigned_to'], 
            'assigned_by': session['name'], 
            'assigned_by_id': session['id'],
            'assigned_to_name': data['assigned_to_name'],
            'status': 'In Progress' 
        }

        print(f"Task data to be added: {task_data}")
        
        result = db_add_task(task_data)

        if result['success']:
            return jsonify({'success': True, 'message': 'Task assigned successfully!', 'data': result.get('data')})
        else:
            
            return jsonify({'success': False, 'message': result.get('message', 'Failed to assign task')}), 500

    except Exception as e:
        print(f"Error in /assign-task route: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error processing request'}), 500


#-----------------------------------------------------------#
#                  PENDING TASKS SECTION                    #
#-----------------------------------------------------------#
    
@app.route('/get-tasks', methods=['POST'])
def get_tasks():
    """Fetches tasks for the logged-in user."""
    if 'id' not in session:
        print("Error: User ID not found in session during /get-tasks")
        return jsonify({'success': False, 'message': 'User not logged in or session expired'}), 401

    try:
        user_id = session['id']
        print(f"Route /get-tasks called for user_id: {user_id}")

        result = get_tasks_for_user(user_id)
        print(f"Result from get_tasks_for_user: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"!!! Unhandled exception in /get-tasks route: {str(e)}")
        return jsonify({'success': False, 'message': f'Server error fetching tasks: {str(e)}', 'data': []}), 500
    
@app.route('/update-task-status', methods=['POST'])
def update_task_status_route():
    """Updates the status of a task."""
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        task_id = data.get('task_id')
        new_status = data.get('new_status')
        feedback = data.get('feedback') # Get optional feedback
        new_due_date = data.get('new_due_date') # Get optional new due date

        print(f"Received task status update data: {data}")

        if not task_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing task_id or new_status'}), 400
        
        # Pass feedback and new_due_date to the handler function
        result = update_task_status(task_id, new_status, feedback, new_due_date) # Added new_due_date

        if result['success']:
            return jsonify(result)
        else:
            
            if 'not found' in result.get('message', '').lower():
                return jsonify(result), 404 
            else:
                return jsonify(result), 500 

    except Exception as e:
        print(f"Error in /update-task-status route: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error processing request'}), 500

#-----------------------------------------------------------#
#                     TASK LOOKUP CARD                      #
#-----------------------------------------------------------#

@app.route('/task_lookup', methods=['POST'])
def task_lookup_route():
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        task_id = data.get('task_id', None)
        search_string = data.get('search_string', None)

        print(f"Received task lookup data: {data}")

        from static.helper_files.supabase_handler import task_lookup
        
        result = task_lookup(task_id=task_id, search_string=search_string)
        
        if result is None and task_id:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
            
        if isinstance(result, list) and len(result) == 0:
            return jsonify({'success': True, 'data': [], 'message': 'No tasks found'})
        
        print(f"Task lookup result: {result}")
            
        return jsonify({'success': True, 'data': result})

    except Exception as e:
        print(f"Error in task lookup: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error processing request'}), 500
























if __name__ == '__main__':
    
    port = int(os.environ.get('PORT', 5005))
    app.run(debug=True, host='0.0.0.0', port=port) 