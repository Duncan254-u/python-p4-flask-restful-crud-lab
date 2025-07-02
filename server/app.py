#!/usr/bin/env python3
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
import os

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/plants', methods=['GET'])
def get_plants():
    plants = Plant.query.all()
    return jsonify([plant.to_dict() for plant in plants])

# FIXED: Combined GET and PATCH into single route
@app.route('/plants/<int:id>', methods=['GET', 'PATCH'])
def plant_by_id(id):
    plant = Plant.query.get_or_404(id)
    
    if request.method == 'GET':
        return jsonify(plant.to_dict())
    
    elif request.method == 'PATCH':
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

@app.route('/plants/<int:id>', methods=['DELETE'])
def delete_plant(id):
    plant = Plant.query.get_or_404(id)
    
    db.session.delete(plant)
    db.session.commit()
    
    # Return empty response with 204 status code
    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555, debug=True)