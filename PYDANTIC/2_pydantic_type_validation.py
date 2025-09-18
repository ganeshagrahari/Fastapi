from pydantic import BaseModel
from typing import List, Dict, Optional

class Patient(BaseModel):
    name : str
    age : int
    weight : float
    married : bool
    allergies : Optional[list[str]] = None
    contact_details : Dict[str,str]
  

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('inserted!')






patient_info = {'name' : 'ganesh', 'age':'30','weight':75.2, 'married' :True,  'contact_details':{'email':'abc@gmail.com','phone':"9044232872"}}

patient1 = Patient(**patient_info)






insert_patient_data(patient1)    





