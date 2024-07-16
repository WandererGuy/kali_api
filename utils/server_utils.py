def gen_extract_command(hash_type, file_path):
    match hash_type:
        case 22100:
            command = [
                'bitlocker2john',
                file_path
            ]
            return "Handled case one"
        case 11600:
            command = [
                '7z2john',
                file_path
            ]        
        case 13600:
            command = [
                'zip2john',
                file_path
            ]
        case 13000:
            command = [
                'rar2john',
                file_path
            ]
        case _:
            return "Default case"
    return command


def data_type_translate(data_name):
    hash_dict = {
        'MD5': 0,
        'BitLocker': 22100,
        '7-Zip': 11600,
        'WinZip': 13600,
        'RAR5': 13000
    }    
    return hash_dict[data_name]
    
def clean_path (path):
    path = '/mnt/'+ path
    path = path.replace('D:', 'd').replace('C:','c').replace('E:','e').replace('F:','f')
    return path

def refine_hash (hash_type, hash):
    match hash_type:
        case 22100:
            command = [
                'bitlocker2john',
                
            ]
            return "Handled case one"