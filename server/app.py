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

api = Api(app)

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [scientist.to_dict(rules=('-missions',)) for scientist in scientists], 200
    
    def post(self):
        data = request.get_json()
        name = data.get('name')
        field_of_study = data.get('field_of_study')
        try:
            scientist = Scientist(name=name, field_of_study=field_of_study)
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400
    
class SingleScientist(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            return scientist.to_dict(), 200
        else:
            return {'error': 'Scientist not found'}, 404
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
        else:
            return {'error': 'Scientist not found'}, 404
        
    def patch(seld, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist:
            data = request.get_json()
            name = data.get('name')
            field_of_study = data.get('field_of_study')
            try:
                scientist.name = name
                scientist.field_of_study = field_of_study
                db.session.add(scientist)
                db.session.commit()
                return scientist.to_dict(), 202
            except:
                return {'errors': ['validation errors']}, 400
        else:
            return {'error': 'Scientist not found'}, 404
    
api.add_resource(Scientists, '/scientists')
api.add_resource(SingleScientist, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return [planet.to_dict(rules=('-missions',)) for planet in planets], 200
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        scientist_id = data.get('scientist_id')
        planet_id = data.get('planet_id')
        try:
            mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict(), 201
        except:
            return {'errors': ["validation errors"]}, 400

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
