#!/bin/bash
#flask shell 
from app.models import User,StatusRoute,Station,Faults,Route,Mode
from app import db
admin=User(name="admin",email="admin@admin.com",phone="+972549111254",is_admin=True)
admin.set_password("admin2021")
db.session.add(admin)

station=Station(name="Basic")
station1=Station(name="Station 1")
station2=Station(name="Station 2")
station3=Station(name="Station 3")
station4=Station(name="Station 4")
station5=Station(name="Station 5")
db.session.add(station)
db.session.add(station1)
db.session.add(station2)
db.session.add(station3)
db.session.add(station4)
db.session.add(station5)

fault=Faults(name="High temperature")
fault1=Faults(name="Obstacle")
fault2=Faults(name="Other")
db.session.add(fault)
db.session.add(fault1)
db.session.add(fault2)

status=StatusRoute(name="Done")
status1=StatusRoute(name="In process")
status2=StatusRoute(name="Not performed")
status3=StatusRoute(name="Failure")

db.session.add(status)
db.session.add(status1)
db.session.add(status2)
db.session.add(status3)

mode=Mode(name="Basic")
mode1=Mode(name="Distribution of objects")
mode2=Mode(name="Security patrol")
db.session.add(mode)
db.session.add(mode1)
db.session.add(mode2)
route=Route(name="Basic",status_id=1,mode_id=1)
db.session.add(route)
db.session.commit()
