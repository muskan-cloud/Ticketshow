from flask import Flask, render_template, send_file,request,jsonify,abort
from flask_security import auth_required
from flask_cors import CORS
from api import api,cache
from flask_security.utils import hash_password
from models import db, User as user_model,show as show_model,Role, ShowRating, theater , ShowTheater, PopularityPrediction,bookings as book_model
from datetime import datetime
import pandas as pd
from sklearn.preprocessing import StandardScaler,MinMaxScaler,MaxAbsScaler
from sklearn.linear_model import LinearRegression
import pytz
from security import user_datastore, sec
import worker
from tasks import export_theater_shows_csv,send_reminder,send_mail_message,send_admin_html,send_user_html,convert_admin_html_to_pdf,convert_ticket_html_to_pdf,convert_completereport_html_to_pdf,export_user_csv
from celery import Celery
from celery.schedules import crontab
from flask import Response

IST = pytz.timezone('Asia/Kolkata')


app = Flask(__name__)
CORS(app) 
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketshow_v2.db'
app.config['SECRET_KEY'] = "thisissecret"
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = "Authentication-Token"
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_ROLE_REQUIRED'] = True
app.config['CELERY_BROKER_URL']="redis://localhost:6379/1"
app.config['CELERY_RESULT_BACKEND']="redis://localhost:6379/2"
app.config['CELERY_TIMEZONE'] = 'Asia/Kolkata'

cache.init_app(app)

api.init_app(app)
db.init_app(app)

sec.init_app(app, user_datastore)
app.app_context().push()
celery = worker.celery
celery.conf.update(
    broker_url= app.config['CELERY_BROKER_URL'],
result_backend = app.config['CELERY_RESULT_BACKEND'],
timezone=app.config['CELERY_TIMEZONE']
)

celery.Task = worker.ContextTask
app.app_context().push()

@app.route('/export_shows_csv/<int:theater_id>', methods=['POST']) #admin
@auth_required()
def export_theater_show_csv(theater_id):
    task = export_theater_shows_csv.delay(theater_id=theater_id)
    task_result = task.get()
    csv_file_path = task_result['csv_file_path']
    return send_file(csv_file_path, as_attachment=True)

@app.route('/export_user_csv/<int:user_id>', methods=['POST']) #user_csv
@auth_required()
def export_report_user_csv(user_id):
    task = export_user_csv.delay(user_id=user_id)
    task_result = task.get()
    csv_file_path = task_result['csv_file_path']
    return send_file(csv_file_path, as_attachment=True)

@app.route('/export_report_user_html/<int:user_id>', methods=['POST']) #general_user_comp
@auth_required()
def export_uhreport(user_id):
    task = send_user_html.delay(user_id=user_id)
    task_result = task.get()
    response = Response(task_result, content_type='text/html')
    response.headers["Content-Disposition"] = f"attachment; filename=user_report.html"
    
    return response



@app.route('/export_report_admin_html/<int:user_id>', methods=['POST']) #admin_comp
@auth_required()
def export_ahreport(user_id):
    task = send_admin_html.delay(user_id=user_id)
    task_result = task.get()
    
    response = Response(task_result, content_type='text/html')
    response.headers["Content-Disposition"] = f"attachment; filename=admin_report.html"
    
    return response


@app.route('/export_report/<int:user_id>', methods=['POST']) #general_user_comp
@auth_required()
def export_report(user_id):
    task = convert_completereport_html_to_pdf.delay(user_id=user_id)
    task_result = task.get()
    return send_file(task_result, as_attachment=True,download_name='report.pdf', mimetype='application/pdf')

@app.route('/export_admin_report/<int:user_id>',methods=['POST']) #admin_comp
@auth_required()
def export_admin_report(user_id):
    task = convert_admin_html_to_pdf.delay(user_id=user_id)
    task_result = task.get()
    return send_file(task_result, as_attachment=True,download_name='report_admin.pdf', mimetype='application/pdf')

@app.route('/download_ticket/<int:booking_id>',methods=['POST']) 
@auth_required()
def download_ticket(booking_id):
    task = convert_ticket_html_to_pdf.delay(booking_id=booking_id)
    task_result = task.get()
    return send_file(task_result, as_attachment=True,download_name='ticket.pdf', mimetype='application/pdf')

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=21, minute=30, day_of_month='12'),
        send_mail_message.s(),
        name='ticketshow'
    )

    sender.add_periodic_task(
        crontab(hour=19, minute=0),
        send_reminder.s(),
        name='ticketbooking not done!'
    )

