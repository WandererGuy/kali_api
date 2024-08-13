from fastapi import FastAPI, HTTPException, Form, APIRouter
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
pot_file = config['DEFAULT']['pot_file'] 
router = APIRouter()




# Endpoint to receive an image and start the processing pipeline
@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post ("/extract_hash") 
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
        # result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

        result = subprocess.Popen([command], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Giao tiếp với tiến trình con
        stdout, stderr = result.communicate()

        # In kết quả đầu ra
        print("Output:", stdout)

        # Kiểm tra và in thông báo lỗi nếu có
        if stderr:
            print("Errors:", stderr)

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


@router.post("/HashCrack/")
async def crack(    
    hash_type: str = Form(...),
    hash_file: str = Form(...), 
    wordlist: str = Form(...), 
    attack_mode: str = Form(...),
    rule_path: str = Form(None)
    ):
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
        crack_collection = 'static/cracked_hashes.txt'
        # Check if the value exists in the dictionary keys
        check_value_in_dict(attack_mode, attack_mode_dict)
        check_value_in_dict(hash_type, hash_type_dict)     

        hash_type = str(data_type_translate(hash_type))
        hash_file = clean_path(hash_file)
        wordlist = clean_path(wordlist)
        attack_mode = str(attack_mode_translate(attack_mode))

        
        cracked_hash_result_folder = 'static/cracked_hash'
        filename = generate_unique_filename(cracked_hash_result_folder)
        cracked_hash_result_file = os.path.join(cracked_hash_result_folder,filename)
        # Build the Hashcat command
        command = [
            'hashcat',
            '-m', hash_type,       # Hash type
            '-a', attack_mode,             # Attack mode
            hash_file,            # Hash
            wordlist,               # Wordlist
            # '-o', cracked_hash_result_file
        ]
        if rule_path != None and rule_path != '':
            command.append('-r')
            command.append(rule_path)
        # Run the command

        process = subprocess.Popen(command, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
        if stderr:
            print("Errors:", stderr)

        # Giao tiếp với tiến trình con
        command = [
            'hashcat',
            '-m', hash_type,       # Hash type
            '-a', attack_mode,             # Attack mode
            hash_file,            # Hash
            wordlist,               # Wordlist
            '--show'
            # '-o', cracked_hash_result_file
        ]
        process = subprocess.Popen(command, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if stderr:
            print("Errors:", stderr)

        with open(cracked_hash_result_file, 'w') as f:
            f.write(stdout)

        # if f_data == '':
        #     path = f"http://{host_ip}:{port_num}/{crack_collection}"
        #     return {
        #         "message":'hash has already been cracked before, stored in',
        #         "url":path
        #     }

        # with open (crack_collection, 'a') as f:
        #     f.writelines(f_data)
        # Kiểm tra và in thông báo lỗi nếu có
        # output_check = check_result_available(cracked_hash_result_file)
        if stdout == '' or stdout == None:

        # if output_check == False:
            return {        
            "message": "Wordlist Exhausted. Cannot crack hash"
            }   
        with open(crack_collection, 'a') as f:
            f.writelines(stdout)

        path = f"http://{host_ip}:{port_num}/static/cracked_hash/{filename}"
        bonus_path = f"http://{host_ip}:{port_num}/{crack_collection}"

        return {        
            "message": "Result saved successfully.",   
            "url":path,
            "bonus_message": "Already cracked hash before will be stored in.",   
            "bonus_url":bonus_path
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



