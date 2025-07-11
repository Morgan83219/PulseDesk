import os # Accessing operating system dependandant functionality

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Development_Secret_Key') # declaring secret key for session management
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') # delcaring the database engine to use: SQLite and to connect to the database named app.db
    SQLALCHEMY_TRACK_MODIFICATIONS = False #turning off event tracking to free up system resources
    
