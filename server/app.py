#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Planet, Scientist, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict()
                      for scientist in Scientist.query.all()]
        return make_response(jsonify(scientists), 200)

    def post(self):
        data = request.get_json()

        try:
            new_scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study'),
                avatar=data.get('avatar')
            )
            db.session.add(new_scientist)
            db.session.commit()

            return new_scientist.to_dict(), 201
        except:
            return {"error": "400: Validation error"}, 400


api.add_resource(Scientists, '/scientists')


class ScientistById(Resource):
    def get(self, id):
        try:
            scientist = Scientist.query.filter_by(id=id).first()
            return make_response(scientist.to_dict(), 200)
        except:
            return {"error": "404: Scientist not found"}, 404

    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404

        try:
            data = request.get_json()
            for attr in data:
                setattr(scientist, attr, data[attr])
            db.session.add(scientist)
            db.session.commit()

            return make_response(scientist.to_dict(), 200)
        except:
            return {"error": "400: Validation error"}, 400

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            Mission.query.filter_by(scientist_id=id).delete()
            db.session.delete(scientist)
            db.session.commit()
            return make_response("", 204)
        else:
            return {"error": "404: Scientist not found"}, 404


api.add_resource(ScientistById, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        planets = [planet.to_dict() for planet in Planet.query.all()]
        return make_response(planets, 200)


api.add_resource(Planets, '/planets')


class Missions(Resource):
    def post(self):
        try:
            data = request.get_json()

            new_mission = Mission(
                name=data.get('name'),
                scientist_id=data.get('scientist_id'),
                planet_id=data.get('planet_id')
                )
            db.session.add(new_mission)
            db.session.commit()

            return make_response(new_mission.to_dict(), 200)
        except:
            return {"error": "400: Validation error"}, 400


api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
