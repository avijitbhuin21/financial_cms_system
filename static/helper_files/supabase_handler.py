import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional
import hashlib

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(url, key)

# =============================================== BASE FUNCTIONS ===================================================

def select_data(table: str, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    try:
        query = supabase.table(table).select("*")
        
        if query_params:
            for key, value in query_params.items():
                query = query.eq(key, value)
                
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
        query = supabase.table(table)
        
        # Apply match criteria
        for key, value in match_criteria.items():
            query = query.eq(key, value)
            
        response = query.update(new_data).execute()
        return response.data
    except Exception as e:
        raise Exception(f"Error updating data in {table}: {str(e)}")

def delete_data(table: str, match_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    try:
        query = supabase.table(table)
        
        # Apply match criteria
        for key, value in match_criteria.items():
            query = query.eq(key, value)
            
        response = query.delete().execute()
        return response.data
    except Exception as e:
        raise Exception(f"Error deleting data from {table}: {str(e)}")

# =============================================== ENCRYPTION FUNCTIONS ===================================================
def get_sha256_hash(text):
    if isinstance(text, str):
        text = text.encode('utf-8')
    hash_object = hashlib.sha256(text)
    return hash_object.hexdigest()





# ================================================ USER FUNCTIONS ===================================================

def login(email, password):
    database_data = select_data("Users", {"emailid": email, "password": get_sha256_hash(password)})
    if database_data != []:
        return {"status": True, "role":database_data[0]['roleid'], "team": database_data[0]['teamid'] }
    
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

def add_lead_to_db(lead_data):
    """Inserts lead data into the leads table."""
    try:
        # Use the generic insert_data function
        response = insert_data("leads", lead_data)
        
        # Check if the insertion was successful by checking if the returned dict is empty
        if response: # An empty dict evaluates to False
            # 'response' already holds the inserted data dict
            return {"status": True, "data": response}
        else:
            # insert_data returned an empty dict, indicating failure or no data returned
            return {"status": False, "message": "Failed to add lead or no data returned."}
            
    except Exception as e:
        print(f"Error in add_lead_to_db: {str(e)}") # Log the specific error
        return {"status": False, "message": str(e)}

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

def get_roles_from_supabase():
    x = [i['rolename'] for i in select_data("Roles")]
    x.remove('ADMIN')
    return x