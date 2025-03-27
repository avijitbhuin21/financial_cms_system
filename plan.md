**Project: JLNB Group CRM**

**Technology Stack:**

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript (potentially a CSS framework like Bootstrap or Tailwind CSS for faster styling)
*   **Database:** Supabase (PostgreSQL)
*   **Version Control:** Git (e.g., GitHub, GitLab, Bitbucket)

---

**`plan.md`**

## Detailed Project Plan: JLNB Group CRM

This plan outlines the steps to develop the CRM system for JLNB Group using Flask and Supabase, based on the provided documents.

**Phase 1: Setup and Foundation (Estimated Time: 1-2 days)**

1.  **Environment Setup:**
    *   Install Python (if not already installed).
    *   Set up a project directory (`jlnb-crm`).
    *   Create and activate a Python virtual environment (e.g., `python -m venv venv`, `source venv/bin/activate` or `venv\Scripts\activate`).
    *   Install necessary Python libraries:
        ```bash
        pip install Flask python-dotenv supabase-py psycopg2-binary # (or just psycopg2)
        ```
        *(Note: `supabase-py` is the official client library. We'll use it for database interactions.)*
    *   Initialize Git repository: `git init`. Create a `.gitignore` file (for `venv`, `__pycache__`, `.env`, etc.). Make an initial commit.

2.  **Supabase Project Setup:**
    *   Go to [Supabase.io](https://supabase.io/) and create a new project (e.g., `jlnb-crm`).
    *   Note down your Supabase Project URL and `anon` & `service_role` API keys. Store these securely (we'll use environment variables).
    *   Navigate to the "Table Editor" and "SQL Editor" sections. We will use these to refine the schema.
    *   Explore the "Authentication" section - we might leverage Supabase Auth later.
    *   Explore "Database" -> "Roles" and "Row Level Security (RLS)" - important for access control later.

3.  **Flask Application Structure:**
    *   Create a basic Flask application structure. A good pattern is using Application Factories and Blueprints:
        ```
        jlnb-crm/
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
    *   Review the provided schema diagram (`jlnbcrm_*` tables).
    *   **Cross-reference with Notes:** Identify missing tables/fields based on the handwritten notes.
        *   **References:** The `leads` table seems to represent references. Add fields: `ref_obtained_by` (FK to users?), `ref_given_by` (text/varchar), `conversion_rm` (FK to users - maybe same as `leadconverter`?), `mode_of_communication` (enum/varchar: 'call', 'mail', 'whatsapp'), `denial_reason` (text, nullable). Consider if `leadgenerator` is `ref_obtained_by`. `leadconverter` might be the `conversion_rm`. Let's assume `leads` *is* the reference table for now.
        *   **Client Interactions:** Create a new table `jlnbcrm_interactions`. Columns: `interaction_id` (PK, serial), `client_id` (FK to clients), `user_id` (FK to users - the RM interacting), `interaction_type` (enum/varchar: 'New Business', 'Query Resolution', 'Portfolio Review'), `details` (text), `related_product_id` (FK to products, nullable), `related_query_id` (FK to queries, nullable), `timestamp` (timestamp with timezone).
        *   **Query Resolution:** Create a new table `jlnbcrm_queries`. Columns: `query_id` (PK, serial), `client_id` (FK to clients), `assigned_rm_id` (FK to users), `query_details` (text), `status` (enum/varchar: 'Open', 'In Progress', 'Resolved', 'Closed'), `resolution_details` (text, nullable), `created_at` (timestamp), `resolved_at` (timestamp, nullable). *Link this to `jlnbcrm_interactions` via `related_query_id`.*
        *   **Portfolio/Active Products:** The `activeproducts` field in `clients` is not normalized. Create a junction table `jlnbcrm_client_products`. Columns: `client_product_id` (PK), `client_id` (FK to clients), `product_id` (FK to products), `subscription_date` (date/timestamp).
        *   **Service Requests:** Create a new table `jlnbcrm_service_requests`. Columns: `request_id` (PK, serial), `client_id` (FK to clients), `request_type` (enum/varchar based on list: 'Account Opening', 'Contact Update', etc.), `details` (text), `status` (enum/varchar: 'Pending', 'In Progress', 'Completed', 'Rejected'), `assigned_user_id` (FK to users, nullable), `created_at` (timestamp), `updated_at` (timestamp).
        *   **Users/Roles/Teams:** The schema seems okay. Ensure `password` will store hashed values. `assignedrm` in `clients` should be a FK to `jlnbcrm_users.userid`. `leadgenerator`, `leadconverter` in `leads` should also be FKs to `jlnbcrm_users.userid`.
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
        *   Logic for handling conversion: Create/Update client record, link product (in `jlnbcrm_client_products`), mark lead as 'Converted'.
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
