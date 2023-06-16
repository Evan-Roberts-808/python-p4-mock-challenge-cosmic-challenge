from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, UniqueConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    missions = db.relationship('Mission', back_populates='planet')
    scientists = association_proxy("missions", "scientist")

    serialize_rules = ('-missions.planet', '-scientists.planets')

    def __repr__(self):
        return f'<Planet {self.id}: {self.name}>'

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    missions = db.relationship('Mission', back_populates='scientist')
    planets = association_proxy("missions", "planet")

    serialize_rules = ("-missions.scientist", "-planets.scientists") 

    def __repr__(self):
        return f'<Scientist {self.id}: {self.name}>'
    
    @validates('name')
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError("Scientist must have name.")
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if field_of_study:
            return field_of_study
        raise ValueError("Scientist must have field of study.")

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'
    __table_args__ = (UniqueConstraint("name", "scientist_id", "planet_id"),)
    serialize_rules = ("-scientist.missions", "-planet.missions")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name) < 0:
            raise ValueError('Mission must have name')
        return name
    
    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if scientist_id:
            return scientist_id
        raise ValueError('Mission must have scientist ID')
    
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if planet_id:
            return planet_id
        raise ValueError('Mission must have planet ID')

# add any models you may need. 