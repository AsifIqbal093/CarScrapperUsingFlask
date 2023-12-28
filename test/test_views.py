import os
import unittest
from app import app, db
from app import Car
from unittest.mock import patch, MagicMock
from flask import Flask

from dotenv import load_dotenv
load_dotenv()

class TestCarView(unittest.TestCase):
    def setUp(self):
        """Set up the test database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_DB")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_car(self):
        """Test creating a new car."""
        data = {'title': 'New Car', 'price': '10000', 'details': 'New Details'}
        response = self.app.post('/cars', json=data)
        created_car = Car.query.first()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(created_car.title, 'New Car')

    def test_get_all_cars(self):
        """Test retrieving all cars."""
        car = Car(title='Test Car', price='Test Price', details='Test Details')
        with app.app_context():
            db.session.add(car)
            db.session.commit()
            response = self.app.get('/cars')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_single_car(self):
        """Test retrieving a single car."""
        car = Car(title='Test Car', price='Test Price', details='Test Details')
        with app.app_context():
            db.session.add(car)
            db.session.commit()
            response = self.app.get(f'/cars/{car.id}')
            data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], 'Test Car')

    

    def test_update_car(self):
        """Test updating a car."""
        car = Car(title='Test Car', price='Test Price', details='Test Details')
        with app.app_context():
            db.session.add(car)
            db.session.commit()

            update_data = {'title': 'Updated Car', 'price':'Test Price', 'details':'Test Details'}
            response = self.app.put(f'/cars/{car.id}', json=update_data)

        self.assertEqual(response.status_code, 200)


    def test_delete_car(self):
        """Test deleting a car."""
        car = Car(title='Test Car', price='Test Price', details='Test Details')
        with app.app_context():
            db.session.add(car)
            db.session.commit()

            car = Car.query.get(car.id)

            response = self.app.delete(f'/cars/{car.id}')

        self.assertEqual(response.status_code, 200)

class TestScrapeDataFunction(unittest.TestCase):
    def setUp(self):
        """Set up the test database and patches."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()

        self.patched_scrape_cars = patch('app.scrape_cars')
        self.mock_scrape_cars = self.patched_scrape_cars.start()

        self.patched_car_query_filter_by = patch('app.Car.query.filter_by')
        self.mock_car_query_filter_by = self.patched_car_query_filter_by.start()

        self.patched_db_session_add = patch('app.db.session.add')
        self.mock_db_session_add = self.patched_db_session_add.start()

        self.patched_db_session_commit = patch('app.db.session.commit')
        self.mock_db_session_commit = self.patched_db_session_commit.start()

        self.patched_jsonify = patch('flask.jsonify')
        self.mock_jsonify = self.patched_jsonify.start()

    def tearDown(self):
        self.patched_scrape_cars.stop()
        self.patched_car_query_filter_by.stop()
        self.patched_db_session_add.stop()
        self.patched_db_session_commit.stop()
        self.patched_jsonify.stop()

    def scrape_data(self):
        """Mocked implementation of the scrape_data endpoint."""
        try:
            cars_data = self.mock_scrape_cars()
            for data in cars_data:
                existing_car = self.mock_car_query_filter_by.return_value.first.return_value
                if not existing_car:
                    new_car = MagicMock(spec=Car)
                    new_car.title = data['title']
                    new_car.price = data['price']
                    new_car.details = data['details']
                    self.mock_db_session_add(new_car)
            self.mock_db_session_commit()

            return self.mock_jsonify({'status': 'success', 'message': 'Successfully scraped and loaded data into database.'}), 200
        except Exception as e:
            return self.mock_jsonify({'status': 'error', 'message': str(e)}), 500

    def test_scrape_data_success(self):
        """Test cases for sucess while scrapping data."""
        self.mock_scrape_cars.return_value = [
            {'title': 'Car 1', 'price': '10000', 'details': 'Details 1'},
            {'title': 'Car 2', 'price': '20000', 'details': 'Details 2'}
        ]

        self.mock_car_query_filter_by.return_value.first.return_value = None
        response = self.scrape_data()

        self.assertEqual(response[1], 200)
        self.assertEqual(self.mock_scrape_cars.call_count, 1)
        self.assertEqual(self.mock_db_session_add.call_count, 2)
        self.assertEqual(self.mock_db_session_commit.call_count, 1)

    def test_scrape_data_error(self):
        """Test case returning error while scraping data."""
        self.mock_scrape_cars.side_effect = Exception('Error')

        response = self.scrape_data()
        self.assertEqual(response[1], 500)



if __name__ == '__main__':
    unittest.main()
