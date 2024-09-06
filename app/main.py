from pydantic import BaseModel
from typing import Literal
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()


class Unchi(BaseModel):
    unchiText: Literal[123] | Literal['うんち']


@app.get('/', response_model=Unchi)
def read_Unchi():
    unchi = Unchi(unchiText=123)
    return JSONResponse(content=jsonable_encoder(unchi))
