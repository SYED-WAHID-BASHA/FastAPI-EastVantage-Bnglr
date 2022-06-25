from fastapi import Depends, FastAPI, status, Response
from . import model, schemas
from sqlalchemy.orm import Session
from .databases import SessionLocal, engine
from geopy.distance import geodesic
from .get_Coordinates import getCoordinate

app = FastAPI()

model.Base.metadata.create_all(engine)

def getDb():
    db = SessionLocal()
    # SQLAlchemy has a connection pooling mechanism for default.That meand with yield you are creating a single session for each request .  return --> using single database connection for all your app
    try:
        yield db
    finally:
        db.close()


#  creating an address

@app.post("/newAddress", status_code=status.HTTP_201_CREATED)
def create_address(req: schemas.Address, res:Response, db :Session = Depends(getDb)):
    try:
        #  extra space are removed
        name = req.name.strip()
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        pincode = req.pincode

        # location and coordinates using mapquest api
        locationData = getCoordinate(name,addressLine, city, state)
        print(locationData)

        # creating columns for address table
        newAddress = model.Address(
            name= name,
            addressLine = addressLine,
            city = city,
            state = state,
            country = locationData["adminArea1"],
            pincode = pincode,
            longitude =  locationData["latLng"]["lng"],
            latitude =  locationData["latLng"]["lat"],
            mapUrl = locationData["mapUrl"]
        )

        # adding column to table
        db.add(newAddress)
        # method used to confirm the changes by userto database
        db.commit()
        #refresh the window with new address
        db.refresh(newAddress)

        return {
            "status": "ok",
            "data": newAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# reads all the addresses

@app.get("/readAll", status_code=status.HTTP_200_OK)
def get_all_address(res: Response, db :Session = Depends(getDb)):
    try:
        # we get all the data from database and then send to user 
        allAddress = db.query(model.Address).all()
        return{
            "status" :"ok",
            "data" : allAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# we get the addresses which are near to the request body address

@app.get("/readAddressNearest", status_code=status.HTTP_200_OK)
def get_nearest_address(res: Response, name, addressLine, city, state, db :Session = Depends(getDb)):
    try:
        # we get the location & coordinate data from mapquest api 
        locationData = getCoordinate(name, addressLine, city, state)
        quaryCoordinate = locationData["latLng"]

        firstCoordinate = (quaryCoordinate["lat"] , quaryCoordinate["lng"])

        allAddress = db.query(model.Address).all()

        someAddress = []

        
  
        # If the distance is below 100km than only it's save the address to someAddress list. 


        # Here, someAddress will hold all the address that between 200km
      

        for address in allAddress:
            secondCoordinate = (address.latitude, address.longitude)
            distanceBetween = geodesic(firstCoordinate, secondCoordinate).km
            if distanceBetween <= 200:
                someAddress.append(address)
        

        #  nearest data to the user
        return {
            "status": "ok",
            "data" : someAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# update the address with id 

@app.put("/updateAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_address(id, req: schemas.Address, res: Response, db: Session = Depends(getDb)):
    try:
       
        name = req.name.strip()
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        pincode = req.pincode

        # using getcoordinate function from grt_coordinate file to update the changes 
        locationData = getCoordinate(name, addressLine, city, state)

        newAddress = {
            "name": name,
            "addressLine" : addressLine,
            "city" : city,
            "state" : state,
            "country" : locationData["adminArea1"],
            "pincode" : pincode,
            "longitude" :  locationData["latLng"]["lng"],
            "latitude" :  locationData["latLng"]["lat"],
            "mapUrl" : locationData["mapUrl"]
        }

     
        updatedAddress = db.query(model.Address).filter(model.Address.id == id).update(newAddress)

        # if the data is not found in database 
        if not updatedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }
         # method used to confirm the changes by userto database
        db.commit()

        # if the data got sucessfully updated 
        return {
            "status" : "ok",
            "data" : updatedAddress
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }



@app.delete("/deleteAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def delete_address(id, res: Response, db: Session = Depends(getDb) ):
    try:
       
        deletedAddress = db.query(model.Address).filter(model.Address.id == id).delete(synchronize_session=False)

        # if the data is not found in database 
        if not deletedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }
        # method used to confirm the changes by userto database
        db.commit()

       
        return {
            "status" : "ok",
            "data" : deletedAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }
