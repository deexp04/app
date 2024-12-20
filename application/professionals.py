from flask import Blueprint, jsonify, request
from application.models import User, Customer, Professional, Service, ServiceRequest
from functools import wraps
from application.routes import resume_format, profile_format, send_email_to_admin
from application.auth import role_required
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from application.extensions import db, bcrypt, cache
from application.celery.tasks import create_csv
from celery.result import AsyncResult
from flask import send_file

prof_bp = Blueprint('prof_bp', __name__)

@prof_bp.get('/celery')
def celery():
    s = ServiceRequest(service_id=1, customer_id=2, professional_id=1, status_updated_by='customer',
                       status='closed')
    db.session.add(s)
    db.session.commit()
    return 'hi'

@jwt_required()
@role_required(["admin"]) 
@prof_bp.get('/get-csv/<task_id>')
def getCSV(task_id):
    result = AsyncResult(task_id)

    if result.ready():
        return send_file(f'celery/user-downloads/{result.result}'), 200
    else:
        return {'message' : 'Task is not ready yet'}, 405

@jwt_required()
@role_required(["admin"]) 
@prof_bp.get('/create-csv')
def createCSV():
    task = create_csv.delay()
    return {'task_id' : task.id}, 200 



    