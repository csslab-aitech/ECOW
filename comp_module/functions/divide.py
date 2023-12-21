#!/usr/local/bin/python
import os
import json
import time
import subprocess
import argparse
from optprocess import OptProcess
from qsubprocess import QsubProcess
from fileprocess import FileProcess
from status import StatusManager, StatusEnum
from filelock import FileLock

class Process:
    # Variable to store the file directory path
    FILE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Path to the configuration file
    CONFIGFILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__config_files/__config.json'))
    # Path to the file storing solutions (used when the solution file is not specified as an option)
    DEFAULT_SENDFILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__config_files/__send_data.json'))
    
    UNRECEIVE_FILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__error_files/UnReceiveData.json'))
    
    LOCKFILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './.opt.lock'))
    
    
    def __init__(self, filepath=DEFAULT_SENDFILE):
        # 再受信機能実装予定 (qsub未実装)=================================
        parser = argparse.ArgumentParser() 
        parser.add_argument('-re', '--receiveAgain', action='store_true',default=False)
        self.args = parser.parse_args()
        
        # Receive Opt user ID and password from the file here
        json_load = json.load(open(self.CONFIGFILE, 'r'))
        main_json = json_load['main']
        
        if self.args.receiveAgain:
            json_load = json.load(open(self.UNRECEIVE_FILE),'r')
            # キーの取得
            keys = list(json_load.keys())
            tmp = keys[0].split('_')
            datum = json_load[keys[0]]
            # create list of ids
            id_list = [item['id'] for item in datum]
            # create list of values
            value_list = [item['value'] for item in datum]
            sub_to = tmp[0] 
            if sub_to == 'opt':
                user_name = main_json[sub_to]['user_name']
                match_id = tmp[2]
                script = main_json[sub_to]["script"]
                fp = FileProcess(filepath, f"{sub_to}_{match_id}")
                self.sm = StatusManager(f"{sub_to}_{match_id}")
                opt = OptProcess(self.sm, fp, int(match_id), user_name, script,send_id_list=id_list,send_value_list=value_list)
                self.__getProcess = opt.GetProcess
            else:
                qsub_sub_to = tmp[2]
                qsub_json = main_json[self.sub_to][qsub_sub_to]
                script = qsub_json["script"]
                if len(tmp) > 2:
                    model = tmp[3]
                
        self.sub_to = main_json['sub_to']
        
        # Store functions as variables
        if self.sub_to == 'opt':
            # If the argument is 'opt'
            user_name = main_json[self.sub_to]['user_name']
            match_id = main_json[self.sub_to]['match_id']
            script = main_json[self.sub_to]["script"]
            fp = FileProcess(filepath, f"{self.sub_to}_{match_id}")
            self.sm = StatusManager(f"{self.sub_to}_{match_id}")
            opt = OptProcess(self.sm, fp, int(match_id), user_name, script)
            self.__sendProcess = opt.SendProcess
            self.__getProcess = opt.GetProcess
        else:
            # If the argument is 'qsub'
            qsub_sub_to = main_json[self.sub_to]['sub_to']
            qsub_json = main_json[self.sub_to][qsub_sub_to]
            script = qsub_json["script"]
            if qsub_json.get('model'):
                match_id = qsub_json['model']
                filename = f"{self.sub_to}_{qsub_sub_to}_{qsub_json['model']}"
            else:
                match_id = None
                filename = f"{self.sub_to}_{qsub_sub_to}"
            fp = FileProcess(filepath, filename)
            self.sm = StatusManager(filename)
            qsub = QsubProcess(self.sm, fp, script, match_id)
            self.__sendProcess = qsub.SendProcess
            self.__getProcess = qsub.GetProcess
            
        # Pass the file path containing the solutions to be sent to the file processing class and instantiate it
        # Also pass this variable when instantiating the class that will perform the sending process
        self.sendList = fp.getValue(self.DEFAULT_SENDFILE)
        
    # Send
    def Send(self, datalist):
        # Sending process
        self.__sendProcess(datalist)

    # Receive
    def Get(self):
        # Receive process and get evaluation value
        return self.__getProcess()
    
    # History
    def History(self):
        # Display using print
        # Enter matchID or job ID to display
        json_load = json.load(open(self.CONFIGFILE, 'r'))
        user_name = json_load['opt']['user_name']
        print("1: matchID 2: time")
        select = input()
        
        if select == "1":
            print("Specify matchID")
            search_id = input()
            send_stdout = subprocess.check_output(  # Run a command and get the output
                    args=f"opt list solutions --limit 3 --query \"_and: [{{match_id: {{_eq: {search_id}}}}}, {{owner: {{name: {{_eq: {user_name}}}}}}}]\"",
                    shell=True,
                    text=True
                )
            search_data = json.loads(send_stdout) 
            result = ["variable:" + x['variable'] + ", objective:" + x['objective'] for x in search_data['solutions']]
            print(result)
    
    # Execute
    def run(self):
        # not reacquired
        if not self.args.receiveAgain:
            try:
                if self.sub_to == 'opt':
                    # Create a file lock
                    lock = FileLock(self.LOCKFILE)
                    with lock:
                        # Place the main logic of the script here
                        time.sleep(10)
                # Wait until the previous evaluation value is returned
                self.sm.New(StatusEnum.WAITING)
                while True:
                    if self.sm.CheckStatus():
                        break
                # Execute
                self.Send(self.sendList)
                return self.Get()
            except KeyboardInterrupt:
                self.sm.SetStatus(StatusEnum.EXITED_WITH_CtrlC)
        else : 
            # reacquire
            result = self.Get()
            if self.sm.NowStatus() == StatusEnum.EVALUATION_RECEIVED:
                os.remove(self.UNRECEIVE_FILE_PATH)
            return result

if __name__=='__main__':
    p = Process()
    result = p.run()
    print(result)