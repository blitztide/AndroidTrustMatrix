import requests
import time
from ppadb.client import Client as AdbClient
from bs4 import BeautifulSoup
from PIL import Image


import AndroidTrustMatrix.config as Config
import AndroidTrustMatrix.adb as adb

proxies = {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        }

install_x = 505
install_y = 558

def check_installbutton(file):
    rgb_image = file.convert('RGB')
    r,g,b = rgb_image.getpixel((576,585))

    #Check if the button is present
    if r==1 and g == 135 and b == 95:
        return True
    return False

def Search(app):
    """Search for app in store and return True if available"""
    url = f"https://play.google.com/store/apps/details?id={app}"
    response = requests.get(url,proxies=proxies,headers=headers)
    if response.status_code == 404:
        print(f"{app} not found: {response.status_code}")
        return False
    elif response.status_code == 200:
        soup = BeautifulSoup(response.text,'html.parser')
        meta = soup.find('meta',attrs={'itemprop':'price'})
        if meta['content'] == None:
            return True
        if meta['content'] == "0":
            print(f"{app} found")
            return True
        else:
            # Return false as we don't want to pay for this
            print(f"{app} found, but paid! Price: {meta['content']}")
            return False
    else:
        print(f"{app} not found: {response.status_code}")
        return False

def Download(app):
    """Downloads the app and returns a file object, None on error"""
    # Connect to adb server
    host,port = Config.get_adb_config()
    client = AdbClient(host,port)
    # check all devices for app
    app_location = None
    devices = client.devices()
    for device in devices:
        if device.is_installed(app):
            print(f"{device} has {app}")
            app_location = device
    #if not found, force install
    if app_location == None:
        device = devices[0]
        adb.unlock(device)
        adb.home(device)
        adb.Market_App(device,app)
        time.sleep(2)
        screenshot = device.screencap()
        installable = check_installbutton(screenshot)
        if not installable:
            adb.lock(device)
            print(f"App: {app} not installable on device: {device.serial}")
            return None
        adb.click(device,install_x,install_y)
        adb.lock(device)
        adb.waitinstall(device,app)
       
    # Extract file from phone
    adb.download_apk(device,app)

    # Load file into memory
    file = open(Config.get_temp_apk_path(),"rb")
    apk = file.read()
    file.close()

    # Remove apk from all phones to save space  
    for device in devices:
        if device.is_installed(app):
            adb.remove(device,app)
    
    return apk

def isUP():
    """Check connection to play.google.com and to phone"""
    #Checking google play
    try:
        response = requests.head("https://play.google.com",proxies=proxies,headers=headers,timeout=10)
    except requests.exceptions.Timeout:
        return False
    #Checking phone connection
    host,port = Config.get_adb_config()
    client = AdbClient(host,port)
    devices = client.devices()
    for device in devices:
        value = adb.hello(device)
        if value != "hello":
            return False
    return True

if __name__ == "__main__":
    import hashlib
    app = "com.termux"
    if Search(app):
        apk = Download(app)
        md5sum = hashlib.md5(apk).digest()
        print(f"Filehash: {md5sum}")