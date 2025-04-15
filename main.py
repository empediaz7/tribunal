from datetime import date, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import (create_access_token, hash_password, verify_password,
                  verify_token)
from database import (  # Asegúrate de importar el engine correctamente
    SessionLocal, engine)
from models import Base  # Asegúrate de importar el Base desde models.py
from models import Person, User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, mejor poner solo el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PersonBase(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    fecha_nacimiento: date
    numero_oficio: str
    tribunal: str
    observaciones: Optional[str] = None
    foto: Optional[str] = None

    class Config:
        orm_mode = True

class PersonCreate(PersonBase):
    nombre: str
    apellido: str
    cedula: str
    fecha_nacimiento: date
    numero_oficio: str
    tribunal: str
    observaciones: Optional[str] = None
    foto: Optional[str] = None

class PersonUpdate(PersonBase):
    pass

class PersonInDB(PersonBase):
    id: int

    class Config:
        orm_mode = True

class PersonOut(PersonBase):
    id: int

# Define la función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

@app.post("/register/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/persons/", response_model=PersonOut)
def create_person(person: PersonCreate, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    new_person = Person(**person.dict())
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person

@app.get("/persons/", response_model=list[PersonOut])
def get_persons(token: str = Depends(verify_token), db: Session = Depends(get_db)):
    return db.query(Person).all()

@app.get("/persons/{person_id}", response_model=PersonOut)
def get_person(person_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@app.put("/persons/{person_id}", response_model=PersonOut)
def update_person(person_id: int, updated: PersonCreate, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    for key, value in updated.dict().items():
        setattr(person, key, value)
    db.commit()
    db.refresh(person)
    return person

@app.delete("/persons/{person_id}")
def delete_person(person_id: int, token: str = Depends(verify_token), db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return {"message": "Person deleted successfully"}
