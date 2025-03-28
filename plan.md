**Project: ilnb Group CRM**

**Technology Stack:**

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript (potentially a CSS framework like Bootstrap or Tailwind CSS for faster styling)
*   **Database:** Supabase (PostgreSQL)
*   **Version Control:** Git (e.g., GitHub, GitLab, Bitbucket)

---

**`plan.md`**

## Detailed Project Plan: ilnb Group CRM

This plan outlines the steps to develop the CRM system for ilnb Group using Flask and Supabase, based on the provided documents.

**Phase 1: Setup and Foundation (Estimated Time: 1-2 days)**

1.  **Environment Setup:**
    *   Install Python (if not already installed).
    *   Set up a project directory (`ilnb-crm`).
    *   Create and activate a Python virtual environment (e.g., `python -m venv venv`, `source venv/bin/activate` or `venv\Scripts\activate`).
    *   Install necessary Python libraries:
        ```bash
        pip install Flask python-dotenv supabase-py psycopg2-binary # (or just psycopg2)
        ```
        *(Note: `supabase-py` is the official client library. We'll use it for database interactions.)*
    *   Initialize Git repository: `git init`. Create a `.gitignore` file (for `venv`, `__pycache__`, `.env`, etc.). Make an initial commit.

2.  **Supabase Project Setup:**
    *   Go to [Supabase.io](https://supabase.io/) and create a new project (e.g., `ilnb-crm`).
    *   Note down your Supabase Project URL and `anon` & `service_role` API keys. Store these securely (we'll use environment variables).
    *   Navigate to the "Table Editor" and "SQL Editor" sections. We will use these to refine the schema.
    *   Explore the "Authentication" section - we might leverage Supabase Auth later.
    *   Explore "Database" -> "Roles" and "Row Level Security (RLS)" - important for access control later.

3.  **Flask Application Structure:**
    *   Create a basic Flask application structure. A good pattern is using Application Factories and Blueprints:
        ```
        ilnb-crm/
        ├── app/
        │   ├── __init__.py       # Application factory
        │   ├── models.py         # Database interaction logic (optional layer)
        │   ├── static/           # CSS, JS, Images
        │   │   ├── css/
        │   │   ├── js/
        │   │   └── images/
        │   ├── templates/        # HTML Templates (Jinja2)
        │   │   └── base.html     # Base template
        │   ├── auth/             # Blueprint for authentication
        │   │   ├── __init__.py
        │   │   └── routes.py
        │   ├── main/             # Blueprint for core/main routes
        │   │   ├── __init__.py
        │   │   └── routes.py
        │   ├── references/       # Blueprint for References module
        │   │   └── ...
        │   ├── clients/          # Blueprint for Clients module
        │   │   └── ...
        │   ├── interactions/     # Blueprint for Interactions module
        │   │   └── ...
        │   ├── service_requests/ # Blueprint for Service Requests module
        │   │   └── ...
        │   └── admin/            # Blueprint for Admin functions (User/Role/Team Mgmt)
        │       └── ...
        ├── venv/                 # Virtual environment
        ├── .env                  # Environment variables (SUPABASE_URL, SUPABASE_KEY)
        ├── .gitignore
        ├── config.py             # Configuration settings
        └── run.py                # Script to run the Flask app
        ```
    *   Create `config.py` to load settings (including Supabase keys from `.env`).
    *   Create `run.py` to initialize and run the Flask app using the factory.
    *   Create a basic `app/__init__.py` with the `create_app` factory function, initializing Supabase client and registering blueprints.
    *   Create a basic `base.html` template in `app/templates/`.

**Phase 2: Database Schema Refinement & Implementation (Estimated Time: 1-2 days)**

1.  **Analyze & Refine Schema:**
    *   Review the provided schema diagram (`ilnbcrm_*` tables).
    *   **Cross-reference with Notes:** Identify missing tables/fields based on the handwritten notes.
        *   **References:** The `leads` table seems to represent references. Add fields: `ref_obtained_by` (FK to users?), `ref_given_by` (text/varchar), `conversion_rm` (FK to users - maybe same as `leadconverter`?), `mode_of_communication` (enum/varchar: 'call', 'mail', 'whatsapp'), `denial_reason` (text, nullable). Consider if `leadgenerator` is `ref_obtained_by`. `leadconverter` might be the `conversion_rm`. Let's assume `leads` *is* the reference table for now.
        *   **Client Interactions:** Create a new table `ilnbcrm_interactions`. Columns: `interaction_id` (PK, serial), `client_id` (FK to clients), `user_id` (FK to users - the RM interacting), `interaction_type` (enum/varchar: 'New Business', 'Query Resolution', 'Portfolio Review'), `details` (text), `related_product_id` (FK to products, nullable), `related_query_id` (FK to queries, nullable), `timestamp` (timestamp with timezone).
        *   **Query Resolution:** Create a new table `ilnbcrm_queries`. Columns: `query_id` (PK, serial), `client_id` (FK to clients), `assigned_rm_id` (FK to users), `query_details` (text), `status` (enum/varchar: 'Open', 'In Progress', 'Resolved', 'Closed'), `resolution_details` (text, nullable), `created_at` (timestamp), `resolved_at` (timestamp, nullable). *Link this to `ilnbcrm_interactions` via `related_query_id`.*
        *   **Portfolio/Active Products:** The `activeproducts` field in `clients` is not normalized. Create a junction table `ilnbcrm_client_products`. Columns: `client_product_id` (PK), `client_id` (FK to clients), `product_id` (FK to products), `subscription_date` (date/timestamp).
        *   **Service Requests:** Create a new table `ilnbcrm_service_requests`. Columns: `request_id` (PK, serial), `client_id` (FK to clients), `request_type` (enum/varchar based on list: 'Account Opening', 'Contact Update', etc.), `details` (text), `status` (enum/varchar: 'Pending', 'In Progress', 'Completed', 'Rejected'), `assigned_user_id` (FK to users, nullable), `created_at` (timestamp), `updated_at` (timestamp).
        *   **Users/Roles/Teams:** The schema seems okay. Ensure `password` will store hashed values. `assignedrm` in `clients` should be a FK to `ilnbcrm_users.userid`. `leadgenerator`, `leadconverter` in `leads` should also be FKs to `ilnbcrm_users.userid`.
        *   **PAN/Acc ID:** `pan` is in `clients` (varchar). Add `account_id` (varchar, nullable) to `clients` as per "Interaction for New Business".

2.  **Implement Schema in Supabase:**
    *   Use the Supabase SQL Editor or Table Editor to create/modify tables based on the refined schema.
    *   Define Primary Keys (PK), Foreign Keys (FK) with appropriate `ON DELETE` / `ON UPDATE` actions (e.g., `SET NULL`, `RESTRICT`).
    *   Set `NOT NULL` constraints where applicable.
    *   Use appropriate data types (e.g., `INT`, `VARCHAR`, `TEXT`, `TIMESTAMP WITH TIME ZONE`, `DATE`, potentially `ENUM` types if preferred over `VARCHAR` for status/type fields).
    *   *Crucially:* Enable Row Level Security (RLS) on *all* tables that contain sensitive or user-specific data. We will define the policies later.

**Phase 3: Backend Development (Estimated Time: 5-10 days)**

1.  **Authentication & Authorization (RBAC):**
    *   Implement user registration (if needed, or maybe only Admins create users).
    *   Implement user login/logout functionality. You can:
        *   *Option A (Recommended):* Leverage Supabase Auth. Use the `supabase-py` client to sign up, sign in, manage users. Flask routes will handle the UI and call Supabase Auth methods. Store the Supabase session (JWT) securely on the client-side (e.g., HttpOnly cookie).
        *   *Option B:* Build custom auth. Hash passwords (`werkzeug.security`). Manage sessions using Flask sessions.
    *   Create decorators or middleware in Flask to check if a user is logged in (`@login_required`).
    *   Implement RBAC based on `roleid` (0: Admin, 1: Ops/RM Head, 2: Ops Exec/Junior RM). Create decorators (e.g., `@role_required(0)`, `@role_required([1, 2])`) to protect routes/endpoints based on the access levels defined in the notes. This involves fetching the user's role after they log in and checking it before allowing access to specific functions.

2.  **Supabase Integration:**
    *   In `app/__init__.py` or a dedicated `app/db.py`, initialize the Supabase client using the URL and service key from `config.py`.
    *   Write helper functions or classes (`app/models.py` or within blueprints) to interact with Supabase tables (select, insert, update, delete) using the `supabase-py` client. Handle potential errors from database operations.

3.  **Develop Module Blueprints:**
    *   **References/Leads (`app/references/`):**
        *   Routes for listing leads (potentially filtered by status, assigned RM).
        *   Route/Form for adding a new reference/lead (capturing all required fields).
        *   Route for viewing a single lead's details.
        *   Routes/Logic for updating lead status (WIP, Converted, Denied - including reason).
        *   Logic for assigning Conversion RM.
        *   Logic for handling conversion: Create/Update client record, link product (in `ilnbcrm_client_products`), mark lead as 'Converted'.
    *   **Clients (`app/clients/`):**
        *   CRUD routes for managing client details (respecting PAN compulsory, Acc ID optional).
        *   Route to view a client's profile, including their associated interactions, service requests, active products (fetched via joins or separate queries).
        *   Logic for assigning/changing the `assignedrm`.
    *   **Interactions (`app/interactions/`):**
        *   Route/Form for logging a new interaction (New Biz, Query, Portfolio Review). Link to client, user, potentially product/query.
        *   Route for listing interactions (filterable by client, RM, type).
        *   Logic within "Portfolio Review" interaction to potentially trigger "New product cross-sale/upsell" (maybe create a new lead or update an existing one).
    *   **Service Requests (`app/service_requests/`):**
        *   Route/Form for creating a new service request for a client.
        *   Route for listing service requests (filterable by client, status, type, assigned user).
        *   Route for viewing/updating a service request (status, assignment, details). Access control based on roles (e.g., Ops Exec can update, RM Head can view all).
    *   **Query Resolution (`app/queries/` or integrated into Interactions):**
        *   Route/Form for logging a new query.
        *   Route for listing queries (filterable by client, RM, status).
        *   Route for viewing/updating a query (assigning RM, updating status, adding resolution).
    *   **Admin (`app/admin/`):** (Protected for Admin role - Role ID 0)
        *   CRUD routes for managing Users (create, view, update role/team, deactivate). *Handle password hashing securely.*
        *   CRUD routes for managing Teams.
        *   CRUD routes for managing Products.
        *   (Optional) CRUD for Roles if they need to be dynamic.

**Phase 4: Frontend Development (Estimated Time: 5-8 days)**

1.  **Base Template and Styling:**
    *   Enhance `base.html` with common structure (navbar, sidebar, footer). Include placeholders for content (`{% block content %}{% endblock %}`).
    *   Set up static file serving in Flask.
    *   Choose a CSS approach:
        *   *Option A (Faster):* Integrate a CSS framework (e.g., Bootstrap, Tailwind CSS). Download or use CDN links in `base.html`. Utilize framework components for layout, forms, tables, buttons, etc.
        *   *Option B:* Write custom CSS from scratch or using a preprocessor like SASS/SCSS.
    *   Create a basic stylesheet (`style.css`) for custom overrides or core styles.

2.  **Develop Templates for Modules:**
    *   For each blueprint/module, create Jinja2 HTML templates (`.html` files in `app/templates/` subdirectories):
        *   **List Views:** Display data in tables (e.g., list of leads, clients, service requests). Include sorting, filtering, pagination controls.
        *   **Detail Views:** Show full details of a single record (e.g., a client's profile, a lead's history).
        *   **Forms:** Create forms for adding/editing data (e.g., new lead form, interaction log form, client edit form). Use appropriate HTML form elements (`input`, `select`, `textarea`).
    *   Use Jinja2 templating features (inheritance, loops, conditionals) to render dynamic data passed from Flask routes.
    *   Ensure forms include CSRF protection (e.g., using Flask-WTF or similar).

3.  **JavaScript for Interactivity:**
    *   Add JavaScript (`app/static/js/`) for:
        *   **Client-side form validation:** Provide immediate feedback to users before submitting forms.
        *   **Dynamic UI updates:** (Optional) Use AJAX/Fetch API to update parts of a page without full reloads (e.g., changing status, adding comments).
        *   **UI Enhancements:** Date pickers, confirmation dialogs, interactive tables (e.g., using DataTables.js).

**Phase 5: Integration, Testing, and Refinement (Estimated Time: 4-7 days)**

1.  **Integrate Frontend and Backend:**
    *   Ensure forms submit data correctly to Flask routes.
    *   Ensure data retrieved from Supabase is correctly displayed in templates.
    *   Test the flow of data through the entire application.

2.  **Implement Row Level Security (RLS) in Supabase:**
    *   Define RLS policies on tables based on user roles and relationships (e.g., an RM can only see their assigned leads/clients, an Ops Exec can only see service requests assigned to them or their team, Admins can see everything).
    *   Test these policies thoroughly by making requests with different user roles/credentials. *This is critical for security.*

3.  **Testing:**
    *   **Manual Testing:** Click through all features using different user roles (Admin, RM Head, Junior RM). Test edge cases, invalid inputs.
    *   **Workflow Testing:** Test key processes end-to-end (e.g., Add Reference -> Convert to Client -> Log Interaction -> Create Service Request).
    *   **(Optional) Automated Testing:** Write unit tests for helper functions/business logic and integration tests for Flask routes if time permits.

4.  **Refinement & Feedback:**
    *   Review the application for usability and consistency.
    *   (If possible) Get feedback from potential users (like the company contacts).
    *   Address bugs and make improvements based on testing and feedback. Polish the UI/UX.

**Phase 6: Deployment (Optional - Estimated Time: 1-2 days)**

1.  **Choose Hosting:** Select a platform (e.g., Heroku, PythonAnywhere, Render, AWS EC2/Elastic Beanstalk, Google Cloud Run).
2.  **Prepare for Production:**
    *   Configure environment variables on the hosting platform (Supabase keys, Flask secret key, database URL if needed).
    *   Set `DEBUG = False` in Flask config.
    *   Use a production-ready WSGI server (e.g., Gunicorn, Waitress) instead of the Flask development server.
3.  **Deploy:** Follow the hosting provider's instructions to deploy the Flask application.
4.  **Domain & HTTPS:** Configure a custom domain and set up HTTPS (often handled by the hosting provider).

**Phase 7: Documentation (Ongoing & Finalization - Estimated Time: 1-2 days)**

1.  **Code Comments:** Add comments to explain complex parts of the code.
2.  **README.md:** Update the project's README file with setup instructions, how to run the application locally, and an overview of the structure.
3.  **Database Schema:** Document the final database schema.
4.  **(Optional) User Guide:** Create a simple guide for end-users on how to use the CRM's features.

---

**Collaboration Points:**

*   **Schema Refinement:** We should confirm the interpretations of the notes and the proposed schema additions/modifications before implementing them in Supabase.
*   **Access Control Details:** Clarify the exact permissions for each role (Level 0, 1, 2) for each module (View, Create, Edit, Delete, Assign).
*   **Workflow Specifics:** Double-check the exact steps involved in "Lead Conversion" or "Portfolio Review leading to Cross-sell".
*   **Prioritization:** If time is limited, which modules are most critical to implement first? (Likely References/Leads and Clients).



## HERE IS THE WHOLE TABLE STRUCTURE IN SUPABASE:
(AS OF NOW ALL THE USERS HAVE READ AND WRITE PERMISSIONS FOR ALL THE TABLES)

-- 1. Roles Table
CREATE TABLE IF NOT EXISTS ilnbcrm_roles (
    roleid SERIAL PRIMARY KEY,
    rolename VARCHAR(50) NOT NULL UNIQUE,
    -- Access Level: 0=Admin, 1=Operation/RM Head, 2=ops executive/Junior RM
    access_level INT NOT NULL UNIQUE CHECK (access_level IN (0, 1, 2)),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Insert Base Roles based on notes
INSERT INTO ilnbcrm_roles (rolename, access_level) VALUES
    ('Admin', 0),
    ('Operation/RM Head', 1),
    ('Ops Executive/Junior RM', 2)
ON CONFLICT (rolename) DO NOTHING; -- Avoid errors if run multiple times

-- 2. Teams Table
CREATE TABLE IF NOT EXISTS ilnbcrm_teams (
    teamid SERIAL PRIMARY KEY,
    teamname VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Products Table
CREATE TABLE IF NOT EXISTS ilnbcrm_products (
    productid SERIAL PRIMARY KEY,
    prodname VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Users Table
CREATE TABLE IF NOT EXISTS ilnbcrm_users (
    userid SERIAL PRIMARY KEY,
    -- Supabase Auth uses UUIDs, link it if using Supabase Auth
    -- auth_user_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE SET NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100),
    emailid VARCHAR(100) NOT NULL UNIQUE,
    -- Password managed by Supabase Auth or hashed if custom
    password_hash VARCHAR(255), -- Store hash if not using Supabase Auth
    mobile VARCHAR(15) UNIQUE,
    roleid INT NOT NULL,
    teamid INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ, -- Manually update or use trigger

    FOREIGN KEY (roleid) REFERENCES ilnbcrm_roles(roleid) ON DELETE RESTRICT, -- Don't delete roles if users exist
    FOREIGN KEY (teamid) REFERENCES ilnbcrm_teams(teamid) ON DELETE SET NULL -- Allow users to exist if team is deleted
);
-- Index for foreign keys often used in queries
CREATE INDEX IF NOT EXISTS idx_users_roleid ON ilnbcrm_users(roleid);
CREATE INDEX IF NOT EXISTS idx_users_teamid ON ilnbcrm_users(teamid);

-- Enable RLS for Users table
ALTER TABLE ilnbcrm_users ENABLE ROW LEVEL SECURITY;

-- 5. Leads Table (Based on References module and schema diagram 'leads')
CREATE TABLE IF NOT EXISTS ilnbcrm_leads (
    leadid SERIAL PRIMARY KEY,
    leadname VARCHAR(100) NOT NULL, -- Name of the potential client
    ref_given_by VARCHAR(100),      -- Name/source of who gave the reference
    mode_of_communication VARCHAR(20) CHECK (mode_of_communication IN ('call', 'mail', 'whatsapp', 'in-person', 'other')),
    leadgenerator INT,            -- User who obtained/entered the reference (FK to users)
    leadconverter INT NULL,           -- User (RM) assigned for conversion (FK to users)
    leadstatus VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (leadstatus IN ('Pending', 'Work In Progress', 'Converted', 'Denied')),
    denial_reason TEXT NULL,         -- Reason if status is 'Denied'
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,         -- Manually update or use trigger

    FOREIGN KEY (leadgenerator) REFERENCES ilnbcrm_users(userid) ON DELETE SET NULL,
    FOREIGN KEY (leadconverter) REFERENCES ilnbcrm_users(userid) ON DELETE SET NULL
);
-- Index for foreign keys and status
CREATE INDEX IF NOT EXISTS idx_leads_leadgenerator ON ilnbcrm_leads(leadgenerator);
CREATE INDEX IF NOT EXISTS idx_leads_leadconverter ON ilnbcrm_leads(leadconverter);
CREATE INDEX IF NOT EXISTS idx_leads_leadstatus ON ilnbcrm_leads(leadstatus);

-- Enable RLS for Leads table
ALTER TABLE ilnbcrm_leads ENABLE ROW LEVEL SECURITY;


-- 6. Clients Table
CREATE TABLE IF NOT EXISTS ilnbcrm_clients (
    clientid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob DATE,
    emailid VARCHAR(100) UNIQUE, -- Can be null initially but maybe required later?
    mobile VARCHAR(15) UNIQUE,   -- Can be null initially?
    address TEXT,
    pan VARCHAR(10) NOT NULL UNIQUE, -- Compulsory & Unique
    account_id VARCHAR(50) UNIQUE NULL, -- Optional Account ID
    assignedrm INT NULL,             -- User (RM) assigned to this client (FK to users)
    leadid INT UNIQUE NULL,          -- Link to the original lead if converted (FK to leads)
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,          -- Manually update or use trigger

    FOREIGN KEY (assignedrm) REFERENCES ilnbcrm_users(userid) ON DELETE SET NULL,
    FOREIGN KEY (leadid) REFERENCES ilnbcrm_leads(leadid) ON DELETE SET NULL -- Keep client even if lead deleted? Or RESTRICT? SET NULL seems ok.
);
-- Index for foreign keys and commonly searched fields
CREATE INDEX IF NOT EXISTS idx_clients_assignedrm ON ilnbcrm_clients(assignedrm);
CREATE INDEX IF NOT EXISTS idx_clients_pan ON ilnbcrm_clients(pan);
CREATE INDEX IF NOT EXISTS idx_clients_leadid ON ilnbcrm_clients(leadid);

-- Enable RLS for Clients table
ALTER TABLE ilnbcrm_clients ENABLE ROW LEVEL SECURITY;


-- 7. Queries Table (For Query Resolution module)
CREATE TABLE IF NOT EXISTS ilnbcrm_queries (
    query_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    assigned_rm_id INT NULL, -- User (RM) assigned to handle the query
    query_details TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
    resolution_details TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    resolved_at TIMESTAMPTZ NULL,
    updated_at TIMESTAMPTZ, -- Manually update or use trigger

    FOREIGN KEY (client_id) REFERENCES ilnbcrm_clients(clientid) ON DELETE CASCADE, -- If client deleted, delete their queries
    FOREIGN KEY (assigned_rm_id) REFERENCES ilnbcrm_users(userid) ON DELETE SET NULL
);
-- Index for foreign keys and status
CREATE INDEX IF NOT EXISTS idx_queries_client_id ON ilnbcrm_queries(client_id);
CREATE INDEX IF NOT EXISTS idx_queries_assigned_rm_id ON ilnbcrm_queries(assigned_rm_id);
CREATE INDEX IF NOT EXISTS idx_queries_status ON ilnbcrm_queries(status);

-- Enable RLS for Queries table
ALTER TABLE ilnbcrm_queries ENABLE ROW LEVEL SECURITY;


-- 8. Interactions Table (Log interactions with clients)
CREATE TABLE IF NOT EXISTS ilnbcrm_interactions (
    interaction_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    user_id INT NOT NULL, -- User (RM/Staff) who had the interaction
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('New Business', 'Query Resolution', 'Portfolio Review', 'General Update', 'Other')),
    details TEXT NOT NULL,
    related_product_id INT NULL, -- Link to product if relevant (e.g., New Business)
    related_query_id INT NULL,   -- Link to query if relevant (e.g., Query Resolution interaction)
    interaction_time TIMESTAMPTZ DEFAULT now(), -- Changed from 'timestamp' to avoid keyword conflict

    FOREIGN KEY (client_id) REFERENCES ilnbcrm_clients(clientid) ON DELETE CASCADE, -- If client deleted, delete their interactions
    FOREIGN KEY (user_id) REFERENCES ilnbcrm_users(userid) ON DELETE RESTRICT, -- Don't allow deleting user if they logged interactions? Or SET NULL? RESTRICT safer.
    FOREIGN KEY (related_product_id) REFERENCES ilnbcrm_products(productid) ON DELETE SET NULL,
    FOREIGN KEY (related_query_id) REFERENCES ilnbcrm_queries(query_id) ON DELETE SET NULL -- If query deleted, just nullify link here
);
-- Index for foreign keys and type
CREATE INDEX IF NOT EXISTS idx_interactions_client_id ON ilnbcrm_interactions(client_id);
CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON ilnbcrm_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON ilnbcrm_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_interactions_related_query_id ON ilnbcrm_interactions(related_query_id);

-- Enable RLS for Interactions table
ALTER TABLE ilnbcrm_interactions ENABLE ROW LEVEL SECURITY;


-- 9. Service Requests Table
CREATE TABLE IF NOT EXISTS ilnbcrm_service_requests (
    request_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    request_type VARCHAR(100) NOT NULL CHECK (request_type IN (
        'Account Opening', 'Contact Details Updation', 'Account Closure',
        'Investment Plan Execution', 'Other Query', 'Address Updation',
        'KYC Updation', 'Bank Updation', 'Nominee Updation'
    )),
    details TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Rejected')),
    assigned_user_id INT NULL, -- User (Ops/RM) assigned to handle request
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ, -- Manually update or use trigger
    completed_at TIMESTAMPTZ NULL,

    FOREIGN KEY (client_id) REFERENCES ilnbcrm_clients(clientid) ON DELETE CASCADE, -- If client deleted, delete their requests
    FOREIGN KEY (assigned_user_id) REFERENCES ilnbcrm_users(userid) ON DELETE SET NULL
);
-- Index for foreign keys and status/type
CREATE INDEX IF NOT EXISTS idx_service_requests_client_id ON ilnbcrm_service_requests(client_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_assigned_user_id ON ilnbcrm_service_requests(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_service_requests_status ON ilnbcrm_service_requests(status);
CREATE INDEX IF NOT EXISTS idx_service_requests_type ON ilnbcrm_service_requests(request_type);

-- Enable RLS for Service Requests table
ALTER TABLE ilnbcrm_service_requests ENABLE ROW LEVEL SECURITY;


-- 10. Client Products Junction Table (Replaces 'activeproducts' field)
CREATE TABLE IF NOT EXISTS ilnbcrm_client_products (
    client_product_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    product_id INT NOT NULL,
    subscription_date DATE DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),

    FOREIGN KEY (client_id) REFERENCES ilnbcrm_clients(clientid) ON DELETE CASCADE, -- If client deleted, delete their product links
    FOREIGN KEY (product_id) REFERENCES ilnbcrm_products(productid) ON DELETE RESTRICT, -- Don't delete product if clients have it? Or CASCADE? RESTRICT is safer.
    UNIQUE (client_id, product_id) -- Ensure a client doesn't have the same product twice
);
-- Index for foreign keys
CREATE INDEX IF NOT EXISTS idx_client_products_client_id ON ilnbcrm_client_products(client_id);
CREATE INDEX IF NOT EXISTS idx_client_products_product_id ON ilnbcrm_client_products(product_id);

-- Enable RLS for Client Products table
ALTER TABLE ilnbcrm_client_products ENABLE ROW LEVEL SECURITY;

-- Confirmation message (optional, won't show in Supabase UI but useful in psql)
-- SELECT 'ilnb CRM tables created successfully.';
