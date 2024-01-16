from flask_restful import Api, Resource, fields, marshal,marshal_with
from flask_security import auth_required, current_user,login_required,roles_required
from flask_security.utils import hash_password
from security import user_datastore
from models import db, User as user_model,Role,theater as theater_model,show as show_model,bookings as book_model,ShowTheater,ShowRating,ShowTags as tag_model
from datetime import datetime
from sqlalchemy import func
from time import perf_counter_ns
from flask import abort, request,jsonify,redirect,url_for
from flask_caching import Cache
import redis
import base64,os

redis_url = "redis://localhost:6379/3"
redis_client = redis.from_url(redis_url)
cache = Cache(config={"CACHE_TYPE": "redis", "CACHE_REDIS_CLIENT": redis_client})

api = Api(prefix="/api")

user_resource_fields = {
    "id": fields.Integer(),
    "username": fields.String,
    "password": fields.String,
    "email": fields.String,
    "roles": fields.List(fields.String),
}

theater_resource_fields = {
    "ut_id":fields.Integer(),
    "theater_id": fields.Integer(),
    "theater_name": fields.String,
    "theater_address" : fields.String,
    "theater_capacity" : fields.Integer(),
    "theater_pic": fields.Raw,
    "user": fields.Nested(user_resource_fields),
}

show_resource_fields = {
    "ts_id":fields.Integer(),
    "show_id": fields.Integer(),
    "show_rating": fields.Float(),
    "show_name":fields.String,
    "show_price":fields.String,
    "show_description":fields.String,
    "show_trailer":fields.String,
    "show_pic" : fields.Raw,
    "show_timing":fields.String,
    "show_duration":fields.Integer(),
    "theater":fields.Nested(theater_resource_fields),
    "user": fields.Nested(user_resource_fields),
}

book_resource_fields = {
    "booking_id": fields.Integer(),
    "booking_tickets_count": fields.Integer(),
    "booking_time":fields.String,
    "seat_range":fields.String,
    "user_id":fields.Integer(),
    "show_id":fields.Integer(),
    "user_rating":fields.Integer(),
    "user": fields.Nested(user_resource_fields),
    "show": fields.Nested(show_resource_fields),
    

}


def allocate_seats(show_id, booking_tickets_count):
    existing_bookings = book_model.query.filter_by(show_id=show_id).all()
    total_booked_seats = sum([booking.booking_tickets_count for booking in existing_bookings])
    starting_seat_number = total_booked_seats + 1
    ending_seat_number = starting_seat_number + int(booking_tickets_count) - 1
    seat_range = f"{starting_seat_number}-{ending_seat_number}"
    return seat_range


