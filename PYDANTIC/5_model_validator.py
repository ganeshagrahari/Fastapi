from pydantic import BaseModel, EmailStr, model_validator
from typing import List, Dict, Optional

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float
    married : bool
    allergies : Optional[list[str]] = None
    contact_details : Dict[str,str]

    @model_validator(mode = 'after')
    def validate_emergency_contact(cls, model):
        if model.age>60 and 'emergency_contact' not in model.contact_details:
            raise ValueError('Emergency contact is required for patients above 60 years')
        return model

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('inserted!')






patient_info = {'name' : 'ganesh','email':'ganesh@gmail.com' ,'age':'65','weight':75.2, 'married' :True,  'contact_details':{'email':'abc@gmail.com','phone':"9044232872", 'emergency_contact':'9044232873'}}

patient1 = Patient(**patient_info)






insert_patient_data(patient1)    





