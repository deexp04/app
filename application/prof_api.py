from flask_restful import Resource, reqparse, fields, marshal, request
from application.extensions import api, db, bcrypt, cache
from application.models import Professional, User, Service, ServiceRequest
from flask import url_for
import os
from application.routes import resume_format, profile_format
from werkzeug.utils import secure_filename
from application.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.celery.tasks import admin_email_reminder, professional_approval_email

prof_resource_parser = reqparse.RequestParser()
prof_resource_parser.add_argument('id', type=int, help='Error: {error_msg}')
prof_resource_parser.add_argument('user_id', type=int, help='Error: {error_msg}')
prof_resource_parser.add_argument('name', type=str, help='Error: {error_msg}')
prof_resource_parser.add_argument('service_name', type=str, help='Error: {error_msg}')
prof_resource_parser.add_argument('contact_no', type=int, help='Error: {error_msg}')
prof_resource_parser.add_argument('experience', type=str, help='Error: {error_msg}')
prof_resource_parser.add_argument('address', type=str, help='Error: {error_msg}')
prof_resource_parser.add_argument('pincode', type=int, help='Error: {error_msg}')
prof_resource_parser.add_argument('status', type=str, help='Error: {error_msg}')
prof_resource_parser.add_argument('flag', type=bool, help='Error: {error_msg}')
prof_resource_parser.add_argument('rating', type=float, help='Error: {error_msg}')
prof_resource_parser.add_argument('service_id', type=int, help='Error: {error_msg}')

prof_resource_fields = {
    'id': fields.Integer,
    'user_id':fields.Integer,
    'name': fields.String,
    'service_name': fields.String,
    'contact_no':fields.Integer,
    'profile_pic':fields.String,
    'experience': fields.String,
    'address': fields.String,
    'pincode': fields.Integer,
    'status': fields.String,
    'rating':fields.Float,
    'flag':fields.Boolean,
    'service_id': fields.Integer,
    'resume': fields.String 
}

class ProfessionalAPI(Resource):
    @jwt_required()
    @cache.cached(timeout = 5, key_prefix='professional_data')
    def get(self, professional_id):
        professional = Professional.query.get(professional_id)
        
        if not professional:
            return {"message": "Professional_id not found"}, 404
        
        if professional.resume and os.path.exists(professional.resume):
            try:
                filename = os.path.basename(professional.resume)
                professional.resume = url_for('serve_resume', filename=filename, _external=True)

            except Exception as e:
                return {"message": f"Failed to retrieve the PDF: {str(e)}"}, 500
        else:
            professional.resume = None

        if professional.profile_pic and os.path.exists(professional.profile_pic):
            try:
                filename = os.path.basename(professional.profile_pic)
                professional.profile_pic = url_for('serve_profile', filename=filename, _external=True)
            except Exception as e:
                return {"message": f"Failed to retrieve the Profile: {str(e)}"}, 500
        else:
            professional.profile_pic = None

        return marshal(professional, prof_resource_fields), 200

    @jwt_required()
    @role_required(["professional","admin"])
    def put(self, professional_id):
        data = prof_resource_parser.parse_args()
        professional = Professional.query.get(professional_id)
        if not professional:
            return {"message": "Professional_id not found"}, 404
        
        if 'profile_pic' in request.files:
            profile = request.files['profile_pic']
            
            if profile.filename == '':
                return {"message": 'No selected profile'}, 400
            
            if not profile_format(profile.filename):
                return {"message": 'File type not allowed'}, 400
    
            filename = secure_filename(profile.filename)
            path = os.path.join('application/static/profile/', filename)
            profile.save(path)
            professional.profile_pic = path

        original_status = professional.status

        for key,value in data.items():
            if value is not None:
                setattr(professional, key, value)

        if original_status != professional.status and professional.status == "approved":
            if not professional.service_id:
                service = Service.query.filter_by(name=professional.service_name).first()
                if not service:
                    return {"message": "Professional can't be approved as the service_name doesn't exist."}, 400
                
                professional.service_id = service.id

            professional_approval_email.delay(professional.user.email, professional.name, professional.status)

        if original_status != professional.status and professional.status == "rejected":
            professional_approval_email.delay(professional.user.email, professional.name, professional.status)
            
        db.session.commit()
            
        return {"message":"Professional details updated"}, 200
    
    @jwt_required()
    @role_required(["professional","admin"])
    def delete(self, professional_id):
        professional = Professional.query.get(professional_id)
        if not professional:
            return {"message":"Professional_id not found"}, 404
        db.session.delete(professional.user)
        db.session.commit()
        return {"message":"Professional_id removed from database"}, 204
    