class User(Resource):
    @auth_required()
    def get(self, email):
        user = user_model.query.filter_by(email=email).first()
        if not user:
            abort(404, "User not found")
        
        else:
            theaters = theater_model.query.filter_by(ut_id=user.id).all()
            user_data = marshal(user, user_resource_fields)
            user_data['theaters'] = []
            
            for theater in theaters:
                theater_data = marshal(theater, theater_resource_fields)
                theater_data['theater_pic'] = base64.b64encode(theater.theater_pic).decode('utf-8')
                shows = show_model.query.filter_by(ts_id=theater.theater_id).all()

                theater_data['shows'] = []
                for show in shows:
                    show_data = marshal(show, show_resource_fields)
                    show_data['show_pic'] = base64.b64encode(show.show_pic).decode('utf-8')
                    theater_data['shows'].append(show_data)
                    
                user_data['theaters'].append(theater_data)
                
            return user_data

            
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        username = request.json.get('username')
        general_signup = request.json.get('general_signup')

        if email and password and username:
            user = user_model.query.filter_by(email=email).first()
            if user:
                abort(400, "User with email already exists")
            else:
                user = user_model(email=email)
                user.password = password
                user = user_datastore.create_user(username=username, email=email, password=hash_password(password))

                if '/admin_signup' in request.path:
                    if general_signup:
                        admin_role = user_datastore.find_role('admin')
                        user_datastore.add_role_to_user(user, admin_role)
                        user_role = user_datastore.find_role('user')
                        user_datastore.add_role_to_user(user, user_role)

                    else:
                        admin_role = user_datastore.find_role('admin')
                        user_datastore.add_role_to_user(user, admin_role)
                else:
                    user_role = user_datastore.find_role('user')
                    user_datastore.add_role_to_user(user, user_role)

                db.session.commit()


                return {"message": "signed up successfully!"},200
        else:
            abort(400, "Email, password, and username are required")

    @auth_required()
    def put(self,email):
        if email:
            user = user_model.query.filter_by(email=email).first()
            if user:
                updated_email = request.form.get('email')
                password = request.form.get('password')
                updated_username = request.form.get('username')
                if updated_email and updated_username:
                    user_1 = user_model.query.filter_by(email=updated_email).first()
                    user_2 = user_model.query.filter_by(username=updated_username).first()
                    if user_1 :
                        if user_1 != user :
                            return{ "message" : "User with email already exists"}, 400
                    if user_2:
                        if user_2 != user :
                            return{ "message" : "User with username already exists"}, 400
                    user.email= updated_email
                    user.username = updated_username
                    if password:
                        user.password = hash_password(password)
                    
                    db.session.commit()

                return {"message": "Account updated successfully"},200
            else:
                return {"message": "User Not Found"},400
            
    @auth_required()        
    def delete(self,email):        
        user=user_model.query.filter_by(email=email).first()
        theaters = theater_model.query.filter_by(ut_id=user.id).all()
        for theater in theaters:
            db.session.delete(theater)
        db.session.delete(user)
        db.session.commit()
            

        return {"message": "deleted successfully"}
           

class Admin_Dashboard(Resource):
    @cache.cached(timeout=10,key_prefix='admin_dashboard')
    def get(self, email):
        if not current_user.has_role('admin'):
            print(current_user.roles)
            abort(403, "You are not authorized to access this resource.")
        else:
            if email != current_user.email:
                abort(403, "You are not authorized to access this resource.")

            user = user_model.query.filter_by(email=email).first()
            if not user:
                abort(404, "User not found.")
            start=perf_counter_ns()
            theaters = theater_model.query.filter(theater_model.ut_id == user.id).all()
            theater_dicts = []
            for theater in theaters:
                theater_dict = marshal(theater, theater_resource_fields)
                theater_dict['theater_pic'] = base64.b64encode(theater.theater_pic).decode('utf-8')
                theater_dicts.append(theater_dict)
            stop = perf_counter_ns()
            print(stop-start)    
            return theater_dicts
        
class User_Dashboard(Resource):
    @cache.cached(timeout=60)
    def get(self, email):
        if not current_user.has_role('user'):
            print(current_user.roles)
            abort(403, "You are not authorized to access this resource.")
        else:
            if email != current_user.email:
                abort(400, "You are not authorized to access this resource.")

            user = user_model.query.filter_by(email=email).first()
            if not user:
                abort(404, "User not found.")
            start=perf_counter_ns()
            shows=show_model.query.all()
            show_dicts = []
            for show in shows:
                theater=theater_model.query.filter_by(theater_id=show.ts_id).first()
                show_dict = marshal(show, show_resource_fields)
                show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
                show_dict['theater'] = marshal(theater, theater_resource_fields)
                show_dict['theater']['theater_pic'] = base64.b64encode(theater.theater_pic).decode() if show.show_pic else None
                show_dicts.append(show_dict)
            stop = perf_counter_ns()
            print(stop-start)
            return show_dicts

            
