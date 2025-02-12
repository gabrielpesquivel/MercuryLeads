from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages

# Configure Flask-Mail for SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use 'smtp.mailtrap.io' for testing
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')  # Store email credentials securely
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')

db = SQLAlchemy(app)
mail = Mail(app)

# Define the Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Project Name
    organisation = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    install_target = db.Column(db.String(100))  # Project installation target date
    action_required = db.Column(db.String(200))  # Action needed
    contacts = db.relationship('Contact', backref='project', lazy=True)  # Relationship with contacts

    def __repr__(self):
        return f'<Project {self.name}>'

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Delete the project from the database
    db.session.delete(project)
    db.session.commit()

    flash(f"Project '{project.name}' deleted successfully.", "success")
    return redirect(url_for('projects'))

@app.route('/update_project/<int:project_id>', methods=['POST'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    new_action = request.form.get('new_action')

    if new_action:
        project.action_required = new_action
        db.session.commit()
        flash(f"Action for '{project.name}' updated successfully.", "success")
    else:
        flash("No action provided.", "warning")

    return redirect(url_for('projects'))

# Update Contact model to reference Project
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    last_contacted = db.Column(db.String(100))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)  # Link to a project

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

@app.route('/')
def index():
    return redirect(url_for('leads'))

@app.route('/leads', methods=['GET', 'POST'])
def leads():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        last_contacted = request.form.get('last_contacted')
        project_id = request.form.get('project_id')

        if first_name and last_name:
            new_contact = Contact(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                last_contacted=last_contacted,
                project_id=project_id if project_id else None
            )
            db.session.add(new_contact)
            db.session.commit()
            return redirect(url_for('leads'))

    contacts = Contact.query.all()
    projects = Project.query.all()  # Fetch projects for dropdown
    return render_template('leads.html', contacts=contacts, projects=projects)

@app.route('/dashboard')
def dashboard():
    # Query all contacts and sort them by 'last_contacted' in ascending order
    contacts = Contact.query.order_by(Contact.last_contacted.asc().nullsfirst()).limit(5).all()

    total_contacts = Contact.query.count()
    
    return render_template('dashboard.html', total_contacts=total_contacts, least_recently_contacted=contacts)

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('leads'))

@app.route('/email/<int:contact_id>', methods=['POST'])
def email_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)

    if contact.email:
        # Update last_contacted date
        contact.last_contacted = datetime.date.today().strftime("%Y-%m-%d")
        db.session.commit()

        # Create and send the email
        subject = "Follow-up Contact"
        body = f"Hello {contact.first_name},\n\nThis is a follow-up email.\n\nBest regards,\n Mercury Innovation PTY LTD"

        msg = Message(subject, sender=os.getenv('EMAIL_USER'), recipients=[contact.email])
        msg.body = body

        try:
            mail.send(msg)
            print("Email sent successfully!")
            flash("Email sent successfully!", "success")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            flash(f"Error sending email: {str(e)}", "danger")

    else:
        print("No email address found for this contact.")
        flash("No email address found for this contact.", "warning")

    return redirect(url_for('leads'))

@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if request.method == 'POST':
        name = request.form.get('name')
        organisation = request.form.get('organisation')
        city = request.form.get('city')
        install_target = request.form.get('install_target')
        action_required = request.form.get('action_required')

        if name and organisation:
            new_project = Project(
                name=name,
                organisation=organisation,
                city=city,
                install_target=install_target,
                action_required=action_required
            )
            db.session.add(new_project)
            db.session.commit()
            return redirect(url_for('projects'))

    # Query all projects
    all_projects = Project.query.all()
    return render_template('projects.html', projects=all_projects)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
