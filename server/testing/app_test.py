import json
import os

os.environ["DB_URI"] = "sqlite:///:memory:"

from flask import request
import ipdb
from app import app, db
from models import Planet, Scientist, Mission


class TestApp:
    """Flask application in app.py"""

    # def test_gets_scientists(self):
    #     """retrieves scientists with GET requests to /scientists."""

    #     with app.app_context():
    #         Scientist.query.delete()
    #         db.session.commit()

    #         albert = Scientist(
    #             name="Albert Einstein",
    #             field_of_study="physics",
    #             avatar="https://placekitten.com/150/150",
    #         )
    #         db.session.add(albert)
    #         db.session.commit()

    #         response = app.test_client().get("/scientists").json
    #         scientists = Scientist.query.all()

    #         assert [scientist["id"] for scientist in response] == [
    #             scientist.id for scientist in scientists
    #         ]
    #         assert [scientist["name"] for scientist in response] == [
    #             scientist.name for scientist in scientists
    #         ]
    #         assert [scientist["field_of_study"] for scientist in response] == [
    #             scientist.field_of_study for scientist in scientists
    #         ]
    #         assert [scientist["avatar"] for scientist in response] == [
    #             scientist.avatar for scientist in scientists
    #         ]

    def test_gets_scientists_by_id(self):
        """retrieves one scientist using its ID with GET request to /scientists/<int:id>."""

        with app.app_context():
            Scientist.query.delete()
            db.session.commit()
            tony_stark = Scientist(
                name="Tony Stark",
                field_of_study="robotics",
                avatar="https://placekitten.com/150/150",
            )
            db.session.add(tony_stark)
            db.session.commit()

            response = (
                app.test_client().get(f"/scientists/{tony_stark.id}").json
            )
            assert response["name"] == tony_stark.name
            assert response["avatar"] == tony_stark.avatar
            assert response["field_of_study"] == tony_stark.field_of_study

    def test_returns_404_if_no_scientist(self):
        """returns an error message and 404 status code when a scientist is searched by a non-existent ID."""

        with app.app_context():
            Scientist.query.delete()
            db.session.commit()

            response = app.test_client().get("/scientists/1")
            assert response.json.get("error")
            assert response.status_code == 404

    def test_creates_scientist(self):
        """creates one scientist using a name, field_of_study, and avatar with a POST request to /scientists."""

        with app.app_context():
            Scientist.query.delete()
            db.session.commit()

            response = app.test_client().post(
                "/scientists",
                json={
                    "name": "Tony Stark",
                    "field_of_study": "robotics",
                    "avatar": "https://placekitten.com/250/250",
                },
            )

            assert response.json["id"]
            assert response.json["name"] == "Tony Stark"
            assert response.json["field_of_study"] == "robotics"
            assert response.json["avatar"] == "https://placekitten.com/250/250"
            tony = Scientist.query.filter(
                Scientist.name == "Tony Stark",
                Scientist.field_of_study == "robotics",
            ).one_or_none()
            assert tony

    def test_400_for_scientist_validation_error(self):
        """returns a 400 status code and error message if a POST request to /scientists fails."""

        with app.app_context():
            Scientist.query.delete()
            db.session.commit()
            response = app.test_client().post(
                "/scientists",
                json={
                    "name": "",
                    "field_of_study": "robotics",
                    "avatar": "https://placekitten.com/250/250",
                },
            )
            assert response.status_code == 400
            assert response.json["error"]

    def test_gets_planets(self):
        """retrieves planets with GET request to /planets"""

        with app.app_context():
            Planet.query.delete()
            db.session.commit()
            planet = Planet(
                name="Mars",
                distance_from_earth="400",
                nearest_star="the sun",
                image="image.jpg",
            )
            db.session.add(planet)
            db.session.commit()

            response = app.test_client().get("/planets").json
            planets = Planet.query.all()

            assert [planet["id"] for planet in response] == [
                planet.id for planet in planets
            ]
            assert [planet["name"] for planet in response] == [
                planet.name for planet in planets
            ]
            assert [planet["distance_from_earth"] for planet in response] == [
                planet.distance_from_earth for planet in planets
            ]
            assert [planet["nearest_star"] for planet in response] == [
                planet.nearest_star for planet in planets
            ]
            assert [planet["image"] for planet in response] == [
                planet.image for planet in planets
            ]

    def test_deletes_planets_by_id(self):
        """deletes planet with DELETE request to /planets/<int:id>."""

        with app.app_context():
            Planet.query.delete()
            db.session.commit()
            planet = Planet(
                name="Mars",
                distance_from_earth="400",
                nearest_star="the sun",
                image="image.jpg",
            )
            db.session.add(planet)
            db.session.commit()

            response = app.test_client().delete(f"/planets/{planet.id}")

            assert response.status_code == 204

            planet = Planet.query.filter(Planet.id == planet.id).one_or_none()
            assert not planet

    def test_returns_404_if_no_planet(self):
        """returns 404 status code with DELETE request to /planets/<int:id> if planet does not exist."""

        with app.app_context():
            Planet.query.delete()
            db.session.commit()

            response = app.test_client().delete("/planets/1")
            assert response.json.get("error")
            assert response.status_code == 404

    def test_creates_missions(self):
        """creates missions with POST request to /missions"""

        with app.app_context():
            Scientist.query.delete()
            db.session.commit()
            tony_stark = Scientist(
                name="Tony Stark",
                field_of_study="robotics",
                avatar="https://placekitten.com/150/150",
            )
            mars = Planet(
                name="Mars",
                distance_from_earth="400",
                nearest_star="the sun",
                image="image.jpg",
            )
            db.session.add_all([tony_stark, mars])
            db.session.commit()

            response = (
                app.test_client()
                .post(
                    "/missions",
                    json={
                        "name": "Iron Man on Mars",
                        "scientist_id": tony_stark.id,
                        "planet_id": mars.id,
                    },
                )
                .json
            )

            assert response["id"]
            assert response["name"] == "Iron Man on Mars"
            assert response["scientist_id"] == tony_stark.id
            assert response["planet_id"] == mars.id

            mission = Mission.query.filter(
                Mission.id == response["id"]
            ).one_or_none()
            assert mission