class Theater(Resource):
    @auth_required()
    def get(self,theater_id):
        theater = theater_model.query.filter_by(theater_id=theater_id).first()
        user=user_model.query.filter_by(id=theater.ut_id).first()
        
        if user and theater:
            shows = show_model.query.filter_by(ts_id=theater.theater_id).all()
            show_dicts = []
            for show in shows:
                show_dict = marshal(show, show_resource_fields)
                show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
                show_dict['theater'] = marshal(theater, theater_resource_fields)
                show_dict['theater']['theater_pic'] = base64.b64encode(theater.theater_pic).decode() if show.show_pic else None
                
                show_dicts.append(show_dict)
            return show_dicts
        else:
                abort(404, "theater not found")
    @auth_required() 
    def post(self,user_id):
        
        if user_id:
            theater_name = request.form.get("theater_name")
            theater_pic = request.files.get('theater_pic')
            theater_address = request.form.get("theater_address")
            theater_capacity = request.form.get("theater_capacity")
            if theater_name and theater_pic and theater_address and theater_capacity :
            
                new_theater = theater_model(ut_id=user_id, theater_name=theater_name, theater_pic=theater_pic.read(),theater_address=theater_address,theater_capacity=theater_capacity)
                db.session.add(new_theater)
                db.session.commit()
                cache.delete('admin_dashboard')
            else:
                abort(400,"please fill details") ; 
        else:
            abort(403, "You are not authorized to access this resource.")
    @auth_required() 
    def delete(self,email,theater_id):
        
            user=user_model.query.filter_by(email=email).first()
            theater = theater_model.query.filter_by(ut_id=user.id,theater_id=theater_id).first()
            shows = show_model.query.filter_by(ts_id=theater.theater_id).all()
            if not theater:
                abort(400, "no theater")
            for show in shows:
                db.session.delete(show)
            db.session.delete(theater)
            db.session.commit()
            cache.delete('admin_dashboard')


            return {"message": "deleted successfully"}
        
  
    @auth_required() 
    def put(self,theater_id):
        theater = theater_model.query.filter_by(theater_id=theater_id).first()
        if not theater:
            abort(404, "theater not found")


        theater_name = request.form.get("theater_name")
        theater_pic = request.files.get('theater_pic')
        theater_address= request.form.get("theater_address")
        theater_capacity = request.form.get("theater_capacity")
        if theater_name and theater_address and theater_capacity:
            theater.theater_name = theater_name
            theater.theater_address =theater_address
            theater.theater_capacity = theater_capacity

        if theater_pic:
            theater.theater_pic = theater_pic.read()

        db.session.commit()
        cache.delete('admin_dashboard')

        return {"message": "theater updated successfully"}
        
        
class Theater_Details(Resource):
    @auth_required()
    def get(self, theater_id):
        theater = theater_model.query.filter_by(theater_id=theater_id).first()
        user = user_model.query.filter_by(id=theater.ut_id).first()

        if user and theater:
            shows = show_model.query.filter_by(ts_id=theater.theater_id).all()
            show_dicts = []
            for show in shows:
                show_dict = marshal(show, show_resource_fields)
                show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
                show_dicts.append(show_dict)

            theater_dict = marshal(theater, theater_resource_fields)
            theater_dict['theater_pic'] = base64.b64encode(theater.theater_pic).decode() if theater.theater_pic else None

            theater_dict['shows'] = show_dicts

            return theater_dict


        
