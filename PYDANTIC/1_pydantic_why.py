def insert_patient_data(name : str, age : int):
    if type(name) == str and type(age) ==int:
        if age < 0:
            raise ValueError('Age cannot be negative!')
        else:
            print(name)
            print(age)
            print('inserted into data!')
    else:
        print("Invalid data type.")    

def update_patient_data(name : str, age : int):
   if type(name) == str and type(age) ==int:
        if age < 0:
            raise ValueError('Age cannot be negative!')
        else:
            print(name)
            print(age)
            print('inserted into data!')
   else:
        print("Invalid data type.")    

insert_patient_data('John', 30)   