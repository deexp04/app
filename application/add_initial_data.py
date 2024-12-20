from flask import current_app as app
from application.extensions import db, bcrypt
from application.models import User, Admin, Customer, Professional

with app.app_context():
    db.create_all()
    
    # new_user = User(email='admin5@gmail.com', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
    #                  role='admin')
    # db.session.add(new_user)
    # db.session.flush()  

    # new_admin = Admin(user_id=new_user.id)
    # db.session.add(new_admin)
    # db.session.commit()

    # new_user = User(email='prof@gmail.com', password='1234', role='professional')
    # db.session.add(new_user)
    # db.session.flush()  

    # new_professional = Professional(user_id=new_user.id, name='prof', service_name='carpenter', 
    #                                 pdf_path='application/static/img/proofs/abcd.pdf')
    # db.session.add(new_professional)
    # db.session.commit()

    # new_user = User(email='deep@gmail.com', password='1234', role='professional')
    # db.session.add(new_user)
    # db.session.flush()  

    # new_professional = Professional(user_id=new_user.id, name='deepika', service_name='plumbing', 
    #                                 experience=2, pdf_path='application/static/img/proofs/efgh.pdf', address='tambaram', pincode='4355')
    # db.session.add(new_professional)
    # db.session.commit()

