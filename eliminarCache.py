#Found existing installation: pytube 15.0.0
#Uninstalling pytube-15.0.0:
#  Would remove:
#    c:\users\sebax\appdata\local\programs\python\python312\lib\site-packages\pytube-15.0.0.dist-info\*
#    c:\users\sebax\appdata\local\programs\python\python312\lib\site-packages\pytube\*
#    c:\users\sebax\appdata\local\programs\python\python312\scripts\pytube.exe


import os
import shutil

def remove_pycache(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"Removed: {pycache_path}")

# Define the path to your site-packages directory
site_packages_path = r"C:\Users\sebax\AppData\Local\Programs\Python\Python312\Lib\site-packages"

remove_pycache(site_packages_path)
