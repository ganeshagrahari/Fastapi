from pydantic import BaseModel, EmailStr, computed_field
from typing import List, Dict, Optional

class Patient(BaseModel):
    name : str
    email : EmailStr
    age : int
    weight : float # in kg
    height : float # in cm
    married : bool
    allergies : Optional[list[str]] = None
    contact_details : Dict[str,str]

    @computed_field
    @property
    def calculate_bmi(self) ->float:
        bmi = self.weight / ((self.height/100) **2)
        return round(bmi,2)
  

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('BMI:', patient.calculate_bmi)
    print('inserted!')






patient_info = {'name' : 'ganesh', 'email':'ganesh@gmail.com' ,'age':'30','weight':55.5, 'height': 170, 'married' :True,  'contact_details':{'email':'abc@gmail.com','phone':"9044232872"}}

patient1 = Patient(**patient_info)






insert_patient_data(patient1)    





