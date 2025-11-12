from dataclasses import dataclass
from app import db
from flask_hashids import HashidMixin

@dataclass(init=False, repr=True, eq=True)
class Area(HashidMixin, db.Model):
  __tablename__ = 'areas'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
  nombre = db.Column(db.String(100), nullable=False)

  materias = db.relationship("Materia", back_populates="area", cascade="all, delete-orphan")