from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=50)]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField ('Register')

class TicketNoteForm(FlaskForm):
    content = TextAreaField('Add a Note', validators=[DataRequired()])
    submit = SubmitField('Post Note')

class EditTicketForm(FlaskForm):
    asset_id = StringField('Asset ID', validators=[Length(max=20)])
    urgency = SelectField('Urgency', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')])
    severity = SelectField('Severity', choices=[('Minor', 'Minor'), ('Major', 'Major'), ('Critical', 'Critical')])
    state = SelectField('State', choices=[('New', 'New'), ('In Progress', 'In Progress'), ('On Hold', 'On Hold'), ('Completed', 'Completed')])
    assigned_user = StringField('Assigned User', validators=[Length(max=50)])
    submit = SubmitField('Update Ticket')

class UserRoleForm(FlaskForm):
    user_id = HiddenField('User ID')
    role = SelectField('Role', choices=[
        ('user', 'User'),
        ('changer', 'Changer'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Role')

class TicketForm(FlaskForm):
    asset_id = StringField('Asset ID', validators=[DataRequired(), Length(max=20)])

    category = SelectField(
        'Category',
        choices=[
            ('Application or Software', 'Application or Software'),
            ('End User Device', 'End User Device'),
            ('Network', 'Network'),
            ('Security & Compliance', 'Security & Compliance')
        ],
        validators=[DataRequired()]
    )

    subcategory = SelectField('Subcategory', choices=[], validators=[DataRequired()])

    short_description = StringField('Short Description', validators=[DataRequired(), Length(max=50)])
    long_description = TextAreaField('Long Description', validators=[Length(max=250)])

    urgency = SelectField(
        'Urgency',
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')],
        validators=[DataRequired()]

    )

    severity= SelectField(
        'Severity',
        choices=[('Minor', 'Minor'), ('Major', 'Major'), ('Critical', 'Critical')],
        validators=[DataRequired()]
        
    )

    submit = SubmitField('Create Ticket')

    
    
