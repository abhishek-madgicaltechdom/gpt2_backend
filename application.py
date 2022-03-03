from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
import pickle
import crud
import model
import schema
from db_handler import SessionLocal, engine
from pydantic import BaseModel
from datetime import datetime

now = datetime.now()

model.Base.metadata.create_all(bind=engine)


# Class describes Bank Note
class BankNote(BaseModel):
    variance: float 
    skewness: float 
    curtosis: float 
    entropy: float


class Prompt(BaseModel):
    prompt: str
    description: str

# initiating app
app = FastAPI(
    title="Bank Prediction App",
    description="You can perform CRUD operation by using this API",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pickle_in = open("model_bin","rb")
classifier=pickle.load(pickle_in)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/', response_model=List[schema.API])
def retrieve_all_api_called(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    api = crud.get_all_api_called(db=db, skip=skip, limit=limit)
    print('=================', api)
    return api


# Prediction Route
@app.post('/product-description')
def product_description(data:Prompt, db: Session = Depends(get_db)):
    print('data typeeee  -----', type(data))
    data = data.dict()
    prompt = data['prompt']
    description = data['description']
    
    crud.add_data_into_db(db=db, api_id='1', api=prompt, description=description, api_type='Prediction of bank note', time=f'{now}')

    return {
        'message': 'Success'
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3030)