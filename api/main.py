from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from deta import Deta

deta = Deta("c0d650br_vmCwwEVhJZpUvTmvWimS48YEAYcoDcA8")

db = deta.Base("bus_details")

app = FastAPI()

fake_db = []

class BusDetails(BaseModel):
    vehicle_id: int
    trip: str
    front_door_entry: int
    front_door_exit: int
    back_door_entry: int
    back_door_exit: int
    trip_count: int
    distress_count: int



@app.get("/")
def read_root():
    return {"greetings": "Welcome to Bus Tracking API!"}


@app.get("/busdetails")
def get_bus_details():
    return next(db.fetch())

@app.get("/busdetails/{vehicle_id}")
def get_bus_detail_by_no(vehicle_id: int):
    item = next(db.fetch({"vehicle_id":vehicle_id}))
    #we can use try method also to handle errors eg:
    # try:
    #     db.delete(1234)
    # except:
    #     return {"error":"delete error"}
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID not found")

@app.post("/busdetails/")
def add_bus_details(bus_details: BusDetails):
    db.put(bus_details.dict())
    return next(db.fetch())[-1]

@app.delete("/busdetails/{vehicle_id}")
def delete_bus_details(vehicle_id: int):
    item = next(db.fetch({"vehicle_id":vehicle_id}))
    if item:
        db.delete(item[0]["key"])
        return {"task":"Deleted Successfully"}
    else:
        raise HTTPException(status_code=404, detail="Vehicle ID not found")

