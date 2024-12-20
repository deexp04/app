from flask import Blueprint, jsonify, request
# from application import celery
from flask_restful import Resource, reqparse, fields, marshal
from application.extensions import api, db
from application.auth import role_required
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt
from application.models import Professional, Customer, Service
# from flask_mail import Message
# from application import mail  

admin_bp = Blueprint('admin', __name__)

@admin_bp.get('/admin-home/<int:user_id>')
@jwt_required()
@role_required(["admin"])
def admin_home(user_id):
    print(request.headers)
    try:
        verify_jwt_in_request()
        token_data = get_jwt()
        print("JWT Payload:", token_data)
    except Exception as e:
        print("Error processing JWT:", e)
    return 'Admin Home'


