import subprocess
def connect(devices_ip:str)->bool:
    '''
    connect to devices
    return: True or False
    '''
    adb_command = ["adb", "connect", devices_ip]
    try:
        output = subprocess.check_output(adb_command)
        output = output.decode("utf-8").strip()
        print(output)
        if  ("connected to " + devices_ip ) in output :
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return False

def input_text(devices_ip:str, text:str)->bool:
    '''
    input text to devices
    return: True or False
    '''
    adb_command = ["adb", "-s", devices_ip, "shell", "input", "text", text]
    try:
        output = subprocess.check_output(adb_command)
        output = output.decode("utf-8").strip()
        print(output)
        if  ("connected to " + devices_ip ) in output :
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return False

def get_screen_size(devices_ip)->tuple:

    '''
    get emulator screen size
    return: screen size width and high
    '''
    
    try:
        #連接到模擬器
        adb_command=["adb","connect",devices_ip]

        output = subprocess.check_output(adb_command)
        adb_command = ["adb", "-s", devices_ip, "shell", "wm", "size"]
        output = subprocess.check_output(adb_command)

        output = output.decode("utf-8").strip()


        width, height = output.split()[-1].split("x", 1)


        return int(width), int(height)

    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None