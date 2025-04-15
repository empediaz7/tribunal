from sqlalchemy import Column, Date, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    cedula = Column(String, unique=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    numero_oficio = Column(String, unique=True, nullable=False)  # Aseguramos que sea único
    tribunal = Column(String, nullable=False)
    observaciones = Column(Text, nullable=True)
    foto = Column(String, nullable=True)  # Guardamos la URL de la foto o la ruta al archivo

    def __repr__(self):
        return f"<Person(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, cedula={self.cedula})>"