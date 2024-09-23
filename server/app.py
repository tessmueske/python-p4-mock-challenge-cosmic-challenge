#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def scientists():

    if request.method == 'GET':

        scientists = Scientist.query.all()

        if scientists:
            return [scientist.to_dict() for scientist in scientists], 200

        else:
            return '', 404

    if request.method == 'POST':
        
        data = request.get_json()

        try:
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )

            db.session.add(new_scientist)
            db.session.commit()

            return new_scientist.to_dict(), 201

        except ValueError as e:
            return {'errors': ["validation errors"]}, 400

@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):

    scientist = Scientist.query.filter(Scientist.id == id).first()

    if request.method == 'GET':
        
        if scientist:
            return {
            'id': scientist.id,
            'name': scientist.name,
            'field_of_study': scientist.field_of_study,
            'missions': [{'id': mission.id, 'name': mission.name} for mission in scientist.missions]
        }, 200
        return {'error': 'Scientist not found'}, 404

    if request.method == 'PATCH':

        data = request.get_json()

        if scientist is None:
            return {'error': 'Scientist not found'}, 404

        if 'name' in data:
            if not data['name']: 
                return {'errors': ['validation errors']}, 400
            scientist.name = data['name']

        if 'field_of_study' in data:
            if not data['field_of_study']:
                return {'errors': ['validation errors']}, 400
            scientist.field_of_study = data['field_of_study']

        db.session.commit()

        return {
            'id': scientist.id,
            'name': scientist.name,
            'field_of_study': scientist.field_of_study,
            'missions': [{'mission': mission.name, 'name': mission.name} for mission in scientist.missions]
        }, 202

    if request.method == 'DELETE':

        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            response = make_response('', 204)  # Create an empty response
            response.headers['Content-Type'] = 'application/json'  # Set content type
            return response

        else:
            return {'error': 'Scientist not found'}, 404

@app.route('/planets', methods=['GET'])
def planets():

    if request.method == 'GET':
        
        planets = Planet.query.all()

        if planets:
            return [planet.to_dict() for planet in planets], 200

        else:
            return '', 404

@app.route('/missions', methods=['GET', 'POST'])
def missions():

    if request.method == 'GET':

        missions = Mission.query.all()

        if missions:
            return [mission.to_dict() for mission in missions], 200

        else:
            return '', 404

    if request.method == 'POST':

        data = request.get_json()

        try:
            new_mission = Mission(
                name = data['name'],
                scientist_id = data['scientist_id'],
                planet_id = data['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()

            return new_mission.to_dict(), 201

        except ValueError as e:
            return {'errors': ["validation errors"]}, 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
