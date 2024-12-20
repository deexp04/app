from flask_restful import Resource, reqparse, fields, marshal, request
from application.extensions import api, db, bcrypt, cache
from flask import url_for
from werkzeug.utils import secure_filename
from application.models import Customer, User, ServiceRequest
from application.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.routes import profile_format
import os
from sqlalchemy import or_

customer_resource_parser = reqparse.RequestParser(bundle_errors=True)
customer_resource_parser.add_argument('id', type=int, help='Error: {error_msg}')
customer_resource_parser.add_argument('user_id', type=int, help='Error: {error_msg}')
customer_resource_parser.add_argument('email', type=str, help='Error: {error_msg}')
customer_resource_parser.add_argument('password', type=str, help='Error: {error_msg}')
customer_resource_parser.add_argument('name', type=str, help='Error: {error_msg}')
customer_resource_parser.add_argument('address', type=str, help='Error: {error_msg}')
customer_resource_parser.add_argument('contact_no', type=int, help='Error: {error_msg}')
customer_resource_parser.add_argument('pincode', type=int, help='Error: {error_msg}')
customer_resource_parser.add_argument('flag', type=bool, help='Error: {error_msg}')

customer_resource_fields = {
    'id': fields.Integer,
    'user_id':fields.Integer,
    'name': fields.String,
    'contact_no':fields.Integer,
    'profile_pic':fields.String,
    'address': fields.String,
    'pincode': fields.Integer,
    'flag':fields.Boolean
}

class CustomerAPI(Resource):
    @jwt_required()
    @cache.cached(timeout = 5, key_prefix='customer_data')
    def get(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            return {"message": "Customer_id not found"}, 404
        
        if customer.profile_pic and os.path.exists(customer.profile_pic):
            try:
                filename = os.path.basename(customer.profile_pic)
                customer.profile_pic = url_for('serve_profile', filename=filename, _external=True)
            except Exception as e:
                return {"message": f"Failed to retrieve the Profile: {str(e)}"}, 500
        else:
            customer.profile_pic = None  

        return marshal(customer, customer_resource_fields), 201

    @jwt_required()
    @role_required(["customer","admin"])
    def put(self, customer_id):
        data = customer_resource_parser.parse_args()
        customer = Customer.query.get(customer_id)
        if not customer:
            return {"message": "Customer_id not found"}, 404
        
        if 'profile_pic' in request.files:
            profile = request.files['profile_pic']
            
            if profile.filename == '':
                return {"message": 'No selected profile'}, 400
            
            if not profile_format(profile.filename):
                return {"message": 'File type not allowed'}, 400
    
            filename = secure_filename(profile.filename)
            path = os.path.join('application/static/profile/', filename)
            profile.save(path)
            customer.profile_pic = path
            
        for key,value in data.items():
            if value is not None:
                setattr(customer, key, value)
        db.session.commit()
        return {"message":"Customer details updated"}, 200
    
    @jwt_required()
    @role_required(["customer","admin"])
    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            return {"message":"Customer_id not found"}, 404
        db.session.delete(customer.user)
        db.session.commit()
        return {"message":"Customer_id removed from database"}, 204
    
class CustomerListAPI(Resource):
    @jwt_required()
    @cache.cached(timeout = 5, key_prefix='customer_list')
    def get(self):
        customers = Customer.query.all()
        if not customers:
            return {"message":"No customers available"},404

        for customer in customers:
            if customer.profile_pic and os.path.exists(customer.profile_pic):
                filename = os.path.basename(customer.profile_pic)
                customer.profile_pic = url_for('serve_profile', filename=filename, _external=True)
            else:
                customer.profile_pic = None     

        return marshal(customers, customer_resource_fields), 201
    
    def post(self):
        data = customer_resource_parser.parse_args()
        email = data.get('email', None)
        password = data.get('password', None)
        name = data.get('name', None)
        contact_no = data.get('contact_no', None)

        if not all([email, password, name, contact_no]):
            return {"message": "All details not provided"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "User already exists"}, 409

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(email=email, password=hashed_password, role='customer')
            db.session.add(new_user)
            db.session.flush()  

            new_customer = Customer(user_id=new_user.id, name=name, contact_no=contact_no)
            db.session.add(new_customer)
            db.session.commit()

            return {"message": "Customer created successfully"}, 201
        
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500 
    
api.add_resource(CustomerListAPI, '/customers')
api.add_resource(CustomerAPI, '/customer/<int:customer_id>')

class CustomerServiceRequestsAPI(Resource):
    @jwt_required()
    @role_required(["customer"])
    def get(self):
        user = User.query.get(get_jwt_identity())
        statuses = request.args.getlist('status')  

        query = ServiceRequest.query.filter_by(customer_id=user.customer.id)

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
                    "professional_name": sr.professional.name,
                    "professional_email": sr.professional.user.email,
                    "professional_no":sr.professional.contact_no,
                    "service_name": sr.service.name,
                    "date_of_completion": sr.date_of_completion.isoformat() if sr.date_of_completion else None,
                    "description": sr.service.description,
                    "status": sr.status,
                }
                for sr in requests
            ]
        }, 200

class CustomerServiceRequestDetailAPI(Resource):
    @jwt_required()
    @role_required(["customer"])
    def get(self, request_id):

        user = User.query.get(get_jwt_identity())

        service_request = ServiceRequest.query.filter_by(
            id=request_id, customer_id=user.customer.id
        ).first()

        if not service_request:
            return {"message": "Service request not found."}, 404

        return {
            "id": service_request.id,
            "professional_name": service_request.professional.name,
            "professional_email": service_request.professional.user.email,
            "service_name": service_request.service.name,
            "description": service_request.service.description,
            "status": service_request.status,
        }, 200


api.add_resource(CustomerServiceRequestsAPI, '/customer/requests')
api.add_resource(CustomerServiceRequestDetailAPI, '/customer/request/<int:request_id>')