from passwordManager.models import VM
from passwordManager import db
from faker import Faker
import traceback
import logging

def create_assrt(size:int=0):
    faker = Faker()
    hostip = [faker.unique.ipv4() for i in range(size)]
    username = [str(faker.profile()["username"]) for i in range(size)]
    password = [str(faker.unique.password()) for i in range(size)]

    try:
        for i in range(size):
            vm_to_create = VM(hostip=hostip[i], username=username[i], password=password[i])
            db.session.add(vm_to_create)
            db.session.commit()
            print(f"asset {i+1:4} inserted successfully! with username '{username[i]}'")
        return True
    except Exception as e:
        logging.error(traceback.format_exc())

if __name__ == '__main__':
    create_assrt(size=int(input("Enter number records to generate:\n")))
