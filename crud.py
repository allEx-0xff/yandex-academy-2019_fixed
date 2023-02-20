from pony.orm import db_session, select, desc
from schema import CitizenImport, PatchCitizen
from models import Citizen
from typing import List
from datetime import datetime


@db_session
def import_citizens(data: CitizenImport):
    try:
        import_id = select(c for c in Citizen).order_by(desc(Citizen.import_id)).limit(1)[:]
        import_id = import_id[0].import_id + 1

    except:
        import_id = 1

    citizens_schema = data.citizens
    citizen_objects = {}

    for c in citizens_schema:
        citizen_object = Citizen(**c.dict(exclude={"gender", "relatives"}), gender=c.gender.value, import_id=import_id)
        citizen_objects[c.citizen_id] = citizen_object

    # add relatives
    for c in citizens_schema:
        relatives_ids = c.relatives
        citizen_objects[c.citizen_id].relatives = [citizen_objects[relative_id] for relative_id in relatives_ids]

    return import_id


@db_session
def patch_citizen(citizen_id: int, import_id: int, citizen: PatchCitizen):
    citizen_obj = Citizen.get_for_update(citizen_id=citizen_id, import_id=import_id)

    # Parse schema
    for key, value in citizen:
        if key not in ['relatives', 'citizen_id', 'gender']:

            setattr(citizen_obj, key, value)
        elif key == 'gender':
            setattr(citizen_obj, key, citizen.gender.value)

        # patch relatives
        else:
            citizen_obj.relatives = select(c for c in Citizen if c.citizen_id in citizen.relatives
                                           and c.import_id == import_id)[:]

    # FIXED: modify citizens without relative modifications
    return citizen_obj, [r.citizen_id for r in citizen_obj.relatives]


@db_session
def get_citizens_by_import_id(import_id: int):
    citizen_objects = Citizen.select(import_id=import_id).prefetch(Citizen.relatives)[:]
    return citizen_objects


@db_session
def get_gifts_by_import_id(import_id):
    months_info = {str(month): [] for month in range(1, 13)}
    citizens = select(c for c in Citizen if c.import_id == import_id)[:]

    # TODO: check if import_id does not exist

    for c in citizens:
        months_citizen = {str(month): [] for month in range(1, 13)}

        # store info about current citizen's relatives
        for r in c.relatives:
            bd = str(r.birth_date.month)
            months_citizen[bd].append(r.citizen_id)

        # store data to general container
        for m, r_ids in months_citizen.items():

            # empty
            if not r_ids:
                continue

            months_info[m].append({
                'citizen_id': c.citizen_id,
                'presents': len(r_ids)
            })

    return months_info


import numpy as np


@db_session
def get_percentile_towns_age_by_import_id(import_id: int):
    citizens: List[Citizen] = select(c for c in Citizen if c.import_id == import_id)[:]
    towns = set(c.town for c in citizens)

    ages_by_town = {town: np.array([int((datetime.now().date() - c.birth_date).days / 365)
                                    for c in citizens if c.town == town])
                    for town in towns}

    percentiles = {}

    for town, ages in ages_by_town.items():
        percentiles[town] = {'p50': np.percentile(ages, 50),
                             'p75': np.percentile(ages, 75),
                             'p99': np.percentile(ages, 99)}

    return percentiles
