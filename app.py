"""app.py"""
import os
from flask import Flask, jsonify, request
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from scraper.car_scrapper import scrape_cars

#Loading python enviroment
from dotenv import load_dotenv
load_dotenv()

#Configuring Flask Application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_DB")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Initializing Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class Car(db.Model):
    """Model class, will represent the car table in Database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    price = db.Column(db.String(255))
    details = db.Column(db.String(255))

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'details': self.details
        }
    
class CarView(MethodView):
    """This a class-based viewset having all the methods to fetch and manage cars data.
    """
    def get(self, car_id=None):
        """Get method for retrieving all cars or single specific car."""
        if car_id is None:
            # Retrieve all cars
            cars = Car.query.all()
            return jsonify([car.serialize() for car in cars])
        else:
            # Retrieve a specific car
            car = Car.query.get_or_404(car_id)
            return jsonify(car.serialize())

    def post(self):
        """POST Method for creating a single record of car in Database."""
        data = request.get_json()

        # Create a new car
        new_car = Car(
            title=data.get('title'),
            price=data.get('price'),
            details=data.get('details')
        )

        # Add the new car to the database
        db.session.add(new_car)
        db.session.commit()

        return jsonify(new_car.serialize()), 201

    def put(self, car_id):
        """Method for updating a car using id."""
        car = Car.query.get_or_404(car_id)
        data = request.get_json()

        # Update car attributes
        car.title = data.get('title', car.title)
        car.price = data.get('price', car.price)
        car.details = data.get('details', car.details)

        # Commit changes to the database
        db.session.commit()

        return jsonify(car.serialize())

    def delete(self, car_id):
        """Delete a car record from Database."""
        car = Car.query.get_or_404(car_id)

        # Delete the car from the database
        db.session.delete(car)
        db.session.commit()

        return jsonify({'message': 'Car deleted successfully'})

@app.route('/scrape', methods=['POST'])
def scrape_data():
    """This is endpoint for scraping data and saving it in Database."""
    try:
        cars_data = scrape_cars()
        for data in cars_data:
            existing_car = Car.query.filter_by(title=data['title'], price=data['price'], details=data['details'] ).first()
            if not existing_car:
                new_car = Car(title=data['title'], price=data['price'], details=data['details'])
                db.session.add(new_car)
            db.session.commit()

        return jsonify({'status': 'success', 'message': 'Successfully scraped and loaded data into database.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Registering class-based views with the Flask app
car_view = CarView.as_view('car_api')
app.add_url_rule('/cars', view_func=car_view, methods=['GET', 'POST'])
app.add_url_rule('/cars/<int:car_id>', view_func=CarView.as_view('car'), methods=['GET', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run(debug=True)
