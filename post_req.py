from fastapi import  FastAPI, Path, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

class Patient(BaseModel):
    id: str
    name : str
    city : str
    age : int
    gender : str
    height : float
    weight : float


def  load_data():
       pass