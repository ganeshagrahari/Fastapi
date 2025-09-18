from pydantic import BaseModel, EmailStr, AnyUrl , Field
from typing import List, Dict, Optional, Annotated

class Patient(BaseModel):
    name : Annotated[str, Field(max_length=50, title="Name of the patient",description="Give name of the patient in less then 50 charactors",examples=['Ganesh', 'Vishul', 'Aman'])]
    email : EmailStr
    age : int = Field(gt=0,lt=120)
    linkedin_url : AnyUrl
    weight : Annotated[float, Field(gt=0,strict=True)]
    married : Annotated[bool, Field(default=False, description= "is the patient married or not")]
    allergies : Annotated[Optional[List[str]],Field(default=None,max_length=5)]
    contact_details : Dict[str,str]
  

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print(patient.allergies)
    print('inserted!')






patient_info = {'name' : 'ganesh', 'email':'abc@gmail.com','linkedin_url':'http://linkedin.com/1322','age':'30','weight':75.2, 'married' :True,  'contact_details':{'phone':"9044232872"}}

patient1 = Patient(**patient_info)






insert_patient_data(patient1)    





