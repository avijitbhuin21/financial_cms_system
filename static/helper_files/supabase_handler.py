import os
from supabase import create_client, Client
from typing import Dict, Any, List, Optional

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

# ================================================ USER FUNCTIONS ===================================================

def login(email, password):
    database_data = select_data("Users", {"emailid": email, "password": password})
    if database_data != []:
        return {"status": True, "role":database_data[0]['roleid'], "team": database_data[0]['teamid'] }
    
    else:
        return {"status": False, "role": None, "team": None}
    
def signup(first_name, last_name, email, password, phone_number, roleid, teamid):
    try:
        data = {
            "username": first_name + " " + last_name,
            "emailid": email,
            "password": password,
            "mobile": phone_number,
            "roleid": roleid,
            "teamid": teamid,
        }
        insert_data("Users", data)
        return {"status": True}
    except Exception as e:
        return {"status": False, "message": str(e)}
