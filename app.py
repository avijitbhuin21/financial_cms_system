from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def login_page():
    """Renders the login page."""
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    """Handles the login form submission."""
    username = request.form.get('username')
    password = request.form.get('password')
    print(f"Received login attempt:")
    print(f"Username/Email: {username}")
    print(f"Password: {password}")
    # In a real app, you'd validate credentials here
    return "Login attempt received (check console)."

@app.route('/signup', methods=['POST'])
def handle_signup():
    """Handles the signup form submission."""
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')

    print(f"\nReceived signup attempt:")
    print(f"First Name: {first_name}")
    print(f"Last Name: {last_name}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Phone Number: {phone_number}")
    print(f"Address: {address}")

    return "Signup attempt received (check console)."

if __name__ == '__main__':
    app.run(debug=True)