class Shows(Resource):  
    @auth_required()
    def post(self,theater_id,user_id):
        theater=theater_model.query.filter_by(theater_id=theater_id,ut_id=user_id).first()

        show_name = request.form.get("show_name")
        show_pic = request.files.get('show_pic')
        show_duration = request.form.get("show_duration")
        show_timing = request.form.get("show_timing")
        show_timing = datetime.strptime(show_timing, '%Y-%m-%dT%H:%M') 
        show_description = request.form.get("show_description")
        show_trailer = request.form.get("show_trailer")
        show_price= request.form.get("show_price")

        if show_name and show_pic and show_timing and show_price and show_description and show_duration:
            if show_trailer:
                new_show = show_model(ts_id=theater.theater_id, show_name=show_name, show_pic=show_pic.read(),show_timing=show_timing,show_duration=show_duration,show_description=show_description,show_trailer=show_trailer,show_price=show_price)
                db.session.add(new_show)
                db.session.commit()
            else:
                new_show = show_model(ts_id=theater.theater_id, show_name=show_name, show_pic=show_pic.read(),show_timing=show_timing,show_duration=show_duration,show_description=show_description,show_price=show_price)
                db.session.add(new_show)
                db.session.commit()

            show=show_model.query.filter_by(show_id=new_show.show_id).first()
            theater=theater_model.query.filter_by(theater_id=show.ts_id).first()
            show_theater_entry = ShowTheater.query.filter_by(show_id=new_show.show_id, theater_id=show.ts_id).first()
            show_theater_entry = ShowTheater(show_id=new_show.show_id, theater_id=show.ts_id, available_tickets=theater.theater_capacity)
            db.session.add(show_theater_entry)

            db.session.commit()

        else:
            abort(400) 

    @auth_required()
    def get(self,show_id):
        show=show_model.query.filter_by(show_id=show_id).first()
        theater=theater_model.query.filter_by(theater_id=show.ts_id).first()
        user=user_model.query.filter_by(id=theater.ut_id).first()
        if user and theater and show:
            show_dict = marshal(show, show_resource_fields)
            
            show_dict['theater'] = marshal(theater, theater_resource_fields)
            show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
            show_dict['theater']['theater_pic'] = base64.b64encode(theater.theater_pic).decode() if show.show_pic else None
            return show_dict
        else:
            return {"message": "show not found"},400
        
        
        
    @auth_required()
    def put(self, show_id):
        show = show_model.query.filter_by(show_id=show_id).first()
        theater = theater_model.query.filter_by(theater_id=show.ts_id).first()
        user = user_model.query.filter_by(id=theater.ut_id).first()
        
        if show and theater and user:
            show_name = request.form.get("show_name")
            show_pic = request.files.get('show_pic')
            show_duration = request.form.get("show_duration")
            show_timing = request.form.get("show_timing")
            show_description = request.form.get("show_description")
            show_trailer = request.form.get("show_trailer")
            show_price = request.form.get("show_price")

            if show_name and show_timing and show_description and show_price and show_duration:
                try:
                    
                    show_timing = datetime.strptime(show_timing, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        
                        show_timing = datetime.strptime(show_timing, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        return {"message": "Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DDTHH:MM'."}

                show.show_name = show_name
                show.show_timing = show_timing
                show.show_description = show_description
                show.show_price = show_price
                show.show_duration = show_duration

                if show_pic:
                    show.show_pic = show_pic.read()

                if show_trailer:
                    show.show_trailer = show_trailer

                db.session.commit()

                return {"message": "show updated successfully"}
            else:
                return {"message": "data not given"}
        else:
            return {"message": "show not found"}
            

    
    @auth_required()        
    def delete(self,show_id):
        show=show_model.query.filter_by(show_id=show_id).first()
        theater=theater_model.query.filter_by(theater_id=show.ts_id).first()
        user=user_model.query.filter_by(id=theater.ut_id).first()
        if user and theater and show:
            db.session.delete(show)
            db.session.commit()
            return {"message": "deleted successfully"}
        else:
            return {"message": "not found"}


class Booking(Resource): 
    @auth_required()   
    def post(self, user_id, show_id):
        booking_tickets_count = request.form.get("booking_tickets_count")
        if booking_tickets_count:
        
            seat_range = allocate_seats(show_id, booking_tickets_count)

        
            new_booking = book_model(
            show_id=show_id,
            user_id=user_id,
            booking_tickets_count=booking_tickets_count,
            seat_range=seat_range
        )
            db.session.add(new_booking)
            db.session.commit()

            show = show_model.query.filter_by(show_id=show_id).first()
            theater = theater_model.query.filter_by(theater_id=show.ts_id).first()
            show_theater_entry = ShowTheater.query.filter_by(show_id=show_id, theater_id=show.ts_id).first()
            if show_theater_entry:
                show_theater_entry.available_tickets -= new_booking.booking_tickets_count
                show_theater_entry.total_bookings += new_booking.booking_tickets_count
            else:
                show_theater_entry = ShowTheater(
                show_id=show_id,
                theater_id=show.ts_id,
                available_tickets=theater.theater_capacity,
                total_bookings=0
            )
            db.session.add(show_theater_entry)
            db.session.commit()
        else:
            abort(400)

    @auth_required()
    def get(self,user_id):
            bookings=book_model.query.filter_by(user_id=user_id).all()
            booked_data=[]
            for booking in bookings:
            
                show=show_model.query.filter_by(show_id=booking.show_id).first()
                show_dict = marshal(show, show_resource_fields)
                show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
                booking_data = marshal(booking, book_resource_fields)
                booking_data['show'] = show_dict
                booked_data.append(booking_data)
            
            return booked_data
        
    @auth_required()
    def delete(self, user_id, show_id, booking_id):
        booking = book_model.query.filter_by(show_id=show_id, user_id=user_id,booking_id=booking_id).first()
        if booking:
            db.session.delete(booking)
            show=show_model.query.filter_by(show_id=show_id).first()
            show_theater_entry = ShowTheater.query.filter_by(show_id=show_id, theater_id=show.ts_id).first()
            if show_theater_entry:
                show_theater_entry.available_tickets += booking.booking_tickets_count
                show_theater_entry.total_bookings -= booking.booking_tickets_count

            db.session.commit()
        else:
            abort(404)


class Rating(Resource):  
    @auth_required()
    def get (self, user_id, show_id):
        show_rating = ShowRating.query.filter_by(show_id=show_id, user_id=user_id).first()
        if show_rating:
            return show_rating.user_rating
        

    @auth_required()
    def post(self, user_id, show_id):
        if not user_id or not show_id:
            return {"message": "you are not authorized"}
        user_rating = request.form.get("userRating")

        show_rating = ShowRating.query.filter_by(show_id=show_id, user_id=user_id).first()
        if show_rating:
            show_rating.user_rating = user_rating
        else:
            show_rating = ShowRating(show_id=show_id, user_id=user_id, user_rating=user_rating)
            db.session.add(show_rating)

        avg_rating = ShowRating.query.with_entities(func.avg(ShowRating.user_rating)).filter_by(show_id=show_id).scalar()

        show = show_model.query.filter_by(show_id=show_id).first()
        show.show_rating = avg_rating
        db.session.commit()

        return jsonify({'message': 'Rating submitted successfully.'})
        
    @auth_required()
    def delete(self, user_id, show_id):
        show_rating = ShowRating.query.filter_by(show_id=show_id, user_id=user_id).first()
        if show_rating:
            db.session.delete(show_rating)
            db.session.commit()

            avg_rating = ShowRating.query.with_entities(func.avg(ShowRating.user_rating)).filter_by(show_id=show_id).scalar()
            show = show_model.query.filter_by(show_id=show_id).first()
            show.show_rating = avg_rating
            db.session.commit()

            return {"message": "User rating deleted successfully."}
        else:
            return {"message": "User rating not found."}, 404

class Tagsall(Resource):
    @auth_required()
    def get (self,show_id):
        show_tags= tag_model.query.filter_by(show_id=show_id).all()
        
        showtags = [{"id": tag.id, "user_tag": tag.user_tag} for tag in show_tags]
        return showtags

        
class Tags(Resource):
    @auth_required()
    def get(self, user_id, show_id):
        show_tags = tag_model.query.filter_by(show_id=show_id, user_id=user_id).all()
        showtags = [{"id": tag.id, "user_tag": tag.user_tag} for tag in show_tags]

        return showtags

    @auth_required()
    def post(self, user_id, show_id):
        user_tag = request.form.get("user_tag")

        show_tag = tag_model(show_id=show_id, user_id=user_id, user_tag=user_tag)
        db.session.add(show_tag)
        db.session.commit()

        return jsonify({'message': 'Tags submitted successfully.'})
    @auth_required()
    def delete(self, user_id, show_id,tag_id):
        show_tag = tag_model.query.filter_by( user_id=user_id, show_id= show_id,id=tag_id).first()
        if show_tag:
            db.session.delete(show_tag)
            db.session.commit()

            return {"message": "Tag deleted successfully."}
        else:
            return {"message": "Tag not found."}, 404

            
class AvailableTickets(Resource):
    @auth_required()
    def get(self,show_id):
        show_theater=ShowTheater.query.filter_by(show_id=show_id).first()
        available_tickets = show_theater.available_tickets 
        return available_tickets

class Search(Resource):
    @auth_required()
    def get(self):
        search_query = request.args.get('q')
        if not search_query:
            abort(400, 'Search query parameter "q" is required')

        theaters = theater_model.query.filter(
            (theater_model.theater_name.ilike(f'%{search_query}%')) |
            (theater_model.theater_address.ilike(f'%{search_query}%'))
        ).all()

        shows = show_model.query.join(theater_model).filter(
            (show_model.show_name.ilike(f'%{search_query}%')) |
            (theater_model.theater_address.ilike(f'%{search_query}%')) |
            (show_model.show_description.ilike(f'%{search_query}%')) |
            (show_model.show_rating.ilike(f'%{search_query}%')) |
            (show_model.show_timing.ilike(f'%{search_query}%')) |
            (show_model.show_id.in_(db.session.query(tag_model.show_id)
                                    .filter(tag_model.user_tag.ilike(f'%{search_query}%')))
            )
        ).all()

        theater_dicts = []
        for theater in theaters:
            theater_dict = marshal(theater, theater_resource_fields)
            theater_dict['theater_pic'] = base64.b64encode(theater.theater_pic).decode() if theater.theater_pic else None
            theater_dicts.append(theater_dict)

        show_dicts = []
        for show in shows:
            show_dict = marshal(show, show_resource_fields)
            show_dict['show_pic'] = base64.b64encode(show.show_pic).decode() if show.show_pic else None
            show_dicts.append(show_dict)

        result_dicts = theater_dicts + show_dicts

        return result_dicts
    
class Total_booking(Resource):
    @auth_required()
    def get(self,show_id):
        show_th=ShowTheater.query.filter_by(show_id=show_id).first()
        return show_th.total_bookings

api.add_resource(User, '/admin_signup', '/general_signup','/users/<string:email>')
api.add_resource(Admin_Dashboard,'/admin_dashboard/<string:email>')
api.add_resource(User_Dashboard,'/user_dashboard/<string:email>')
api.add_resource(Theater,'/<int:user_id>/add_theater','/users/<string:email>/theaters/<int:theater_id>','/theaters/<int:theater_id>')
api.add_resource(Shows,'/<int:user_id>/<int:theater_id>/theater/add_show','/show/<int:show_id>')
api.add_resource(Booking,'/book_show/<int:user_id>/<int:show_id>','/bookings/<int:user_id>','/cancel_booking/<int:user_id>/<int:show_id>/<int:booking_id>')
api.add_resource(Theater_Details,'/theater_details/<int:theater_id>')
api.add_resource(AvailableTickets,'/avl_tickets/<int:show_id>')
api.add_resource(Search,'/search')
api.add_resource(Rating,'/rate_show/<int:user_id>/<int:show_id>')
api.add_resource(Tags,'/tag_show/<int:user_id>/<int:show_id>','/tag_show/<int:user_id>/<int:show_id>/<int:tag_id>')
api.add_resource(Tagsall,'/tag_show/<int:show_id>')
api.add_resource(Total_booking,'/booked_tickets_count/<int:show_id>')
