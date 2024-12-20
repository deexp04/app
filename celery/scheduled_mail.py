from weasyprint import HTML
from io import BytesIO
from datetime import date
from flask_mail import Message
from application.extensions import mail
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
def generate_pdf(service_requests, customer, first_day_of_last_month):
    
    total_services = len(service_requests)
    closed_services = sum(1 for sr in service_rqequests if sr.status == "closed")
    requested_services = total_services - closed_services

    html_content = f"""
    <html>qqqqqqq
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
                <td>{item['status']}</td>
                <td>{item.date_of_request}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
        <ul>
            <li>Total Services Requested: {total_services}</li>
            <li>Services Closed: {closed_services}</li>
            <li>Open Requests: {requested_services}</li>
        </ul>
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0) 
    return pdf_buffer

def send_email_with_pdf(recipient, subject, body, pdf_buffer):

    msg = Message(
        subject=subject,
        sender="deebhika04@gmail.com",
        recipients=[recipient],
        body=body,
    )

    msg.attach(f"monthly_report_{date.today().strftime('%Y_%m')}.pdf", "application/pdf", pdf_buffer.read())

    try:
        mail.send(msg)
        print("Email sent to customer successfully!")
        return {"message": "Email sent to {recipient_email} with PDF attached."}, 500
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return {"message": "Failed to notify customer"}, 500
