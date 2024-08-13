from fastapi import FastAPI, HTTPException, Form
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.server_utils import *
from fastapi.staticfiles import StaticFiles
from routers import api 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
app = FastAPI()
app.include_router(api.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}



def main():
    print ('INITIALIZING FASTAPI SERVER')
    uvicorn.run("server_api:app", host=host_ip, port=int(port_num), reload=True)



if __name__ == "__main__":
    main()
