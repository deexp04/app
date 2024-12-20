from flask_restful import Resource, reqparse, fields, marshal
from application.extensions import api, db, cache
from application.models import ServiceRequest, User, Professional
from datetime import datetime
from application.auth import role_required
from flask_jwt_extended import jwt_required
from application.celery.tasks import professional_email_reminder, customer_email_reminder

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

service_request_parser = reqparse.RequestParser(bundle_errors=True)
service_request_parser.add_argument('id', type=int, help='Error: {error_msg}')
service_request_parser.add_argument('service_id', type=int, help='Error: {error_msg}')
service_request_parser.add_argument('customer_id', type=int, help='Error: {error_msg}')
service_request_parser.add_argument('professional_id', type=int, help='Error: {error_msg}')
service_request_parser.add_argument('date_of_request', type=lambda x: datetime.strptime(x, DATE_FORMAT), help='Error: {error_msg}')
service_request_parser.add_argument('date_of_completion', type=lambda x: datetime.strptime(x, DATE_FORMAT), help='Error: {error_msg}')
service_request_parser.add_argument('status_updated_by', type=str, help='Error: {error_msg}')
service_request_parser.add_argument('status', type=str, help='Error: {error_msg}')
service_request_parser.add_argument('remarks', type=str, help='Error: {error_msg}')

service_request_fields = {
    'id': fields.Integer,
    'service_id':fields.Integer,
    'customer_id': fields.Integer,
    'professional_id': fields.Integer,
    'date_of_request': fields.DateTime,
    'date_of_completion': fields.DateTime,
    'status_updated_by': fields.String,
    'status': fields.String,
    'remarks': fields.String
}

class ServiceRequestAPI(Resource):
    @jwt_required()
    @cache.cached(timeout = 5, key_prefix='service_request_data')
    def get(self, service_request_id):
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return {"message":"Service_request_id not found"}, 404
        
        return marshal(service_request,service_request_fields), 201
    
    @jwt_required()
    @role_required(["customer","professional"])
    def put(self, service_request_id):
        args = service_request_parser.parse_args(strict=True)
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return {"message":"Service_request_id not found"}, 404
        
        original_status = service_request.status

        for key,value in args.items():
            if value is not None:
                if key == 'customer_id':
                    return {"message": "Customer_id cannot be changed after creation"}, 403
                setattr(service_request, key, value)    

        if original_status != service_request.status and service_request.status == "closed":
            service_request.date_of_completion = datetime.now()

        db.session.commit()

        if original_status != service_request.status and (service_request.status == "accepted" or service_request.status == "rejected"):
            customer_email_reminder.delay(service_request.customer.user.email, service_request.customer.name, service_request.status, service_request.service.name)

        return {"message":"Service_request updated"}
    
    @jwt_required()
    @role_required(["customer"])
    def delete(self, service_request_id):
        service_request = ServiceRequest.query.get(service_request_id)

        if not service_request:
            return {"message":"Service_request_id not found. Could not delete the service request."}, 404
        
        if service_request.status == "accepted":
            return {"message": "Cannot delete this service request as your request is accepted by the professional."}, 400
        
        db.session.delete(service_request)
        db.session.commit()
        return {"message":"Service Request Deleted"}, 204   
    
class ServiceRequestListAPI(Resource):
    @jwt_required()
    @role_required(["admin"])
    @cache.cached(timeout = 5, key_prefix='service_request_list')
    def get(self):
        service_requests = ServiceRequest.query.all()
        if not service_requests:
            return {"message":"No service requests available"},404
        return marshal(service_requests, service_request_fields), 201            

    @jwt_required()
    @role_required(["customer"])
    def post(self):
        args = service_request_parser.parse_args(strict=True)
        new_service_request = ServiceRequest(**args)
        user = User.query.get(new_service_request.customer_id)
        professional = Professional.query.get(new_service_request.professional_id)

        if not user.customer:
            return {"message":"No such customer is available"}, 404
        
        new_service_request.customer_id = user.customer.id
        db.session.add(new_service_request)
        db.session.commit()

        professional_email_reminder.delay(user.customer.name, user.email, professional.user.email)

        return {"message":"Your service request is sent. Wait for sometime. Professional will get back to you soon."}, 201

api.add_resource(ServiceRequestListAPI, '/service-requests')
api.add_resource(ServiceRequestAPI, '/service-request/<int:service_request_id>')