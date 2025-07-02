from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

class Plant(db.Model):
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    is_in_stock = db.Column(db.Boolean, nullable=False, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'price': self.price,
            'is_in_stock': self.is_in_stock
        }

# Routes

# GET all plants
@app.route('/plants', methods=['GET'])
def get_plants():
    plants = Plant.query.all()
    return jsonify([plant.to_dict() for plant in plants])

# GET single plant
@app.route('/plants/<int:id>', methods=['GET'])
def get_plant(id):
    plant = Plant.query.get_or_404(id)
    return jsonify(plant.to_dict())

# POST new plant
@app.route('/plants', methods=['POST'])
def create_plant():
    data = request.get_json()
    
    new_plant = Plant(
        name=data.get('name'),
        image=data.get('image'),
        price=data.get('price'),
        is_in_stock=data.get('is_in_stock', True)
    )
    
    db.session.add(new_plant)
    db.session.commit()
    
    return jsonify(new_plant.to_dict()), 201

# PATCH update plant
@app.route('/plants/<int:id>', methods=['PATCH'])
def update_plant(id):
    plant = Plant.query.get_or_404(id)
    data = request.get_json()
    
    # Update only the fields that are provided in the request
    if 'name' in data:
        plant.name = data['name']
    if 'image' in data:
        plant.image = data['image']
    if 'price' in data:
        plant.price = data['price']
    if 'is_in_stock' in data:
        plant.is_in_stock = data['is_in_stock']
    
    db.session.commit()
    
    return jsonify(plant.to_dict())

# DELETE plant
@app.route('/plants/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = Plant.query.get_or_404(id)
    
    db.session.delete(plant)
    db.session.commit()
    
    # Return empty response with 204 status code
    return make_response('', 204)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Plant not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)