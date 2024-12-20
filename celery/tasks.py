from celery import shared_task
from weasyprint import HTML
from io import BytesIO
from application.models import ServiceRequest, Professional, Customer
import flask_excel
from datetime import datetime, timedelta
from application.celery.mail_service import send_professional_notification, send_admin_notification, send_customer_notification, send_approval_notification
from flask_mail import Message
from application.extensions import mail
from application.celery.scheduled_mail import generate_pdf, send_email_with_pdf

@shared_task(bind = True, ignore_result = False)
def create_csv(self):
    resource = ServiceRequest.query.filter_by(status_updated_by='customer',status='closed').all()
    task_id = self.request.id
    filename = f'data_{task_id}.csv'
    column_names = [column.name for column in ServiceRequest.__table__.columns]
    csv_out = flask_excel.make_response_from_query_sets(query_sets = resource, column_names = column_names, file_type='csv' )
    print(csv_out)
    with open(f'../backend/application/celery/user-downloads/{filename}', 'wb') as file:
        file.write(csv_out.data)
    
    return filename

@shared_task(ignore_result = True)
def professional_approval_email(professional_email, professional_name, status):
    return send_approval_notification(professional_email, professional_name, status)

@shared_task(ignore_result = True)
def professional_email_reminder(customer_name, customer_email, professional_email):
    return send_professional_notification(customer_name, customer_email, professional_email)

@shared_task(ignore_result = True)
def check_service_requests():
    professionals = Professional.query.all()
    for professional in professionals:
        service_requests = ServiceRequest.query.filter_by(professional_id=professional.id, status="requested").all()

        if service_requests:
            subject = "New Service Requests"
            body = f"Hello {professional.name}, you have {len(service_requests)} new service request(s). Please log in to view them."
            
            msg = Message(subject=subject, sender="deebhika04@gmail.com", recipients=[professional.user.email])
            msg.body = body

            try:
                mail.send(msg)
                print("Email sent to professional successfully!")
                return {"message": "Email sent to professional successfully"}, 500
            
            except Exception as e:
                print(f"Error sending email: {e}")
                return {"message": "Failed to notify professional"}, 500
            
@shared_task(ignore_result = True)
def send_monthly_activity_reports():

    today = datetime.today()
    first_day_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_of_last_month = today.replace(day=1) - timedelta(days=1)

    customers = Customer.query.all()

    for customer in customers:
        service_requests = ServiceRequest.query.filter(
            ServiceRequest.customer_id == customer.id,
            ServiceRequest.date_of_request.between(first_day_of_last_month, today)
        ).all()

        total_services = len(service_requests)
        closed_services = sum(1 for sr in service_requests if sr.status == "closed")
        requested_services = total_services - closed_services

        print(service_requests)

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ text-align: center; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 10px;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <h1>Monthly Activity Report - {customer.name}</h1>
            <p>Report for the period: {first_day_of_last_month.strftime('%B %Y')}</p>
            <table>
                <thead>
                    <tr>
                        <th>Service Name</th>
                        <th>Status</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
        """

        for item in service_requests:
            html_content += f"""
                <tr>
                    <td>{item.service}</td>
                    <td>{item.status}</td>
                    <td>{item.date_of_request}</td>
                </tr>
            """

        html_content += """
                </tbody>
            </table>
            <div>
                <p>Total Services Requested: {total_services}</p>
                <p>Services Closed: {closed_services}</p>
                <p>Open Requests: {requested_services}</p>
            </div>
        </body>
        </html>
        """

        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0) 
        # return pdf_buffer

        # pdf_buffer = generate_pdf(service_requests, customer, first_day_of_last_month)

        send_email_with_pdf(
            recipient=customer.user.email,
            subject="Your Monthly Activity Report",
            body="Please find your monthly activity report attached.",
            pdf_buffer=pdf_buffer
        )

@shared_task(ignore_result = True)
def admin_email_reminder(professional_name, professional_email):
    return send_admin_notification(professional_name, professional_email)

@shared_task(ignore_result = True)
def customer_email_reminder(customer_email, customer_name, status, service_name):
    return send_customer_notification(customer_email, customer_name, status, service_name)