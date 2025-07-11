from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users' #Explicitly setting the table name to use
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'assigner', or 'user'
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    caller = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    asset_id = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    short_description = db.Column(db.String(200), nullable=False)
    long_description = db.Column(db.Text, nullable=True)
    urgency = db.Column(db.String(20), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), default='New')
    assigned_user = db.Column(db.String(50), nullable=True)
    notes = db.relationship('TicketNote', backref='ticket', cascade='all, delete', lazy=True)

class TicketNote(db.Model):
    __tablename__ = 'ticket_notes'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    
