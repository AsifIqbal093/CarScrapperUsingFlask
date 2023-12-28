import os
import unittest
from app import app, db  # Replace 'your_flask_app' with your actual Flask app name
from app import Car  # Import your Car model

from dotenv import load_dotenv
load_dotenv()

class CarModelTest(unittest.TestCase):
    """This class contains test cases for CarModel."""
    def setUp(self):
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("POSTGRES_DB")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up the test database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_car(self):
        """Test creating a new Car instance."""
        car = Car(
            title='Test Car',
            price='10000',
            details='Engine-CC 1800'
        )

        with app.app_context():
            db.session.add(car)
            db.session.commit()

            # Retrieve the car from the database
            retrieved_car = Car.query.get(car.id)

        # Assert that the retrieved car has the correct attributes
        self.assertEqual(retrieved_car.title, 'Test Car')
        self.assertEqual(retrieved_car.price, '10000')
        self.assertEqual(retrieved_car.details, 'Engine-CC 1800')

    def test_serialize_car(self):
        """Test the serialization of a Car instance."""
        car = Car(
            title='Test Car',
            price='Test Price',
            details='Test Details'
        )

        with app.app_context():
            db.session.add(car)
            db.session.commit()

            # Serialize the car
            serialized_car = car.serialize()

        # Assert that the serialized car has the correct structure
        self.assertEqual(serialized_car['id'], car.id)
        self.assertEqual(serialized_car['title'], 'Test Car')
        self.assertEqual(serialized_car['price'], 'Test Price')
        self.assertEqual(serialized_car['details'], 'Test Details')

if __name__ == '__main__':
    unittest.main()
