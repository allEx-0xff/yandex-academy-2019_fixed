from fastapi import FastAPI, Response
from schema import CitizenImport, PatchCitizen, PatchCitizenResponse, CitizensResponse, MonthsGiftBuyers
from crud import import_citizens, patch_citizen, get_citizens_by_import_id, get_gifts_by_import_id, \
    get_percentile_towns_age_by_import_id

app = FastAPI()


@app.post('/imports')
def import_c(citizens: CitizenImport):
    i_id = import_citizens(citizens)
    return {'import_id': i_id}


@app.patch('/imports/{import_id}/citizens/{citizen_id}')
def patch_c(import_id: int, citizen_id: int, citizen: PatchCitizen):

    # SEE : FIXED FOR
    citizen_obj, relatives = patch_citizen(citizen_id, import_id, citizen)
    data = PatchCitizenResponse.from_orm(citizen_obj)
    data.relatives = relatives

    return {"data": data}


@app.get('/imports/{import_id}/citizens')
def get_c_by_import_id(import_id: int):

    citizen_objects = get_citizens_by_import_id(import_id)
    data = CitizensResponse(data=citizen_objects)
    return {'citizens': data}


@app.get('/imports/{import_id}/citizens/birthdays', status_code=200)
def get_gifts_buyers_import_id(import_id: int):
    report = get_gifts_by_import_id(import_id)
    data = MonthsGiftBuyers(jan=report['1'], feb=report['2'], mar=report['3'], apr=report['4'], may=report['5'],
                            jun=report['6'], jul=report['7'], aug=report['8'], sep=report['9'], oct=report['10'],
                            nov=report['11'], dec=report['12'])
    return {"data": data}


@app.get('/imports/{import_id}/towns/stat/percentile/age', status_code=200)
def get_stat_by_import_id(import_id: int):
    report = get_percentile_towns_age_by_import_id(import_id)
    return {'data': report}
