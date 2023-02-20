from datetime import datetime, date
from pony.orm import db_session


def birth_date_check(v):
    if isinstance(v, date):
        v = v.strftime('%d.%m.%Y')
        return v

    return datetime.strptime(v, "%d.%m.%Y").date()


def was_citizen_born_check(v):
    copy_v = v

    if isinstance(v, str):
        copy_v = datetime.strptime(v, "%d.%m.%Y").date()

    if datetime.now().date() < copy_v:
        raise ValueError('Citizen wasn\'t born at this moment')

    return v


# Check: unique relative ids
def are_unique_relative_id_check(v):
    if len(set(v)) != len(v):
        raise ValueError('Relative IDs must be unique')

    return v


# Check: citizen can't be relative to himself / herself
def is_citizen_relative_to_self_check(cls, v):
    citizen_id = v.get('citizen_id')
    relatives = v.get('relatives')

    if relatives is not None:
        if citizen_id in relatives:
            raise ValueError("Citizen can't be relative to himself/herself")

    return v


# Check: citizen_id is unique in import set
def is_citizen_ids_unique_check(cls, v):
    citizens = v.get('citizens')
    ids = set()

    for c in citizens:
        if c.citizen_id in ids:
            raise ValueError('citizen_id must be unique in import set')

        ids.add(c.citizen_id)

    return v


# Check: data relative is symmetric
def are_relatives_symmetric_check(cls, v):
    citizens = v.get('citizens')

    for citizen in citizens:
        citizen_relatives_ids = citizen.relatives

        for relative in citizens:
            if relative.citizen_id in citizen_relatives_ids:
                relative_relatives_ids = relative.relatives

                if citizen.citizen_id not in relative_relatives_ids:
                    raise ValueError('Data about relatives is not symmetric')

    return v


def clean_from_none(cls, v):
    v = {key: val for key, val in v.items() if val is not None}
    return v


# Convert relatives response to valid format
def relative_to_list(v):
    return [r.citizen_id for r in v]
