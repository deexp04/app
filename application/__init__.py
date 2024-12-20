from flask import Flask, send_from_directory
from application.config import DevelopmentConfig
from application.auth import auth_bp
from application.admin import admin_bp
import application.admin
import application.resources.customer_api
import application.resources.prof_api
import application.resources.service_api
import application.resources.service_request_api
import application.resources.category_api
# from application.customers import api
from application.professionals import prof_bp
from application.models import User, Admin, Professional, Service
from application.celery.celery_factory import celery_init_app
from application.extensions import api, db, bcrypt, jwt, cors, mail, cache
from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies, get_jwt_identity
from datetime import datetime, timedelta, timezone
import flask_excel as excel

def create_app():
    app = Flask(__name__)

    #configure app before initialisation
    app.config.from_object(DevelopmentConfig)

    #initialise extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    bcrypt.init_app(app)
    api.init_app(app)
    cors.init_app(app, expose_headers=["Authorization","X-CSRF-TOKEN"], resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)

    app.app_context().push()

    #register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(prof_bp)

    @jwt.user_identity_loader
    def user_identity_lookup(id):
        return str(id)

    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        user = User.query.get(identity) 
        if user:
            return {
                "role": user.role
            }
        return {}

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        print(identity)
        return User.query.filter_by(id=identity).one_or_none()
    
    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            return response

    with app.app_context():
        db.create_all()

        # new_user = User(email='admin@gmail.com', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
        #                 role='admin')
        # db.session.add(new_user)
        # db.session.flush()  

        # new_admin = Admin(user_id=new_user.id)
        # db.session.add(new_admin)
        # db.session.commit()
            
        # import application.add_initial_data
        import application.routes

        @app.get('/application/static/resume/<filename>')
        def serve_resume(filename):
            return send_from_directory('static/resume', filename)

        @app.get('/profile/<filename>')
        def serve_profile(filename):
            return send_from_directory('static/profile', filename)
        
        @app.get('/approve-professional/<int:prof_id>')
        def approve_professional(prof_id):
            prof = Professional.query.get(prof_id)
            
            if not prof:
                return {"message": "Professional not found."}, 404
            
            if not prof.service_id:
                service = Service.query.filter_by(name=prof.service_name).first()
                if not service:
                    return {"message": "Professional can't be approved as the service_name didn't exist"}, 400
                prof.service_id = service.id
            
            if prof.status == 'approved':
                return {'message': 'Professional already approved'}, 400

            prof.status = 'approved'  
            db.session.commit()

            # send_approval_email.delay(prof.user_id, 'approved')

            return {'message': 'Professional approved and notified by email'}
        
        @app.get('/reject-professional/<int:prof_id>')
        def reject_professional(prof_id):
            prof = Professional.query.get(prof_id)
            
            if not prof:
                return {"message": "Professional not found."}, 404
            
            if prof.status == 'rejected':
                return {'message': 'Professional already rejected'}, 400

            prof.status = 'rejected'  
            db.session.commit()

            # send_approval_email.delay(prof.user_id, 'rejected')

            return {'message': 'Professional rejected and notified by email'}

        excel.init_excel(app)

    return app

app = create_app()









