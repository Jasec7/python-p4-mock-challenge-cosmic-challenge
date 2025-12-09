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


@app.route('/')
def home():
    return 'To the infinite and beyond'

class Scientists(Resource):
    def get(self):
        scientist = [scientist.to_dict(only=('id','name','field_of_study')) for scientist in Scientist.query.all()]
        return make_response(jsonify(scientist), 200)
    
    def post(self):
        data = request.get_json()

        try:
            new_scientist = Scientist(
                name = data['name'],
                field_of_study = data['field_of_study']
            )

            db.session.add(new_scientist)
            db.session.commit()

        except ValueError:
            return {"errors":["validation errors"]}, 400
        
        return make_response(jsonify(new_scientist.to_dict()), 201)
    
class Scientists_Id(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id = id).first()

        if not scientist:
            return {'error':"Scientist not found"}, 404
        
        return make_response(jsonify(scientist.to_dict()), 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        data = request.get_json()

        if not scientist:
            return {'error':'Scientist not found'}, 404
        
        try:
            for attr in data:
                setattr(scientist, attr, data.get(attr))

            db.session.add(scientist)
            db.session.commit()
        except ValueError:
            return {"errors":["validation errors"]}, 400
        
        return make_response(jsonify(scientist.to_dict()), 202)
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id = id).first()

        if not scientist:
            return {'error':'Scientist not found'}, 404
        
        db.session.delete(scientist)
        db.session.commit()

        return make_response(jsonify(), 204)
    
class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(only=('id','name','distance_from_earth','nearest_star')) for planet in Planet.query.all()]
        return make_response(jsonify(planets), 200)
    
class Missions(Resource):
    def post(self):
        data = request.get_json()

        try:
            new_mission = Mission(
                name = data['name'],
                scientist_id = data['scientist_id'],
                planet_id = data['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()

        except ValueError:
            return {'errors':['validation errors']}, 400
        
        return make_response(jsonify(new_mission.to_dict()), 201)

api.add_resource(Scientists,'/scientists')
api.add_resource(Scientists_Id,'/scientists/<int:id>')
api.add_resource(Planets,'/planets')
api.add_resource(Missions,'/missions')
if __name__ == '__main__':
    app.run(port=5555, debug=True)
