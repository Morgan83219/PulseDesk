from flask import render_template, redirect, url_for, flash, session, request, Blueprint, request
from app.forms import LoginForm, RegistrationForm, TicketForm, TicketNoteForm, EditTicketForm, UserRoleForm
from app.models import User, Ticket, TicketNote
from app import db
from flask_login import current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app.utils import admin_required
import sqlite3


main = Blueprint('main', __name__)

@main.before_app_request
def require_login():
    exempt_routes = ['main.login', 'main.register', 'main.index']
    if 'username' not in session and (request.endpoint not in exempt_routes):
        flash("Your session has expired. Please log in again.", "warning")
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            user.date_last_login = datetime.now()
            db.session.commit()

            session['username'] = user.username
            session['role'] = user.role

            role = user.role
            
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{time_now}]User logged in as: {username}, with role: {role}, redirecting {username} to homepage")
            
            flash('Login Sucessful!', 'success')
            return redirect(url_for('main.home'))

        flash('Invalid username or password.', 'danger')
            
    return render_template("login.html", form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another one.', 'danger')
            return render_template('register.html', form=form)

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/home')
def home():
    print("Session role:", session.get('role'))
    return render_template('home.html')

@main.route('/ticket_creation', methods=['GET', 'POST'])
def ticket_creation():
    form = TicketForm()

    # Define subcategory choices mapping
    subcategory_map = {
        "Application or Software": [
            "Access", "Password Reset", "Configuration Issue", "Data Issue",
            "Defect or Error", "How to Question", "Installation", "Performance"
        ],
        "End User Device": [
            "Audio Issue", "Broken Faulty Device", "Capacity Issue",
            "Configuration Issue", "Defect or Error"
        ],
        "Network": [
            "Access or Connectivity Issue", "Data Issue", "Network Drive Issue",
            "Performance Issue"
        ],
        "Security & Compliance": [
            "Compliance/Audit", "Data Issue", "Intrusion", "New Employee On-boarding",
            "Remote Access Issue", "User Account Issue", "Virus/Malware"
        ]
    }

    # Dynamically set subcategory choices based on selected category
    if form.category.data in subcategory_map:
        form.subcategory.choices = [(s, s) for s in subcategory_map[form.category.data]]
    else:
        # Default to empty choices
        form.subcategory.choices = []

    if form.validate_on_submit():
        print("Current session:", session)
        print("Form validated successfully")
        
        ticket = Ticket(
            caller=session['username'],
            asset_id=form.asset_id.data,
            category=form.category.data,
            subcategory=form.subcategory.data,
            short_description=form.short_description.data,
            long_description=form.long_description.data,
            urgency=form.urgency.data,
            severity=form.severity.data,
            state='new',
            assigned_user=None
        )
        try:
            db.session.add(ticket)
            db.session.commit()
            print("Ticket committed to database")
            flash('Ticket successfully created!', 'success')
            return redirect(url_for('main.ticket_system'))
        except Exception as e:
            print("Error inserting ticket:", e)
            db.session.rollback()
            flash('There was an error creating the ticket.', 'danger')
    elif request.method == 'POST':
        print("Form validation failed")
        print(form.errors)
        

    return render_template('ticket_creation.html', form=form)         

@main.route('/ticket_system', methods=['GET', 'POST'])
def ticket_system():
    #Getting filter values from query parameters
    ticket_id = request.args.get('ticket_id', type=int)
    caller = request.args.get('caller', type=str)
    state = request.args.get('state', type=str)
    severity = request.args.get('severity', type=str)

    #Query Start, allows filters
    query = Ticket.query
    if ticket_id:
        query = query.filter_by(id=ticket_id)
    if caller:
        query = query.filter(Ticket.caller.ilike(f'%{caller}%'))
    if state:
        query = query.filter_by(state=state)
    if severity:
        query = query.filter_by(severity=severity)

    tickets = query.order_by(Ticket.date_created.desc()).all()

    return render_template(
        'ticket_system.html',
        tickets=tickets,
        filter_values={
            'ticket_id': ticket_id or '',
            'caller': caller or '',
            'state': state or '',
            'severity': severity or ''
        },
        states = ['New', 'In Progress', 'On Hold', 'Completed'],
        severities = ['Minor', 'Major', 'Critical']
    )

@main.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    user_role = session.get('role')

    # Forms
    # Main ticket edit form
    edit_form = EditTicketForm(obj=ticket)

    # Notes form
    note_form = TicketNoteForm()

    # Adjust edit_form fields based on role
    if user_role == 'user':
        # Remove fields not editable by User
        if hasattr(edit_form, 'asset_id'):
            del edit_form.asset_id
        if hasattr(edit_form, 'assigned_user'):
            del edit_form.assigned_user
        if hasattr(edit_form, 'state'):
            del edit_form.state

    # Process ticket edits
    if edit_form.validate_on_submit() and 'edit_ticket' in request.form:
        if user_role in ['changer', 'admin']:
            ticket.asset_id = edit_form.asset_id.data
            ticket.assigned_user = edit_form.assigned_user.data
            ticket.state = edit_form.state.data

        ticket.urgency = edit_form.urgency.data
        ticket.severity = edit_form.severity.data

        db.session.commit()
        flash('Ticket updated successfully.', 'success')
        return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))

    # Process adding a note
    elif note_form.validate_on_submit() and 'add_note' in request.form:
        note = TicketNote(
            ticket_id=ticket.id,
            author=session['username'],
            content=note_form.content.data
        )
        db.session.add(note)
        db.session.commit()
        flash('Note added.', 'success')
        return redirect(url_for('main.ticket_detail', ticket_id=ticket.id))
    
    print("Rendering ticket_detail.html with edit_form:", 'edit_form' in locals())
    print("Request method:", request.method)
    print("Form errors (edit_form):", edit_form.errors)
    print("Form errors (note_form):", note_form.errors)

    return render_template(
        'ticket_detail.html',
        ticket=ticket,
        edit_form=edit_form,
        note_form=note_form,
        role=user_role
    )

@main.route('/user_manual')
def user_manual():
    return "User Manual Page - Coming Soon"

@main.route('/user_management', methods=['GET', 'POST'])
@admin_required
def user_management():
    users = User.query.all()
    forms = {}
    for user in users:
        form = UserRoleForm(obj=user)
        form.user_id.data = user.id
        form.role.data = user.role
        forms[user.id] = form

    if request.method == 'POST':
        print("=== POST Data ===", request.form)
        form = UserRoleForm(request.form)
        if form.validate():
            user_id = int(form.user_id.data)
            new_role = form.role.data
            user = User.query.get(user_id)

            if user.username == session['username']:
                flash("You can't change your own role.", 'warning')
            elif user:
                user.role = new_role
                db.session.commit()
                flash(f"Role for {user.username} updated to {new_role}.", 'success')
            else:
                flash("User not found.", "danger")
        else:
            flash("Invalid form submission.", "danger")
            print("Form errors:", form.errors)

        return redirect(url_for('main.user_management'))

    return render_template('user_management.html', users=users, forms=forms)



@main.route('/logout')
def logout():
    username = session.get('username', 'unknown')
    session.clear()
    flash("You have successfully been logged out.", "info")
    return render_template('logout.html', username=username)

@main.context_processor
def verify_user_roles():
    username = session.get('username')
    role = (session.get('role') or '').lower()
    return {
        'username': username,
        'is_user': role == 'user',
        'is_admin': role == 'admin',
        'is_changer': role == 'changer'
    }


    


