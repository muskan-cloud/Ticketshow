import os
import csv
from models import User, theater as theater_model, show as show_model,ShowTheater as show_thmodel,bookings,db,ShowRating,Role
from datetime import datetime, timedelta
from worker import celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy import and_

from jinja2 import Template


SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "ticket_show@email.com"
SENDER_PASSWORD = ""

def format_duration(duration_in_seconds):
        hours, remainder = divmod(duration_in_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"

@celery.task(bind=True)
def export_theater_shows_csv(self, theater_id):
    
        theater = theater_model.query.filter_by(theater_id=theater_id).first()
        shows = show_model.query.filter_by(ts_id=theater.theater_id)

        csv_folder_path = os.path.join(os.getcwd(), 'csv_files')

        if not os.path.exists(csv_folder_path):
            os.makedirs(csv_folder_path)

        fieldnames = ['Show ID', 'Show Name', 'Show Genre/Description', 'Show price', 'Show Rating', 'Show Time','Show Duration', 'Total_Bookings',
                  'Theater ID']

        csv_file_path = os.path.join(csv_folder_path, f'theater_shows_{self.request.id}.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for show in shows:
                tb = show_thmodel.query.filter_by(show_id=show.show_id).first()
                writer.writerow({
                'Show ID': show.show_id,
                'Show Name': show.show_name,
                'Show Genre/Description': show.show_description,
                'Show price': show.show_price,
                'Show Rating': show.show_rating,
                'Show Time':show.show_timing,
                'Show Duration':format_duration(show.show_duration),
                'Total_Bookings':tb.total_bookings,
                'Theater ID': show.ts_id
            })

        return {'csv_file_path': csv_file_path}

@celery.task(bind=True)
def export_user_csv(self, user_id):
        bookings_all=bookings.query.filter_by(user_id=user_id).all()

        csv_folder_path = os.path.join(os.getcwd(), 'csv_files')

        if not os.path.exists(csv_folder_path):
            os.makedirs(csv_folder_path)

        fieldnames = ['Booking Id','Show Name', 'Theater Name','Show price', 'Your Rating', 'Show Time','Show Duration', 'Total_tickets','Seat Numbers']

        csv_file_path = os.path.join(csv_folder_path, f'report_{self.request.id}.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for booking in bookings_all:
                show = show_model.query.filter_by(show_id=booking.show_id).first()
                theater = theater_model.query.filter_by(theater_id=show.ts_id).first()
                rating = ShowRating.query.filter_by(user_id=user_id,show_id=show.show_id).first()


                writer.writerow({
                'Booking Id':booking.booking_id,
                'Show Name': show.show_name,
                'Theater Name':theater.theater_name,
                'Show price': show.show_price,
                'Your Rating': rating.user_rating if rating else 0,
                'Show Time':show.show_timing,
                'Show Duration':format_duration(show.show_duration),
                'Total_tickets':booking.booking_tickets_count,
                'Seat Numbers' :f"'{booking.seat_range}'"
            })

        return {'csv_file_path': csv_file_path}

from json import dumps

from httplib2 import Http

WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAAAdGe_8Qw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=xO2_MwB96-0lwCHCEatV8ecnIHO6qJIFAa0ttpcz_MQ"

@celery.task
def send_reminder():
    
    url = WEBHOOK_URL
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

    users_without_booking = User.query.join(User.roles).filter(and_(Role.name == 'user', ~User.id.in_(db.session.query(bookings.user_id).filter(bookings.booking_time >= twenty_four_hours_ago)))).all()


    if not users_without_booking:
        return "No reminders sent. All users have booked shows recently."

    for user in users_without_booking:
        reminder_message = f"Dear {user.username}, you haven't booked any show in the last 24 hours. Please check the available shows."

        send_gspace_message(reminder_message)

    return f"Reminders sent to {len(users_without_booking)} users who haven't booked in the last 24 hours."

def send_gspace_message(message):
    url = WEBHOOK_URL
    bot_message = {'text': message}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )
    print(response)




from sqlalchemy import extract


#common
def send_email(to_address, subject, message, content="text", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
        )
        
        msg.attach(part)

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True


def generate_monthly_progress_report(user_id):    
    current_month = datetime.now().month
    user = User.query.filter_by(id=user_id).first()
    
    bookings_data = bookings.query.filter(extract('month', bookings.booking_time) == current_month,bookings.user_id == user.id).all()
    show_ids = [booking.show_id for booking in bookings_data]
    shows_seen = show_model.query.filter(show_model.show_id.in_(show_ids)).all()
    ratings = ShowRating.query.filter(ShowRating.user_rating.isnot(None), ShowRating.show_id.in_(show_ids)).all()
    booking_show_names = {}
    for booking in bookings_data:
        show = show_model.query.filter_by(show_id=booking.show_id).first()
        booking_show_names[booking.show_id] = show.show_name
    username=user.username

    with open('monthly_report.html', 'r') as template_file:
        template_content = template_file.read()
    template = Template(template_content)

    report_html = template.render(bookings_data=bookings_data, shows_seen=shows_seen, ratings=ratings,username=username,booking_show_names=booking_show_names)

    return report_html

def generate_complete_entertainment_report(user_id):    
    user = User.query.filter_by(id=user_id).first()    
    bookings_data = bookings.query.filter(bookings.user_id == user.id).all()
    show_ids = [booking.show_id for booking in bookings_data]
    shows_seen = show_model.query.filter(show_model.show_id.in_(show_ids)).all()
    ratings = ShowRating.query.filter(ShowRating.user_rating.isnot(None), ShowRating.show_id.in_(show_ids)).all()
    booking_show_names = {}
    for booking in bookings_data:
        show = show_model.query.filter_by(show_id=booking.show_id).first()
        booking_show_names[booking.show_id] = show.show_name
    username=user.username

    with open('complete_report.html', 'r') as template_file:
        template_content = template_file.read()

    
    template = Template(template_content)

    report_html = template.render(bookings_data=bookings_data, shows_seen=shows_seen, ratings=ratings,username=username,booking_show_names=booking_show_names)

    return report_html



def generate_monthly_theaters_report(user_id):
    current_month = datetime.now().month
    current_month_name = datetime.now().strftime('%B')
    user = User.query.filter_by(id=user_id).first()

    theaters = theater_model.query.filter_by(ut_id=user.id)
    theater_data = []

    for theater in theaters:
        shows = show_model.query.filter(
            extract('month', show_model.show_timing) == current_month,
            show_model.ts_id == theater.theater_id
        ).all()
        
        if not shows:
            continue
        
        theater_capacity = theater.theater_capacity
        total_theater_revenue = 0
        show_data = []

        for show in shows:
            show_name = show.show_name
            show_ratings = show.show_rating
            show_time = show.show_timing
            show_duration = format_duration(show.show_duration)
            show_theater = show_thmodel.query.filter_by(show_id=show.show_id).first()
            show_total_bookings = show_theater.total_bookings
            show_total_revenue = show_total_bookings * show.show_price
            total_theater_revenue += show_total_revenue

            show_data.append({
                'show_name': show_name,
                'show_ratings': show_ratings,
                'show_total_bookings': show_total_bookings,
                'show_time': show_time,
                'show_duration' : show_duration,
                'show_total_revenue': show_total_revenue
            })

        theater_data.append({
            'theater_name': theater.theater_name,
            'theater_capacity': theater_capacity,
            'theater_total_revenue': total_theater_revenue,
            'shows': show_data
        })

    with open('monthly_theaters_report.html', 'r') as template_file:
        template_content = template_file.read()

    template = Template(template_content)
    admin_report_html = template.render(user=user, theater_data=theater_data, username=user.username, total_admin_revenue=sum(t['theater_total_revenue'] for t in theater_data),current_month = current_month_name )

    return admin_report_html


def generate_complete_theaters_report(user_id):
    current_month = datetime.now().month
    user = User.query.filter_by(id=user_id).first()

    theaters = theater_model.query.filter_by(ut_id=user.id)
    theater_data = []

    for theater in theaters:
        shows = show_model.query.filter(show_model.ts_id == theater.theater_id).all()

        if not shows:
            continue

        theater_capacity = theater.theater_capacity
        show_data = []
        theater_total_revenue = 0

        for show in shows:
            show_name = show.show_name
            show_ratings = show.show_rating
            show_time = show.show_timing
            show_duration = show.show_duration
            show_theater = show_thmodel.query.filter_by(show_id=show.show_id).first()
            show_total_bookings = show_theater.total_bookings
            total_revenue = 0
            for booking in show.bookings:
                total_revenue += booking.booking_tickets_count * show.show_price

            formatted_duration = format_duration(show_duration)
            show_data.append({
                'show_name': show_name,
                'show_ratings': show_ratings,
                'show_total_bookings': show_total_bookings,
                'show_time': show_time,
                'show_duration': formatted_duration,
                'show_total_revenue': total_revenue,
            })

            theater_total_revenue += total_revenue

        theater_data.append({
            'theater_name': theater.theater_name,
            'theater_capacity': theater_capacity,
            'shows': show_data,
            'theater_total_revenue': theater_total_revenue,
        })

    with open('theater_shows.html', 'r') as template_file:
        template_content = template_file.read()

    template = Template(template_content)

    
    total_admin_revenue = sum(theater['theater_total_revenue'] for theater in theater_data)

    admin_report_html = template.render(user=user, theater_data=theater_data, 
                                        username=user.username, total_admin_revenue=total_admin_revenue)

    return admin_report_html


    
@celery.task()
def send_mail_message():
    users_general = User.query.join(User.roles).filter(Role.name == 'user').all()
    users_admin = User.query.join(User.roles).filter(Role.name == 'admin').all()


    for user in users_general:
        
        report_html = generate_monthly_progress_report(user.id)
        recipient_email = user.email
        recipient_username = user.username if user.username else 'Recipient'
        
        subject = 'Monthly Entertainment Report'
        message = report_html.replace('Recipient', recipient_username)

        
        send_email(to_address=recipient_email, subject=subject, message=message, content='html', attachment_file='monthly_report.html')

    for user in users_admin:
        
        report_html = generate_monthly_theaters_report(user.id)
        recipient_email = user.email
        recipient_username = user.username if user.username else 'Recipient'

        
        subject = 'Monthly Theaters Report'
        message = report_html.replace('Recipient', recipient_username)

        
        send_email(to_address=recipient_email, subject=subject, message=message, content='html', attachment_file='monthly_theaters_report.html')


    return "Monthly report emails sent"

from weasyprint import HTML
import tempfile

@celery.task()
def send_user_html(user_id):
    report_html = generate_complete_entertainment_report(user_id)
    return report_html

@celery.task()
def send_admin_html(user_id):
    report_html = generate_complete_theaters_report(user_id)
    return report_html
    
@celery.task()
def convert_completereport_html_to_pdf(user_id):
    report_html = generate_complete_entertainment_report(user_id)
    pdf_bytes = HTML(string=report_html).write_pdf()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_bytes)
        temp_file_path = temp_file.name

    return temp_file_path

@celery.task()
def convert_admin_html_to_pdf(user_id):
    report_html = generate_complete_theaters_report(user_id)
    pdf_bytes = HTML(string=report_html).write_pdf()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_bytes)
        temp_file_path = temp_file.name

    return temp_file_path

def generate_ticket(booking_id):

    booking = bookings.query.filter_by(booking_id=booking_id).first()
    user = bookings.query.filter_by(user_id=booking.user_id).first()
    show = show_model.query.filter_by(show_id=booking.show_id).first()
    theater = theater_model.query.filter_by(theater_id=show.ts_id).first()

    show_timing_str = show.show_timing.strftime('%Y-%m-%d %H:%M:%S')

    show_time_obj = datetime.strptime(show_timing_str, '%Y-%m-%d %H:%M:%S')

    formatted_show_time = show_time_obj.strftime('%B %d, %Y, %I:%M %p')


    with open('ticket.html', 'r') as template_file:
        template_content = template_file.read()


    template = Template(template_content)

    ticket_html = template.render(theater_name=theater.theater_name,
                                  show_name=show.show_name,
                                  show_time=formatted_show_time,
                                  seat_range=booking.seat_range)


    return ticket_html

@celery.task()
def convert_ticket_html_to_pdf(booking_id):
    ticket_html = generate_ticket(booking_id)
    pdf_bytes = HTML(string=ticket_html).write_pdf()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_bytes)
        temp_file_path = temp_file.name

    return temp_file_path




