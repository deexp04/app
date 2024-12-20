from flask_mail import Message
from flask import current_app as app, jsonify, send_from_directory, request
from application.extensions import mail
# from application.celery.tasks import create_csv
# from celery.result import AsyncResult
# from application.auth import role_required
# from flask_jwt_extended import jwt_required
# from flask import send_file
qqqqqqqqqqqqqqqqqqqqqqqq
def profile_format(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def resume_format(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

# with app.app_context():

#     @app.get('/application/static/resume/<filename>')
#     def serve_resume(filename):
#         return send_from_directory('static/resume', filename)

#     @app.get('/profile/<filename>')
#     def serve_profile(filename):
#         return send_from_directory('static/profile', filename)

# def send_dynamic_email(sender, recipient, subject, body):
#     msg = Message(subject=subject)
#     msg.body = body
    
#     # Set the dynamic sender and recipient
#     msg.sender = sender
#     msg.recipients = [recipient]

#     try:
#         mail.send(msg)
#         print(f"Email sent from {sender} to {recipient}")
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         return {"message": "Failed to send email"}, 500

# def send_email_to_admin(professional_name, professional_email, admin_email):
#     subject = "New Professional Registered"
#     body = f"A new professional has registered:\n\nName: {professional_name}\nEmail: {professional_email}\n\nPlease review and approve the registration."

#     return send_dynamic_email(sender=professional_email, recipient=admin_email, subject=subject, body=body)

def send_email_to_admin(professional_name, professional_email):
    subject = "New Professional Registered"
    body = f"A new professional has registered:\n\nName: {professional_name}\nEmail: {professional_email}\n\nPlease review and approve the registration."

    msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=["deebhika2004@gmail.com"])
    msg.body = body

    try:
        mail.send(msg)
        print("Email sent to admin successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify admin"}, 500
    
# @jwt_required()
# @role_required(["admin"]) 
# @app.get('/get-csv/<task_id>')
# def getCSV(task_id):
#     result = AsyncResult(task_id)

#     if result.ready():
#         return send_file(f'./application/celery/user-downloads/{result.result}'), 200
#     else:
#         return {'message' : 'Task is not ready yet'}, 405

# @jwt_required()
# @role_required(["admin"]) 
# @app.get('/create-csv')
# def createCSV():
#     task = create_csv.delay()
#     return {'task_id' : task.id}, 200
    