class ProfessionalListAPI(Resource):
    @jwt_required()
    @cache.cached(timeout = 5, key_prefix='professional_list')
    def get(self):
        professionals = Professional.query.all()
        if not professionals:
            return {"message":"No professionals available"},404
        
        for prof in professionals:
            if prof.profile_pic and os.path.exists(prof.profile_pic):
                filename = os.path.basename(prof.profile_pic)
                prof.profile_pic = url_for('serve_profile', filename=filename, _external=True)
            else:
                prof.profile_pic = None     
                
        return marshal(professionals, prof_resource_fields), 201
    
    def post(self):
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        name = request.form.get('name', None)
        service_name = request.form.get('service_name', None)

        if not all([email, password, name, service_name]):
            return {"message": "All details not provided"}, 400

        if 'resume' not in request.files:
            return {'message':'No file exists'}, 400
        
        resume = request.files['resume']

        if resume.filename == '':
                return {'message':'No selected file'}, 400
        
        if not resume_format(resume.filename):
            return {'message': 'File type not allowed, only PDFs are allowed'}, 400
        
        if User.query.filter_by(email=email).first():
            return {"message": "User already exists"}, 409
        
        resume_path = None
        path = os.path.join('application/static/resume/', secure_filename(resume.filename))
        os.makedirs(os.path.dirname(path), exist_ok=True)  

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            resume.save(path)
            resume_path = path
            new_user = User(email=email, password=hashed_password, role='professional')
            db.session.add(new_user)
            db.session.flush()  

            service = Service.query.filter_by(name=service_name).first()
            service_id = service.id if service else None
            
            new_professional = Professional(user_id=new_user.id, name=name, 
                                            service_name=service_name, service_id=service_id, resume=resume_path)
            db.session.add(new_professional)
            db.session.commit()

            admin_email_reminder.delay(name, email)

            return {"message": "Customer created successfully"}, 201
        
        except Exception as e:
            db.session.rollback()
            if os.path.exists(path):
                os.remove(path)
            return {"message": str(e)}, 500 
    
    
api.add_resource(ProfessionalAPI, '/professional/<int:professional_id>')
api.add_resource(ProfessionalListAPI, '/professionals')

# class CustomerRequestToProfessionalAPI(Resource):
#     @jwt_required()
#     @role_required(["customer"])
#     def post(self):
#         """
#         Allows a customer to send a service request to a professional.
#         """
#         data = request.get_json()
#         professional_id = data.get("professional_id")
#         service_id = data.get("service_id")
#         description = data.get("description")  # Optional details from the customer

#         # Validate inputs
#         if not professional_id or not service_id:
#             return {"message": "Professional ID and Service ID are required."}, 400

#         # Fetch the professional and service
#         professional = Professional.query.get(professional_id)
#         service = Service.query.get(service_id)

#         if not professional or not service:
#             return {"message": "Invalid professional or service ID."}, 404

#         # Create a new service request
#         service_request = ServiceRequest(
#             customer_id=get_jwt_identity(),  # Assuming JWT provides customer ID
#             professional_id=professional_id,
#             service_id=service_id,
#             description=description,
#             status="Pending"  # Initial status
#         )

#         db.session.add(service_request)
#         db.session.commit()

#         return {"message": "Service request sent successfully.", "request_id": service_request.id}, 201

#     @jwt_required()
#     @role_required(["customer", "admin"])
#     def get(self):
#         """
#         Retrieve service requests made by the customer.
#         """
#         customer_id = get_jwt_identity()

#         # Fetch service requests for the logged-in customer
#         requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()

#         return {
#             "service_requests": [
#                 {
#                     "id": sr.id,
#                     "professional_name": sr.professional.user.name,
#                     "service_name": sr.service.name,
#                     "status": sr.status,
#                     "created_at": sr.created_at
#                 }
#                 for sr in requests
#             ]
#         }, 200

# api.add_resource(CustomerRequestToProfessionalAPI, '/api/customer/request')



# class ServiceRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
#     professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=False)
#     service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
#     description = db.Column(db.String(255), nullable=True)
#     status = db.Column(db.String(50), default="Pending")
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     customer = db.relationship('Customer', backref='service_requests', lazy=True)
#     professional = db.relationship('Professional', backref='service_requests', lazy=True)
#     service = db.relationship('Service', backref='service_requests', lazy=True)

class ProfessionalServiceRequestsAPI(Resource):
    @jwt_required()
    @role_required(["professional"])
    def get(self):
        user = User.query.get(get_jwt_identity())
        statuses = request.args.getlist('status')  

        query = ServiceRequest.query.filter_by(professional_id=user.professional.id)

        if statuses:
            # query = query.filter(or_(*[ServiceRequest.status == status for status in statuses]))
            query = query.filter(ServiceRequest.status.in_(statuses))

        requests = query.all()

        if not requests:
            return {"message": "No service requests found."}, 404

        return {
            "service_requests": [
                {
                    "id": sr.id,
                    "customer_name": sr.customer.name,
                    "customer_email": sr.customer.user.email,
                    "customer_no":sr.customer.contact_no,
                    "customer_pincode":sr.customer.pincode,
                    "service_name": sr.service.name,
                    "date_of_completion": sr.date_of_completion.isoformat() if sr.date_of_completion else None,
                    "description": sr.service.description,
                    "status": sr.status,
                }
                for sr in requests
            ]
        }, 200

class ProfessionalServiceRequestDetailAPI(Resource):
    @jwt_required()
    @role_required(["professional"])
    def get(self, request_id):

        user = User.query.get(get_jwt_identity())

        service_request = ServiceRequest.query.filter_by(
            id=request_id, professional_id=user.professional.id
        ).first()

        if not service_request:
            return {"message": "Service request not found."}, 404

        return {
            "id": service_request.id,
            "customer_name": service_request.customer.name,
            "customer_email": service_request.customer.user.email,
            "service_name": service_request.service.name,
            "description": service_request.service.description,
            "status": service_request.status,
        }, 200


api.add_resource(ProfessionalServiceRequestsAPI, '/professional/requests')
api.add_resource(ProfessionalServiceRequestDetailAPI, '/professional/request/<int:request_id>')



