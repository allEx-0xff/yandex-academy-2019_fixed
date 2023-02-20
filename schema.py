from pydantic import BaseModel, PositiveInt, validator, root_validator, Field, ValidationError
from enum import Enum
from typing import List
from validators import *


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'


class Citizen(BaseModel):
    citizen_id: PositiveInt
    town: str
    street: str
    building: str
    apartment: PositiveInt
    name: str
    birth_date: date
    gender: Gender
    relatives: List[PositiveInt]

    _birth_date_check = validator('birth_date', allow_reuse=True, pre=True)(birth_date_check)
    _are_unique_relative_id_check = validator('relatives', allow_reuse=True)(are_unique_relative_id_check)
    _is_citizen_relative_to_self_check = root_validator(allow_reuse=True)(is_citizen_relative_to_self_check)
    _was_citizen_born_check = validator('birth_date', allow_reuse=True)(was_citizen_born_check)

    class Config:
        min_anystr_length = 1


class CitizenImport(BaseModel):
    citizens: List[Citizen]

    _is_citizen_ids_unique_check = root_validator()(is_citizen_ids_unique_check)
    _are_relatives_symmetric_check = root_validator()(are_relatives_symmetric_check)


class PatchCitizen(Citizen):
    _clean_from_none = root_validator()(clean_from_none)

    class Config:
        def prepare_field(field) -> None:
            field.required = False


class PatchCitizenResponse(Citizen):
    import_id: PositiveInt

    # Convert birth_date from DB response to valid format
    _birth_date_check = validator('birth_date', allow_reuse=True)(birth_date_check)

    # Convert relatives response from DB response to valid format
    _relative_list_convert = validator('relatives', pre=True, allow_reuse=True)(relative_to_list)

    class Config:
        orm_mode = True


class CitizensResponse(BaseModel):
    data: List[PatchCitizenResponse]

    # Convert data response to valid format
    @validator('data', pre=True)
    def relative_to_list(cls, v):
        return [citizen for citizen in v]

    class Config:
        orm_mode = True


class GiftBuyer(BaseModel):
    citizen_id: int
    presents: int


class MonthsGiftBuyers(BaseModel):
    jan: List[GiftBuyer] = Field(alias='1')
    feb: List[GiftBuyer] = Field(alias='2')
    mar: List[GiftBuyer] = Field(alias='3')
    apr: List[GiftBuyer] = Field(alias='4')
    may: List[GiftBuyer] = Field(alias='5')
    jun: List[GiftBuyer] = Field(alias='6')
    jul: List[GiftBuyer] = Field(alias='7')
    aug: List[GiftBuyer] = Field(alias='8')
    sep: List[GiftBuyer] = Field(alias='9')
    oct: List[GiftBuyer] = Field(alias='10')
    nov: List[GiftBuyer] = Field(alias='11')
    dec: List[GiftBuyer] = Field(alias='12')

    class Config:
        allow_population_by_field_name = True
