from fastapi import FastAPI
from cryptography.fernet import Fernet
from fastapi.responses import JSONResponse
import pymongo
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from models import GetPasswordReq, SetPasswordReq, User

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
handler = Mangum(app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/setpassword")
def SetPassword(request: SetPasswordReq):

    username = request.username
    site = request.site
    sitepassword = request.sitepassword

    user = GetUser(username)
    print(user)
    f = Fernet(user.get("key"))
    encryptedpass = f.encrypt(sitepassword.encode())
    data = {"$set": {
        "username": username,
        "site": site,
        "sitepassword": encryptedpass.decode("utf-8")
    }}
    collection = GetMongoCollection("PassData")
    collection.update_one(
        {"username": username, "site": site}, data, upsert=True)
    return JSONResponse(content={"message": "success"}, status_code=201)


@app.post("/getpassword")
def GetPassword(request: GetPasswordReq):

    username = request.username

    site = request.site
    user = GetUser(username)
    collection = GetMongoCollection("PassData")
    result = collection.find_one(
        {"username": username, "site": site}, {"_id": 0})
    f = Fernet(user.get("key"))
    decryptedpass = f.decrypt(result.get("sitepassword")).decode()
    data = {
        "site": site,
        "password": decryptedpass
    }
    return JSONResponse(content=data, status_code=200)


@app.post("/login")
def login(request: User):

    username = request.username
    password = request.password

    collection = GetMongoCollection("Users")
    user = collection.find_one(
        {"username": username, "password": password}, {"_id": 0})

    if user is None:
        content = {"message": "User not found"}
        return JSONResponse(content=content, status_code=200)
    return JSONResponse(content=user, status_code=200)


@app.post("/signup")
async def signup(request: User):

    username = request.username
    password = request.password

    user = GetUser(username)

    if user is not None:
        content = {"message": "User already exists"}
        return JSONResponse(content=content, status_code=200)

    encryptionkey = GenerateKey()
    data = {
        "username": username,
        "password": password,
        "key": encryptionkey
    }

    collection = GetMongoCollection("Users")
    collection.insert_one(data)

    return JSONResponse(status_code=200)

@app.post("/getsites")
def GetSites(request:User):
    collection = GetMongoCollection("PassData")
    result = collection.find({"username":request.username})
    sites = []
    for site in list(result):
        sites.append(site.get("site"))
    data ={
        "message":"success",
        "data":sites
    }
    return JSONResponse(content=data,status_code=200)

def GetUser(username):
    collection = GetMongoCollection("Users")
    user = collection.find_one({"username": username}, {"_id": 0})
    return user


def GetMongoCollection(collectionName):
    uri = "mongodb+srv://ankur221b:ankur221b@cluster0.sdwqnto.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    # Create a new client and connect to the server
    client = pymongo.MongoClient(uri)
    db = client.get_database("PassManager")
    collection = db.get_collection(collectionName)
    return collection


def GenerateKey():
    key = Fernet.generate_key()
    return key.decode("utf-8")


def SaveKeys(username, key):
    pass
