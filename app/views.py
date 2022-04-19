"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import datetime

from app import app, db
from flask import render_template, request, jsonify, send_file,flash,url_for,redirect
from flask_login import current_user, login_user,login_required, logout_user
import os
from app.forms import *
from app.models import *
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash



###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/register', methods = ['POST'])
def register():    
    form= RegisterForm()
    if request.method=='POST':
        if form.validate_on_submit():
            username= form.username.data
            password= form.password.data
            fullname= form.fullname.data
            email= form.email.data
            location = form.location.data
            biography= form.biography.data
            photo = form.photo.data
            filename= secure_filename(photo.fiename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

            userRecord = Users( 
                username=username,
                password=password,
                fullname=fullname,
                email=email,
                location = location,
                biography = biography,
                photo = filename,
                date_joined = datetime.now()
            )
            db.session.add(userRecord)
            db.session.commit()

            flash('User successfully registered', 'success')
            return redirect(url_for('login'))

    return jsonify(errors=form_errors(form))        

@app.route('/api/auth/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('cars'))

    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = Users.query.filter_by(username=username).first()

        if user is not None:
            if check_password_hash(user.password,password):
                login_user(user)
                flash('You have been successfully logged in.', 'success')
                return redirect(url_for('cars'))
            else:
                flash("Username or password is incorrect", "danger")
        else:
            return redirect(url_for('register'))


    else:
        error={
            "error": form_errors(form)
        }
        return error
            
            
@app.route('/api/auth/logout', methods=['POST'])
@login_required 
def logout():
    logout_user()
    flash('You were logged out', 'success')

    #PUT CORRECT ROUTE
    return redirect(url_for('home'))


#@app.route('/api/cars', methods=['GET'])
#@login_required
#def cars():
#    cars= Cars.query.all()
#    return cars

@app.route('/api/cars', methods=['POST','GET'])
@login_required
def cars():
    form= AddNewCarForm()
    if request.method=="POST":
        if form.validate_on_submit():
            make= form.make.data
            model= form.model.data
            color= form.color.data
            year= form.year.data
            price= form.price.data
            car_type= form.Car_Type.data
            transmission= form.transmission.data
            description=form.description.data
            photo= form.photo.data
            filename= secure_filename(photo.filename)

            photo.save(os.path.join(app.config["UPLOAD_FOLDER", filename]))

            car= Cars(
                description=description,
                make=make,
                model= model,
                color=color,
                year=year,
                transmission=transmission,
                car_type=car_type,
                price= price,
                photo= filename,
                user_id= flask_login.current_user.id
                #ADD USER ID
            )

            db.session.add(car)
            db.session.commit()
            
            #should we send over user id?
            data={
                "message": "Car successfully added",
                "description": description,
                "make":make,
                "model": model,
                "color": color,
                "year":year,
                "transmission":transmission,
                "car_type":car_type,
                "price":price,
                "filename": filename
            }
            #PUT CORRECT ROUTE
            return jsonify(data=data)

        else:
            error={
                "error": form_errors(form)
            }
            return error

    elif request.method=="GET":
        cars= Cars.query.all()
        return cars


@app.route('/api/cars/<car_id>', methods=['GET'])
@login_required
def carsSpecific(car_id):
    car = Cars.query.filter_by(id=car_id).first()

    data={
    "id": car.id, 
    "description":car.description, 
    "make":car.make, 
    "model":car.model,
    "colour": car.colour, 
    "year": car.year, 
    "transmission":car.transmission, 
    "car_type": car.car_type, 
    "price":car.price, 
    "photo":car.photo, 
    "user_id":car.user_id}

    return jsonify(data=data)

@app.route('/api/cars/<car_id>/favourite', methods=['POST'])
@login_required
def carsFavorite(car_id):
    fav_car= Cars.query.filter(id=car_id).first()
    #ADD CAR TO FAVORITY FOR LOGGED IN USER
    return


@app.route('/api/search', methods=['GET'])
@login_required
def search():
    form= ExploreForm()
    if request.method=="GET":
        if form.validate_on_submit():
            make_model= form.make_or_model.data

            cars= Cars.query.filter(make=make_model, model=make_model).all()
            return cars
        else:
            error={
                "error": form_errors(form)
            }
            return error


    

@app.route('/api/users/<user_id>', methods=['GET'])
@login_required
def user(user_id):
    user= Users.query.filter(id=user_id).first()
    return user

@app.route('/api/users/<user_id>/favorites', methods=['GET'])
@login_required
def userFavorite():
    return











###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return jsonify(error="Page Not Found"), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")