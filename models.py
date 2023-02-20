from datetime import date
from pony.orm import *

db = Database()


class Citizen(db.Entity):
    id = PrimaryKey(int, auto=True)
    import_id = Required(int)
    citizen_id = Required(int)
    town = Required(str)
    street = Required(str)
    building = Required(str)
    apartment = Required(int)
    name = Required(str)
    birth_date = Required(date)
    gender = Required(str)
    relatives = Set('Citizen', reverse='relatives')


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)
