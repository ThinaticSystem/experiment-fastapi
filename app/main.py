from fastapi.testclient import TestClient
from typing_extensions import deprecated
from pydantic import BaseModel
from typing import Literal
from fastapi import APIRouter, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# API Routers
v1 = APIRouter(deprecated=True)
v2 = APIRouter(deprecated=True)
v3 = APIRouter()
apis = [v1, v2, v3]

# ReadNewResource


@v3.get('/newResource', response_model=Literal['newResource'])
def new_resource():
    return 'newResource'

# ReadOnigiri


class OnigiriV2(BaseModel):
    taste: list[str]


@deprecated('Use Onigiri instead')
class OnigiriV1(BaseModel):
    taste: str


@v2.get('/onigiri', response_model=OnigiriV2)
def read_onigiri_v2():
    onigiri = OnigiriV2(taste=['ツナマヨ', '昆布'])
    return JSONResponse(content=jsonable_encoder(onigiri))


@v1.get('/onigiri', response_model=OnigiriV1)
def read_onigiri_v1():
    onigiri = OnigiriV1(taste='ツナマヨ')
    return JSONResponse(content=jsonable_encoder(onigiri))

# ReadUnchi


class UnchiV3(BaseModel):
    unchiText: Literal['おうんち']


@deprecated('Use Unchi instead')
class UnchiV2(BaseModel):
    unchiText: Literal['うんち']


@v3.get('/unchi', response_model=UnchiV3)
def read_unchi_v3():
    unchi = UnchiV3(unchiText='おうんち')
    return JSONResponse(content=jsonable_encoder(unchi))


@v2.get('/unchi', response_model=UnchiV2)
def read_unchi_v2():
    unchi = UnchiV2(unchiText='うんち')
    return JSONResponse(content=jsonable_encoder(unchi))


app = FastAPI()

# Add APIs


def prefix_of(version: int):
    return f'/v{version}'


for index, api in enumerate(apis):
    version = index + 1
    prefix = prefix_of(version)

    # NOTE: include_router() は先勝ちで登録される

    # このバージョンでスナップショットされた API を登録する
    app.include_router(api, prefix=prefix)
    # このバージョン以前にスナップショットされた API を登録する
    for previous_api in reversed(apis[:index]):
        app.include_router(previous_api, prefix=prefix)

# Test

if True:
    client = TestClient(app)

    # ReadNewResource API is only available in v3
    v1_new_resource_response = client.get('/v1/newResource')
    assert v1_new_resource_response.status_code == 404
    v2_new_resource_response = client.get('/v2/newResource')
    assert v2_new_resource_response.status_code == 404
    v3_new_resource_response = client.get('/v3/newResource')
    assert v3_new_resource_response.json() == 'newResource'

    # ReadOnigiri API has changed in v2
    v1_onigiri_response = client.get('/v1/onigiri')
    assert v1_onigiri_response.json() == {'taste': 'ツナマヨ'}
    v2_onigiri_response = client.get('/v2/onigiri')
    assert v2_onigiri_response.json() == {'taste': ['ツナマヨ', '昆布']}
    v3_onigiri_response = client.get('/v3/onigiri')
    assert v3_onigiri_response.json() == {'taste': ['ツナマヨ', '昆布']}

    # ReadUnchi API is only available in v2 and above
    # ReadUnchi API has changed in v3
    v1_unchi_response = client.get('/v1/unchi')
    assert v1_unchi_response.status_code == 404
    v2_unchi_response = client.get('/v2/unchi')
    assert v2_unchi_response.json() == {'unchiText': 'うんち'}
    v3_unchi_response = client.get('/v3/unchi')
    assert v3_unchi_response.json() == {'unchiText': 'おうんち'}
