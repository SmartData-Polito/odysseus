from odysseus.webapp.apis.__init__ import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    __tablename__ = 'user'
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password):
        self.email = email
        #self.username = email
        self.set_password(password)

    def is_active(self):
        """True, as all users are active."""
        return True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
        
    def __repr__(self):
        return '<User {}>'.format(self.username)  

    def register(self):
        print(self.email)
        db.session.add(self)
        db.session.commit()

def init_db():
    from odysseus.webapp.apis.__init__ import db
    db.create_all()

if __name__ == '__main__':
    init_db()