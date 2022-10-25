from xmlrpc.client import Boolean
from passwordManager.models import Asset
from passwordManager import db
from faker import Faker
import traceback
import logging

def create_assrt(size:int=0,truncate:Boolean=False):
    if truncate:
        Asset.query.delete()
        print("truncated the table Asset")

    faker = Faker()
    instance = [faker.unique.ipv4() for i in range(size)]
    username = [str(faker.profile()["username"]) for i in range(size)]
    password = [str(faker.unique.password()) for i in range(size)]
    other_details = [str(faker.unique.name()) for i in range(size)]

    try:
        for i in range(size):
            vm_to_create = Asset(instance=instance[i], username=username[i], password=password[i], other_details=other_details[i])
            db.session.add(vm_to_create)
            db.session.commit()
            print(f"asset {i+1:4} inserted successfully! with username '{username[i]}'")
        print(f"asset {i+1:4} inserted successfully!")
        return True
    except Exception as e:
        logging.error(traceback.format_exc())

if __name__ == '__main__':
    create_assrt(size=int(input("Enter number records to generate:\n")), truncate=bool(input("truncate table [True/False]:\n")))
