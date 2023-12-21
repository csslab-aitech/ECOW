#!/usr/local/bin/python
from subprocess import check_output, CalledProcessError
import subprocess
# from module.main import Process
from .history import History
from .fileprocess import FileProcess
from .status import StatusManager
import argparse
import os

# Variable to store the file directory path
FILE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# File path where unsubmitted solutions are stored
UNRECEIVE_FILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__error_files/UnReceiveData.json'))

class Main():
    """
        class that executes the module
        
    """
    def __init__(self) -> None:
        parser = argparse.ArgumentParser() 
        parser.add_argument('-s', '--status', action='store_true',default=False)
        parser.add_argument('-hi','--history',action='store_true',default=False)
        parser.add_argument('-o', '--output',action='store',nargs='?',type=str,default='')
        self.args = parser.parse_args()
    
    # 実装予定の再受信機能のための関数
    def __Check_Received(self):
        """Check if the evaluation value of the submitted solution was received when executed previously

        Parameters
        ----------
        check (boolean):
            Returns True if received.
        """
        check = None
        # Check if you received it
        if os.path.exists(UNRECEIVE_FILE):
            if os.path.getsize(UNRECEIVE_FILE) != 0:
                check = True
            else:
                check = False
                os.remove(UNRECEIVE_FILE)
        else:
            check =False

        return check
    
    
    def Run(self, value=None, no_wait=False):
        """
        Function that executes the module
        
        Parameters
        ----------
        value (list):
            the solution you want to send
        available (boolean):
            Whether to receive an evaluation value as a return value. True if received
        """
        out = None
        
        if self.__Check_Received():
            print("There are solutions that have not been received. Would you like to receive it again?")
            while True:
                user_input = input("Please answer Yes or No (y/n): ").lower()
                if user_input in ["y", "yes"]:
                    # Stores the path of the executable file to run in the background (using subprocess)
                    run_path = os.path.normpath(os.path.join(dir_file,'./divide.py'))
                    # execution command
                    cmd = ['python3', run_path, '-re']
                    # Do not get evaluation value
                    process = subprocess.Popen(cmd,stdout=subprocess.DEVNULL)
                elif user_input in ["n", "no"]:
                    
                    break
                else:
                    print("Invalid input. Please answer with 'y' or 'n'.")
            
        dir_file = os.path.dirname(os.path.abspath(__file__))
        # Run solution submission in background (using subprocess) only if option is not selected
        if(self.args.status) :
            # Make sending/receiving information visible
            StatusManager.Show()
        elif(self.args.history) :
            # View history information
            History().GetHist(self.args.output)
        else :
            if value:
                FileProcess().setValue(values=value)
            # Stores the path of the executable file to run in the background (using subprocess)
            run_path = os.path.normpath(os.path.join(dir_file,'./divide.py'))
            # execution command
            cmd = ['python3', run_path]
            # Whether or not to obtain the evaluation value (set with the argument available)
            if no_wait:
                # Do not get evaluation value
                process = subprocess.Popen(cmd,stdout=subprocess.DEVNULL)
                out = None
                
            else:
                try:
                    # Get evaluation value
                    process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                    out, err = process.communicate()
                    out = eval(out)
                except Exception as e:
                    print(f"{e.__class__.__name__}: {e}")
                    return None
            
            return out