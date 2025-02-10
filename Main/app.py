from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    last_contacted = db.Column(db.String(100))

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

@app.route('/')
def index():
    # Redirect to the leads database page
    return redirect(url_for('leads'))

@app.route('/leads', methods=['GET', 'POST'])
def leads():
    if request.method == 'POST':
        # Retrieve data from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        last_contacted = request.form.get('last_contacted')

        # Create and add a new contact if first name and last name are provided
        if first_name and last_name:
            new_contact = Contact(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                last_contacted=last_contacted
            )
            db.session.add(new_contact)
            db.session.commit()
            return redirect(url_for('leads'))

    # Query all contacts to display in the table
    contacts = Contact.query.all()
    return render_template('leads.html', contacts=contacts)

@app.route('/dashboard')
def dashboard():
    # Example dashboard: just show the total number of contacts
    total_contacts = Contact.query.count()
    return render_template('dashboard.html', total_contacts=total_contacts)

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('leads'))

@app.route('/email/<int:contact_id>', methods=['POST'])
def email_contact(contact_id):
    # Get the contact or return 404 if not found
    contact = Contact.query.get_or_404(contact_id)
    # Update the last_contacted field to today's date.
    # You can format the date as you wish; here we use YYYY-MM-DD.
    contact.last_contacted = datetime.date.today().strftime("%Y-%m-%d")
    db.session.commit()
    # Redirect back to the leads page (or any other page)
    return redirect(url_for('leads'))

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
