from flask_mail import Message
from application.extensions import mail

def send_professional_notification(customer_name, customer_email, professional_email):
    subject = "New Service Request"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
            }}
            .header img {{
                width: 50px;
                height: auto;
            }}
            .content {{
                padding: 20px;
                line-height: 1.6;
            }}
            .content h2 {{
                color: #007bff;
                margin-bottom: 20px;
            }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #007bff;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Service Request Notification</h1>
            </div>
            <div class="content">
                <h2>Hello Professional,</h2>
                <p>
                    A customer has requested your service. Please review the details below:
                </p>
                <strong>CUSTOMER NAME:</strong> {customer_name}
                <strong>CUSTOMER EMAIL:</strong> {customer_email}
                <p>
                    Please log in to your account to view more details and approve the request.
                </p>
                <a href="" class="button">View Service Request</a>
            </div>
            <div class="footer">
                <p>
                    This is an automated message. Please do not reply directly to this email.
                </p>
                <p>© 2024 Household Services. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=[professional_email])
    msg.html = body_html

    try:
        mail.send(msg)
        print("Email sent to professional successfully!")
        return {"message": "Email sent to professional successfully"}, 500
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify professional"}, 500

def send_admin_notification(professional_name, professional_email):
    subject = "New Professional Registered"

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
            }}
            .header img {{
                width: 50px;
                height: auto;
            }}
            .content {{
                padding: 20px;
                line-height: 1.6;
            }}
            .content h2 {{
                color: #007bff;
                margin-bottom: 20px;
            }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #007bff;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Professional Request Notification</h1>
            </div>
            <div class="content">
                <h2>Hello Admin,</h2>
                <p>
                    A new professional has been registered. 
                </p>
                <strong>PROFESSIONAL NAME:</strong> {professional_name}
                <strong>PROFESSIONAL EMAIL:</strong> {professional_email}
                <p>
                    Please log in to your account to review the details and approve the request.
                </p>
                <a href="" class="button">View Request</a>
            </div>
            <div class="footer">
                <p>
                    This is an automated message. Please do not reply directly to this email.
                </p>
                <p>© 2024 Household Services. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # use admin email in recipients
    msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=["deebhika2004@gmail.com"])
    msg.html = body_html

    try:
        mail.send(msg)
        print("Email sent to admin successfully!")
        return {"Email sent to admin successfully"}, 200
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify admin"}, 500
    
def send_customer_notification(customer_email, customer_name, status, service_name):
    subject = f"Service Request {status.capitalize()}"
    body = (
        f"Dear {customer_name},\n\n"
        f"Your service request for '{service_name}' has been {status} by the professional. Professional has {status} your service request."
    )

    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                color: #333;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                text-align: center;
                padding: 20px;
                border-radius: 10px 10px 0 0;
            }}
            .header img {{
                width: 50px;
                height: auto;
            }}
            .content {{
                padding: 20px;
                line-height: 1.6;
            }}
            .content h2 {{
                color: #007bff;
                margin-bottom: 20px;
            }}
            .button {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #007bff;
                color: #ffffff;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                padding: 10px;
                font-size: 12px;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Professional Request Notification</h1>
            </div>
            <div class="content">
                <h2>Hello Admin,</h2>
                <p>
                    A new professional has been registered. 
                </p>
                <strong>PROFESSIONAL NAME:</strong> {professional_name}
                <strong>PROFESSIONAL EMAIL:</strong> {professional_email}
                <p>
                    Please log in to your account to review the details and approve the request.
                </p>
                <a href="" class="button">View Request</a>
            </div>
            <div class="footer">
                <p>
                    This is an automated message. Please do not reply directly to this email.
                </p>
                <p>© 2024 Household Services. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    #sender != admin email .. deebhika04 email is used as sender in all emails
    msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=[customer_email])
    msg.html = body_html

    try:
        mail.send(msg)
        print("Email sent to customer successfully!")
        return {"message": "Email sent to customer successfully"}, 500
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify customer"}, 500

def send_approval_notification(professional_email, professional_name, status):
    if status == "rejected" or "unapproved":
        subject = f"Status Update: Your Professional Account Has Been {status.capitalize()}"
        body = (
            f"Dear {professional_name},\n\n"
            f"We regret to inform you that your account status has been updated to '{status}'. "
            f"If you have any questions, please contact support.\n\n"
            f"Thank you,\nTeam"
        )
    elif status == "approved":
        subject = "Congratulations! Your Professional Account Has Been Approved"
        body = (f"Dear {professional_name},\n\n"
            f"Congratulations! Your professional account has been approved. You can now log in and start offering services on our platform.\n\n"
            f"Thank you,\nTeam")
    
    #sender != admin email .. can also be admin mail.. deebhika04 email is used as sender in all emails
    msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=[professional_email])
    msg.body = body

    try:
        mail.send(msg)
        print("Email sent to professional successfully!")
        return {"message": "Email sent to professional successfully"}, 500
    
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify professional"}, 500
    
