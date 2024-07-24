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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
hashcat_crack_result_file = config['DEFAULT']['hashcat_crack_result_file'] 
extract_hash_result_file = config['DEFAULT']['extract_hash_result_file'] 
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


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
async def extract_hash(    
    hash_type: str = Form(...),
    file_path: str = Form(...)
    ):
    """
    extract hash from file 
    """
    extract_hash_result_folder = "static/extract_hash_results"
    filename = generate_unique_filename(extract_hash_result_folder)
    extract_hash_result_file = extract_hash_result_folder + '/' + filename

    hash_type = data_type_translate(hash_type)
    command = gen_extract_command(hash_type, file_path)
    # command.append('>')
    # command.append(extract_hash_result_file)    
    os.makedirs('static/extract_hash_results', exist_ok=True)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
        print (result.stdout)
        if result.stdout != None and result.stdout != "":
            with open (extract_hash_result_file, 'w') as f :
                f.write(result.stdout)
            path = f"http://{host_ip}:{port_num}/static/extract_hash_results/{filename}"
            return {        
                # "stdout": result.stdout,
                # "stderr": result.stderr,
                "message": "Result saved successfully.",   
                "url":path}
        else:
            return {                
                "message": "Cannot extract file. Something is wrong",   
                }

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
