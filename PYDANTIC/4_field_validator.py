from pydantic import BaseModel, EmailStr, AnyUrl, Field, field_validator
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float
    married : bool
    allergies : Optional[list[str]] = None
    contact_details : Dict[str,str]

    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        valid_domains = ['hdfc.com','icici.com']
        #abc@gmail.com
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError(f'Email domain must be one of {valid_domains}')
        
        return value
    
    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()

    @field_validator('age')
    @classmethod
    def validate_age(cls,value):
        if 0 <value <120:
            return value
        raise ValueError('Age must be between 0 and 120')


  

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('inserted!')






patient_info = {'name' : 'ganesh','email':'ganesh@hdfc.com', 'age':'30','weight':75.2, 'married' :True,  'contact_details':{'email':'abc@gmail.com','phone':"9044232872"}}

patient1 = Patient(**patient_info) #validation happens here-> type conversion -> validators are called






insert_patient_data(patient1)    





