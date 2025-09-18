from pydantic import BaseModel

class Patient(BaseModel):
    name : str
    age : int




patient_info = {'name' : 'ganesh', 'age':30}

patient1 = Patient(**patient_info)

def insert_patient_data(patient : Patient):

    print(patient.name)
    print(patient.age)
    print('inserted!')




insert_patient_data(patient1)    





