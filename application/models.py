from application.extensions import db, bcrypt
from datetime import datetime
from sqlalchemy import event

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    admin = db.relationship('Admin', uselist=False, cascade="all,delete,save-update", backref='user')
    customer = db.relationship('Customer', uselist=False, cascade="all,delete,save-update", backref='user')
    professional = db.relationship('Professional', uselist=False, cascade="all,delete,save-update", backref='user')

    def __repr__(self):
        return f'<User {self.email}>'
    
class Admin(db.Model):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Admin {self.user.email}>'

class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.Integer, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=False)  
    flag = db.Column(db.Boolean, nullable=True, default=False)
    service_requests = db.relationship('ServiceRequest',cascade="all,delete",backref="customer")

    def __repr__(self):
        return f'<Customer {self.user.email}>'

@event.listens_for(Customer, 'before_insert')
def set_default_customer_profile(mapper, connection, target):
    if not target.profile_pic:  
        target.profile_pic = 'application/static/profile/default_profile_pic.jpeg'

class Professional(db.Model):
    __tablename__ = 'professional'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    contact_no = db.Column(db.Integer, nullable=True)
    experience = db.Column(db.String(20), nullable=True)
    resume = db.Column(db.String(255), nullable=False)  
    profile_pic = db.Column(db.String(255), nullable=False)  
    address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='unapproved')
    rating = db.Column(db.Float, nullable=False, default=0.0)
    flag = db.Column(db.Boolean, nullable=True, default=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service_requests = db.relationship('ServiceRequest',cascade="all,delete",backref="professional")
    # description, date created

    def __repr__(self):
        return f'<Professional {self.user.email}>'

@event.listens_for(Professional, 'before_insert')
def set_default_prof_profile(mapper, connection, target):
    if not target.profile_pic:  
        target.profile_pic = 'application/static/profile/default_profile_pic.jpeg'

CATEGORY_IMAGE = {
    'cleaning': 'https://images.pexels.com/photos/3768910/pexels-photo-3768910.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2',
    'plumbing': 'https://example.com/images/plumbing.jpg',
    'electricians': 'https://example.com/images/electricians.jpg',
}

class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Float,  nullable=False)
    time_req = db.Column(db.Float,  nullable=False)
    category = db.Column(db.String(50), nullable=False)
    category_image = db.Column(db.String(255), nullable=True)
    professionals = db.relationship('Professional',cascade="all,delete",backref="service")
    service_requests = db.relationship('ServiceRequest',cascade="all,delete",backref="service")

@event.listens_for(Service, 'before_insert')
def set_default_category_image(mapper, connection, target):
    if not target.category_image:  
        target.category_image = CATEGORY_IMAGE.get(target.category, 'https://example.com/images/default.jpg')

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.now)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    status_updated_by = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='requested')
    remarks = db.Column(db.String,  nullable=True)
    # add rating