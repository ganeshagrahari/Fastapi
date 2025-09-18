from pydantic import BaseModel


class Address(BaseModel):
    city :str
    state : str
    pin :str

class Patient(BaseModel):
    name : str
    gender : str
    age : int
    address : Address


address_dict = {'city':'Bangalore', 'state':'Karnataka', 'pin':'560037'}
address1 = Address(**address_dict)

patient_dict = {'name':'Ganesh', 'gender':'Male', 'age':30, 'address':address1}

patient1 = Patient(**patient_dict)

print(patient1)
print(patient1.address.city)
print(patient1.address.pin)