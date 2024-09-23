from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
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
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    missions = db.relationship('Mission', back_populates="planet", cascade='all, delete-orphan')

    serialize_rules = ('-missions.planet',)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'distance_from_earth': self.distance_from_earth,
            'nearest_star': self.nearest_star
        }

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    missions = db.relationship('Mission', back_populates="scientist", cascade='all, delete-orphan')

    serialize_rules = ('-missions.scientist',)

    @validates('name')
    def validate_name(self, key, name):
        if name is None or name == '':
            raise ValueError("Name cannot be None or empty.")
        return name

    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if field_of_study is None or field_of_study == '':
            raise ValueError("Field of study cannot be None or empty.")
        return field_of_study

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'field_of_study': self.field_of_study
        }

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    scientist = db.relationship('Scientist', back_populates="missions")
    planet = db.relationship('Planet', back_populates="missions")

    serialize_rules = ('-scientist.missions', '-planet.missions')

    @validates('name')
    def validate_name(self, key, name):
        if name is None or name == '':
            raise ValueError("Name cannot be None or empty.")
        return name

    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if scientist_id is None:
            raise ValueError("Scientist ID cannot be None.")
        return scientist_id

    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if planet_id is None:
            raise ValueError("Planet ID cannot be None.")
        return planet_id

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scientist_id': self.scientist_id,
            'planet_id': self.planet_id,
            'scientist': self.scientist.to_dict(),
            'planet': self.planet.to_dict()
        }