#popularity prediction
@app.route('/predict_bookings/<int:show_id>', methods=['POST'])
@auth_required()
def predict_bookings(show_id):
    required_show=show_model.query.filter_by(show_id=show_id).first()
    rst = theater.query.filter_by(theater_id=required_show.ts_id).first()
    shows = show_model.query.all()
    data = []
    target = []
    
    for show in shows:
        if show.show_id == show_id :
            continue
        show_theater = theater.query.filter_by(theater_id=show.ts_id).first()
        show_booking_theater = ShowTheater.query.filter_by(show_id=show.show_id).first()
        
        show_data = {
            'show_id': show.show_id,
            'show_price': show.show_price,
            'capacity': show_theater.theater_capacity if show_theater else 0,
            'show_duration' : show.show_duration
        }
        
        bookings_count = show_booking_theater.total_bookings if show_booking_theater else 0
        data.append(show_data)
        target.append(bookings_count)
    
    df = pd.DataFrame(data)
    df['bookings_count'] = target
    
    df = df.dropna()
    
    if df.shape[0] < 1:
        return jsonify({'error': 'Insufficient data for prediction.'}), 400
    
    X = df.drop('bookings_count', axis=1)
    y = df['bookings_count']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    new_show_data = {
        'show_id': show_id,
        'show_price': required_show.show_price,
        'capacity': rst.theater_capacity,
        'show_duration' : required_show.show_duration
    }
    new_show_df = pd.DataFrame([new_show_data])
    new_show_scaled = scaler.transform(new_show_df)

    prediction = max(int(model.predict(new_show_scaled)[0]), 0)

    new_booking_prediction = PopularityPrediction(
        show_id=new_show_data['show_id'],
        predicted_booking_count=prediction,
        timestamp=datetime.now(IST)
    )
    db.session.add(new_booking_prediction)
    db.session.commit()
    
    return jsonify({'prediction': prediction}), 200

#graph for revenue generated by each show of each theater
import matplotlib.pyplot as plt
import os
import matplotlib.pyplot as plt
import os

def plot_graph(show_names, revenues, bookings, theater_name):
    plt.figure(figsize=(10, 8), facecolor='bisque')
    plt.bar(show_names, revenues, color='darkblue')

    
    offset = max(revenues) * 0.05

    for i, (revenue, booking) in enumerate(zip(revenues, bookings)):
        plt.text(i, revenue, f'\u20B9 {revenue}, Bookings: {booking}', ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.xlabel('Show Names', fontsize=14, fontweight='bold')
    plt.ylabel('Total Revenue', fontsize=14, fontweight='bold')
    plt.title(f'Total Revenue and Bookings for Shows in {theater_name}', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10, fontweight='bold')

    plt.tight_layout()

    if not os.path.exists("graphs"):
        os.makedirs("graphs")

    image_file = os.path.join("graphs", f'revenue_graph_{theater_name}.png')
    plt.savefig(image_file)
    plt.close()

    return image_file

@app.route("/revenue/<int:user_id>", methods=["GET"])
@auth_required()
def revenue_graphs(user_id):
    if not user_id :
        return abort(403, "You are not authorized to access this resource.")
    user = user_model.query.filter_by(id=user_id).first()
    theaters = theater.query.filter_by(ut_id=user_id).all()

    all_theater_data = []

    for t in theaters:
        show_names = []
        revenues = []
        bookings = []

        show_theaters = ShowTheater.query.filter_by(theater_id=t.theater_id).all()

        for show_theater in show_theaters:
            show = db.session.get(show_model, show_theater.show_id)

            total_revenue = 0
            total_bookings = 0 

            for booking in show.bookings:
                total_revenue += booking.booking_tickets_count * show.show_price
                total_bookings += booking.booking_tickets_count

            show_names.append(show.show_name)
            revenues.append(total_revenue)
            bookings.append(total_bookings)

        graph_image_file = plot_graph(show_names, revenues, bookings, t.theater_name)

        theater_data = {
            "theaterName": t.theater_name,
            "showNames": show_names,
            "revenues": revenues,
            "bookings": bookings,
            "graphImageUrl": f"http://localhost:5000/get-graph-image/{t.theater_name}",
        }

        all_theater_data.append(theater_data)

    return jsonify(all_theater_data)

        

@app.route("/get-graph-image/<theater_name>", methods=["GET"])
def get_graph_image(theater_name):
    image_path = os.path.join("graphs", f"revenue_graph_{theater_name}.png")

    if os.path.exists(image_path):
        return send_file(image_path, mimetype="image/png")
    else:
        return jsonify({"error": "Graph image not found"}), 404





if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()

        if not admin_role:
            
            admin_role = Role(name='admin', description='Administrator Role')
            db.session.add(admin_role)

        if not user_role:
           
            user_role = Role(name='user', description='User Role')
            db.session.add(user_role)

        
        db.session.commit()
        users=user_model.query.all()
        if not users:
            admin_user = user_model.query.filter_by(email='admin@gmail.com').first()

            if not admin_user:
                
                admin_user = user_model(email='admin@gmail.com', username='admin', password=hash_password('admin_password'))
                admin_user.active = True  
                admin_user.fs_uniquifier = 'unique_value'
                admin_user.roles.append(admin_role)

               
                db.session.add(admin_user)
                db.session.commit()

    app.run(debug=True)
