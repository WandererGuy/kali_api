from fastapi import FastAPI, HTTPException
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from dateutil import parser
import os 
from pydantic import BaseModel, validator, ValidationError
import re
import unidecode
from utils.server_utils import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
hashcat_crack_result_file = config['DEFAULT']['hashcat_crack_result_file'] 
extract_hash_result_file = config['DEFAULT']['extract_hash_result_file'] 
app = FastAPI()


class InputData2(BaseModel):
    hash_type : str
    file_path :str 

class InputData1(BaseModel):
    hash_type : str
    hash_file : str
    wordlist : str
    attack_mode : str
# Endpoint to receive an image and start the processing pipeline
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post ("/extract_hash") 
async def extract_hash(data: InputData2):
    """
    extract hash from file 
    """
    hash_type = data.hash_type
    file_path = data.file_path
    hash_type = data_type_translate(hash_type)
    command = gen_extract_command(hash_type, file_path)
    command.append('>')
    command.append(extract_hash_result_file)    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        with open (extract_hash_result_file, 'w') as f :
            f.write(result.stdout)
        return {"message":"Done", "result_file": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/HashCrack/")
async def crack(data: InputData1):
    """
    Hashcat crack given hash using wordlist. 
    Args:
        hash_type : type of the hash 
        wordlist : wordlist path 
        attack?_mode : attacking mode 
    return:
        plaintext of given hash if cracked 
    """
    try:
        hash_type = data.hash_type
        hash_type = str(data_type_translate(hash_type))
        hash_file = clean_path(data.hash_file)
        wordlist = clean_path(data.wordlist)
        attack_mode = data.attack_mode

        # Build the Hashcat command
        command = [
            'hashcat',
            '-m', hash_type,       # Hash type
            '-a', attack_mode,             # Attack mode, 0 = Straight
            hash_file,            # Hash
            wordlist,               # Wordlist
            '-o', hashcat_crack_result_file
        ]

        # Run the command
        subprocess.run(command, stdout=subprocess.PIPE, text=True)
        with open (hashcat_crack_result_file, 'r') as f :
            data = f.readlines()
        return {"message":"Done", "result_file": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    print ('INITIALIZING FASTAPI SERVER')
    uvicorn.run("server_api:app", host=host_ip, port=int(port_num), reload=True)



if __name__ == "__main__":
    main()
