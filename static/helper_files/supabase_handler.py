import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import hashlib
from typing import Optional, Dict, Any, List, Union
from datetime import datetime


# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

# ---------------------------------------------------------------------------- #
#                                  Base Functions                              #
# ---------------------------------------------------------------------------- #

def select_data(
    table: str,
    query_params: Optional[Dict[str, Union[Any, List[Any]]]] = None,
    Except_params: Optional[Dict[str, Union[Any, List[Any]]]] = None,
    required_params: str = "*",
) -> List[Dict[str, Any]]:
    try:
        query = supabase.table(table).select(required_params)

        if query_params:
            for key, value in query_params.items():
                if isinstance(value, list):
                    query = query.in_(key, value)
                else:
                    query = query.eq(key, value)

        if Except_params:
            for key, value in Except_params.items():
                if isinstance(value, list):
                    query = query.not_.in_(key, value)
                else:
                    query = query.neq(key, value)

        response = query.execute()
        return response.data
    except Exception as e:
        raise Exception(f"Error selecting data from {table}: {str(e)}")

def insert_data(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = supabase.table(table).insert(data).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        raise Exception(f"Error inserting data into {table}: {str(e)}")

def update_data(table: str, match_criteria: Dict[str, Any], new_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        # Use the match method which takes the entire match_criteria dictionary at once
        response = supabase.table(table).update(new_data).match(match_criteria).execute()
        return response.data[0]
    except Exception as e:
        raise Exception(f"Error updating data in {table}: {str(e)}")

def delete_data(table: str, match_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        # Use the match method which takes the entire match_criteria dictionary at once
        response = supabase.table(table).delete().match(match_criteria).execute()
        return response.data[0]
    except Exception as e:
        raise Exception(f"Error deleting data from {table}: {str(e)}")
    
def _process_and_deduplicate_tasks(results, limit_count):
    if not results:
        return []

    processed_ids = set()
    final_task_list = []
    for task in results:
        task_id = task.get('task_id')
        if task_id and task_id not in processed_ids:
            final_task_list.append({
                "task_id": task_id,
                "task_title": task.get('task_title'),
                "task_description": task.get('task_description')
            })
            processed_ids.add(task_id)
            if len(final_task_list) == limit_count:
                break
    return final_task_list

# ---------------------------------------------------------------------------- #
#                            Encryption Functions                              #
# ---------------------------------------------------------------------------- #
def get_sha256_hash(text):
    if isinstance(text, str):
        text = text.encode('utf-8')
    hash_object = hashlib.sha256(text)
    return hash_object.hexdigest()

#-----------------------------------------------------------#
#                 GENERALLY USED FUNCTION                   #
#-----------------------------------------------------------#

def get_roles_from_supabase():
    try:
        response = supabase.table('Roles').select('rolename').execute()
        if response.data:
            roles = [item['rolename'] for item in response.data if item['rolename'] != 'ADMIN']
            return {'success': True, 'data': roles}
        else:
            return {'success': True, 'data': []}
    except Exception as e:
        print(f"Error fetching roles: {e}")
        return {'success': False, 'message': str(e), 'data': []}

def get_teams_from_supabase():
    try:
        response = supabase.table('Teams').select('teamname').execute()
        if response.data:
            teams = [item['teamname'] for item in response.data]
            return {'success': True, 'data': teams}
        else:
            return {'success': True, 'data': []}
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return {'success': False, 'message': str(e), 'data': []}

def get_all_users(roleID: Optional[int] = None, search_string: str =None) -> Dict[str, Any]:
    """Fetches user IDs and usernames from the users table."""
    try:
        if roleID is not None:
            # Select only id and username
            query = supabase.table('Users').select('username','id')
            if roleID is not None:
                query = query.gt('roleid', roleID)
            response = query.execute()
            print(f"Supabase get_all_users response: {response}")
            if response.data:
                # Return data in the format expected by the frontend (list of dicts)
                return {'success': True, 'data': response.data}
            else:
                # Handle cases where the query runs but returns no data
                return {'success': True, 'data': []}
        if search_string is not None:
            query = supabase.table("Users") \
                        .select("username, id")

            query = query.ilike('username', f'%{search_string}%')
            fetch_limit = 10

            response = query.limit(fetch_limit).execute()
            return {'success': True, 'data': response.data}
    except Exception as e:
        print(f"Unexpected error fetching users: {e}")
        return {'success': False, 'message': f"An unexpected error occurred: {str(e)}", 'data': []}
    
#-----------------------------------------------------------#
#                   LOGIN/SIGNUP FUNCTION                   #
#-----------------------------------------------------------#

def login(email, password):
    database_data = select_data("Users", {"emailid": email, "password": get_sha256_hash(password)})
    if database_data != []:
        user_id = database_data[0]['id']
        print("Login Debug - Database ID:", {
            'raw_id': user_id,
            'type': type(user_id).__name__,
            'str_value': str(user_id)
        })
        return {
            "status": True,
            "role": database_data[0]['roleid'],
            "team": database_data[0]['teamid'],
            "id": str(user_id),
              "username": database_data[0]['username']  # Convert to string for consistency
        }
    
    else:
        return {"status": False, "role": None, "team": None}
    
def signup(first_name, last_name, email, password, phone_number, roleid, teamid):
    roleid = select_data("Roles", {"rolename": roleid})[0]['roleid']
    teamid = select_data("Teams", {"teamname": teamid})[0]['teamid']
    try:
        data = {
            "username": first_name + " " + last_name,
            "emailid": email,
            "password": get_sha256_hash(password),
            "mobile": phone_number,
            "roleid": roleid,
            "teamid": teamid,
        }
        insert_data("Users", data)
        return {"status": True}
    except Exception as e:
        return {"status": False, "message": str(e)}
    
def add_client_to_db(client_data):
    try:
        response = insert_data("clients", client_data)
        if response: 
            return {"status": True, "data": response}
        else:
            return {"status": False, "message": "Failed to add client or no data returned."}
            
    except Exception as e:
        print(f"Error in add_client_to_db: {str(e)}")
        return {"status": False, "message": str(e)}

#-----------------------------------------------------------#
#                   LEAD RELATED FUNCTION                   #
#-----------------------------------------------------------#

def add_lead_to_db(lead_data):
    """
    Inserts lead data into the leads table.
    Expects leadgenerator and leadconverter to be dictionaries like {"username": "...", "id": ...}.
    Extracts the username string for storage in the text columns.
    Maps frontend keys to correct column names.
    """
    try:
        # Extract usernames from the potentially nested dictionary structure
        generator_data = lead_data.get("leadgenerator")
        converter_data = lead_data.get("leadconverter") # Optional

        generator_username = generator_data.get("username") if isinstance(generator_data, dict) else generator_data
        converter_username = converter_data.get("username") if isinstance(converter_data, dict) else converter_data

        # Map frontend keys to Supabase column names, using extracted usernames
        supabase_lead_data = {
            "leadname": lead_data.get("leadname"),
            "leadgenerator": generator_username, # Store username string
            "leadconverter": converter_username, # Store username string (optional)
            "leadstatus": lead_data.get("leadstatus"),
            "leadFeedback": lead_data.get("leadfeedback"), # Map leadfeedback to "leadFeedback"
            "leadMOC": lead_data.get("leadMOC")             # Map leadMOC to "leadMOC"
        }

        # Remove keys with None values to avoid inserting nulls explicitly unless intended
        supabase_lead_data = {k: v for k, v in supabase_lead_data.items() if v is not None}

        print(f"Inserting lead data into Supabase: {supabase_lead_data}") # Log data being inserted

        # Use the generic insert_data function with the prepared data
        response = insert_data("leads", supabase_lead_data)

        # Check if the insertion was successful
        if response:
            return {"status": True, "data": response}
        else:
            return {"status": False, "message": "Failed to add lead or no data returned."}

    except Exception as e:
        print(f"Error in add_lead_to_db: {str(e)}")
        # Check for specific Supabase errors if possible, e.g., constraint violations
        error_message = str(e)
        if "duplicate key value violates unique constraint" in error_message:
             return {"status": False, "message": "A lead with similar details might already exist."}
        # Add more specific error handling if needed
        return {"status": False, "message": f"Database error: {error_message}"}
    
#-----------------------------------------------------------#
#                 PRODUCT RELATED FUNCTION                  #
#-----------------------------------------------------------#

def add_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = insert_data("products", product_data)
        if response: 
            return {"status": True, "data": response}
        else:
            return {"status": False, "message": "Failed to add product or no data returned."}

    except Exception as e:
        print(f"Error in add_product: {str(e)}") # Log the specific error
        return {"status": False, "message": str(e)}
    
#-----------------------------------------------------------#
#                   USER RELATED FUNCTION                   #
#-----------------------------------------------------------#

def add_user_to_db(user_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        response = insert_data("Users", user_data)
        if response: 
            return {"status": True, "data": response}
        else:
            return {"status": False, "message": "Failed to add user or no data returned."}

    except Exception as e:
        print(f"Error in add_user_to_db: {str(e)}") # Log the specific error
        return {"status": False, "message": str(e)}



# ---------------------------------------------------------------------------- #
#                                  Task Functions                              #
# ---------------------------------------------------------------------------- #


def get_tasks_for_user(user_id: str) -> Dict[str, Any]:
    """Fetches tasks assigned to a specific user ID."""
    try:
        data = select_data("Tasks", query_params={"assigned_to": user_id}, Except_params={"status": ["Completed","pending approval"]}) + select_data("Tasks", query_params={"assigned_by_id": user_id, "status": "pending approval"})

        print(data)
        return {'success': True, 'data': data} if data != [] else {'success': False, 'data': []}
    except Exception as e:
        print(f"Unexpected error fetching tasks: {e}")
        return {'success': False, 'message': f"An unexpected error occurred: {str(e)}", 'data': []}

def add_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Inserts a new task into the tasks table."""
    try:
        print(f"Adding task: {task_data}")
        # Ensure required fields are present (add more checks as needed)
        required_fields = ['task_title', 'task_description', 'due_date', 'assigned_to', 'assigned_by', 'assigned_by_id', 'assigned_to_name']
        for field in required_fields:
            if field not in task_data or not task_data[field]:
                return {'success': False, 'message': f'Missing required field: {field}'}

        # Add default status if not provided
        if 'status' not in task_data:
            task_data['status'] = 'In Progress' # Or your default status

        response = insert_data("Tasks", task_data)
        del response['created_at']
        response = insert_data("Tasks_tracking", response)
        print(f"Supabase add_task response: {response}")

        return {'success': True}

    except Exception as e:
        print(f"Unexpected error adding task: {e}")
        return {'success': False, 'message': f"An unexpected error occurred: {str(e)}"}

# Add new_due_date parameter to the function signature
def update_task_status(task_id: str, new_status: str, feedback: Optional[str] = None, new_due_date: Optional[str] = None) -> Dict[str, Any]:
    """Updates the status and optionally the feedback and due date of a specific task."""
    try:
        # --- Start of correctly indented block ---
        update_payload = {"status": new_status}

        # Add feedback if provided
        if feedback is not None:
            update_payload["feedback"] = feedback
            print(f"Updating task {task_id} to status: {new_status} with feedback.")
        else:
            print(f"Updating task {task_id} to status: {new_status} (No feedback provided - check frontend)")

        # Add new_due_date if provided and not empty
        if new_due_date:
            update_payload["due_date"] = new_due_date
            print(f"Updating task {task_id} with new due date: {new_due_date}")

        # Log the final payload being sent
        print(f"Update payload for task {task_id}: {update_payload}")

        if new_status == "Completed":
            response = delete_data("Tasks", {"task_id": task_id})
            response['status'] = new_status
            del response['created_at']
            response = insert_data("Tasks_tracking", response)

            if response:
                return {'success': True, 'message': 'Task status updated successfully.'}
            else:
                # Check if the task ID was simply not found
                check_task = supabase.table('Tasks').select('task_id').eq('task_id', task_id).execute()
                if not check_task.data:
                    return {'success': False, 'message': f'Task with ID {task_id} not found.'}
                else:
                    # If task exists but wasn't updated
                    return {'success': False, 'message': 'Task status update failed for an unknown reason.'}

        response = update_data(table="Tasks", match_criteria={"task_id": task_id}, new_data=update_payload)
        del response['created_at']
        response = insert_data("Tasks_tracking", response)

        print(f"Supabase update_task_status response: {response}")

        if response:
            return {'success': True, 'message': 'Task status updated successfully.'}
        else:
            # Check if the task ID was simply not found
            check_task = supabase.table('Tasks').select('task_id').eq('task_id', task_id).execute()
            if not check_task.data:
                return {'success': False, 'message': f'Task with ID {task_id} not found.'}
            else:
                # If task exists but wasn't updated
                return {'success': False, 'message': 'Task status update failed for an unknown reason.'}
        # --- End of correctly indented block ---

    except Exception as e:
        print(f"Unexpected error updating task status: {e}")
        return {'success': False, 'message': f"An unexpected error occurred: {str(e)}"}
        

def task_lookup(task_id: str = None, search_string: str = None):
    try:
        if task_id is not None:
            response = supabase.table("Tasks_tracking") \
                           .select("task_id, task_title, task_description, assigned_to_name, assigned_by, status, feedback, update_date") \
                           .eq('task_id', task_id) \
                           .order('update_date', desc=True) \
                           .execute()

            if not response.data:
                return None 

            first_record = response.data[0] 
            task_details = {
                'task_id': first_record.get('task_id'),
                'task_title': first_record.get('task_title'),
                'task_description': first_record.get('task_description'),
                'assigned_to': first_record.get('assigned_to_name'), 
                'assigned_by': first_record.get('assigned_by'), 
                'changing_entities': [
                    {
                        "status": item.get('status'),
                        "update_date": item.get('update_date'),
                        "feedback": item.get('feedback')
                    }
                    for item in response.data 
                ]
            }
            return task_details

        query = supabase.table("Tasks_tracking") \
                      .select("task_id, task_title, task_description, update_date") \
                      .order('update_date', desc=True)

        if search_string is not None:
            query = query.ilike('task_title', f'%{search_string}%')
            limit = 10
            fetch_limit = limit * 5 
        else:
            limit = 10
            fetch_limit = limit * 5

        response = query.limit(fetch_limit).execute()

        if not response.data:
            
            return []

        unique_tasks = _process_and_deduplicate_tasks(response.data, limit)
        
        return unique_tasks

    except Exception as e:
        return [] 
