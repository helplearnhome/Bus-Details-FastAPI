from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from deta import Deta
from datetime import date
from typing import Optional
import re


deta = Deta()

db = deta.Base("bus_details")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BusDetails(BaseModel):
    vehicle_id: int 
    date_field: str
    trip: str
    front_door_entry: int
    front_door_exit: int
    back_door_entry: int
    back_door_exit: int
    trip_count: int
    distress_count: int

class UpdatedBusDetails(BaseModel):
    trip: str = None
    front_door_entry: int = None
    front_door_exit: int = None
    back_door_entry: int = None
    back_door_exit: int = None
    trip_count: int = None
    distress_count: int = None

@app.get("/")
async def read_root():
    return {"greetings": "Welcome to the Bus Tracking API!"}

@app.get("/busdetails")
async def get_bus_details():
    return next(db.fetch())

@app.get("/busdetails/vehicle_id/{vehicle_id}") #alternative you don't need an endpoint to be speicified at all!
async def get_bus_detail_by_no(vehicle_id: int,date_field: str=None):
    
    if date_field == None:
        json_item = next(db.fetch({"vehicle_id":vehicle_id}))
    else:
        json_item = next(db.fetch({"vehicle_id":vehicle_id,"date_field":date_field}))
    return json_item

@app.post("/busdetails/")
async def add_bus_details(bus_details: BusDetails):
    current_object_vehicle_id = bus_details.dict()["vehicle_id"]
    current_object_date_field = bus_details.dict()["date_field"]
    if re.match("^(0[1-9]|[12][0-9]|3[01])[-](0[1-9]|1[012])[-](20)\d\d$",current_object_date_field):
        json_item = next(db.fetch({"vehicle_id":current_object_vehicle_id, 'date_field':current_object_date_field}))
        if json_item:
            raise HTTPException(status_code=409, detail="Bus with same vehicle_id and date field exist")
        else:
            db.put(bus_details.dict())
            return next(db.fetch())[-1]
    else:
        raise HTTPException(status_code=400, detail="Invalid Date")

@app.delete("/busdetails/vehicle_id/{vehicle_id}")
async def delete_bus_details(vehicle_id: int,date_field: str=None):
    if date_field == None:
        json_item = next(db.fetch({"vehicle_id":vehicle_id}))
    else:
        json_item = next(db.fetch({"vehicle_id":vehicle_id,"date_field":date_field}))
    if json_item:
        for dictionary in json_item:
            db.delete(dictionary["key"])
        return {"task":"Deleted Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID/Date Field not found")

@app.put("/busdetails/vehicle_id/{vehicle_id}/{date_field}")
async def update_bus_details(vehicle_id: int, updated_bus_details: UpdatedBusDetails, date_field: Optional[str]=None):
    json_item = next(db.fetch({"vehicle_id":vehicle_id, "date_field":date_field}))
    if json_item == []:
        raise HTTPException(status_code=404, detail="Vehicle ID/Date Field not found")
    item_key = json_item[0]["key"]
    updated_dictionary_of_bus_details = {k:v for k,v in updated_bus_details.dict().items() if (v is not None)}
    db.update(updated_dictionary_of_bus_details,item_key)
    return db.get(item_key)