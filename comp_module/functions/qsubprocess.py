#!/usr/local/bin/python
from subprocess import check_output, CalledProcessError
from status import StatusEnum
import os
import random
import time
import string
import json
from datetime import datetime

SLEEP_TIME = 60

class QsubProcess:
    """Class for sending solutions to Qsub and receiving evaluations.

    Parameters
    ----------
    sm: StatusManager
        Class for recording and checking statuses.
    fp: FileProcess
        Class for executing file-related processes.
    script: string
        Command script for executing send and receive operations using Qsub.
    model: string
        Model information (optional).

    """
    def __init__(self, sm, fp, script, model=None):
        # Record status using sm
        self.sm = sm
        # Store the class for file processing
        self.fp = fp
        # List of files sent
        self.__send_file_list = []
        # List of files generated when evaluations are received
        self.__ofile_list = []
        # List of error files
        self.__efile_list = []
        # List to store sent solutions
        self.__send_value_list = []
        
        self.__result_list =[]
        # Generate template
        if model:
            self.__template = string.Template(script).safe_substitute({"MODEL": model})
        else:
            self.__template = script

    def SendProcess(self, send_data: list):
        """Process for sending solutions.

        Parameters
        ----------
        datalist(list): List of solutions to be sent.
        """
        # Clear each file
        self.__send_file_list.clear()
        self.__ofile_list.clear()
        self.__efile_list.clear()
        self.__send_value_list.clear()
        self.__result_list.clear()

        # Send data (solutions) one by one
        self.sm.SetStatus(StatusEnum.SOLUTION_SENDING)
        # Remove previously sent solutions
        send_data, self.__result_list = self.fp.CheckSolution(values=send_data)
        if not send_data:
            self.sm.SetStatus(StatusEnum.PREVIOUSLY_SOLUTION)
            exit()
        try:
            for data in send_data:
                # Get the current time to include in the file name
                time = datetime.now().strftime("%Y%m%d")
                # Substitute the solution into the template
                script = string.Template(self.__template).safe_substitute({"SOLUTION": json.dumps(data)})
                # Generate a file name
                file_name = "tmp_" + time + "_" + "{:010d}".format(random.randint(0, 10**10)) + ".sh"

                # Input the execution script into the file and generate it
                with open(file_name, "w") as f:
                    f.write(script)

                # Execute the generated file
                # ----- Add exception handling for failed execution
                send_stdout = check_output(
                    args=f"qsub {file_name}",
                    shell=True,
                    text=True
                )
                
                
                # Get the absolute path of the generated file
                create_path = os.path.abspath(os.path.dirname(file_name))
                # Add the expected file names to the respective file lists
                self.__send_file_list.append(file_name)
                self.__ofile_list.append(f"{create_path}/{file_name}.o{send_stdout.split('.')[0]}")
                self.__efile_list.append(f"{create_path}/{file_name}.e{send_stdout.split('.')[0]}")
                # Save the solution to the list
                self.__send_value_list.append(data)
            self.fp.SolutionRestore(self.__send_value_list)
            self.sm.SetStatus(StatusEnum.SOLUTION_SENT)
        except:
            self.sm.SetStatus(StatusEnum.SOLUTION_SENDING_ERROR)
            exit()

    def GetProcess(self):
        """Process for receiving evaluation values."""
        # Lists to store actually generated files
        ofileList = []
        efileList = []
        
        if not self.__send_value_list:
            return self.__result_list
        
        # Receive
        self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVING)
        try:
            while True:
                # Wait for 1 minute
                time.sleep(SLEEP_TIME)

                # Check if a response to the solution has arrived
                # Check if the expected file names have been generated
                for get in self.__ofile_list:
                    # It can also be done using os.path.exists()
                    if os.path.isfile(get):
                        ofileList.append(get)
                # Check if the expected file names have been generated
                for get in self.__efile_list:
                    if os.path.isfile(get):
                        efileList.append(get)

                # Check the consistency between the expected file names and the actually generated file names
                if (set(ofileList) == set(self.__ofile_list)) and (set(efileList) == set(self.__efile_list)):
                    # Exit the loop if everything is present
                    break
        except:
            self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVING_ERROR)
            exit()

        # List to store evaluation values generated from the files
        objectives = []
        info = []
        res_values = []
        # Retrieve evaluation values from files where they should be input
        for get in self.__ofile_list:
            with open(get, 'r') as f:
                tmp = json.loads(f.read())
                objectives.append(tmp['objective'])
                info.append(tmp['info'])
                res_values.append(tmp)

        # Delete all generated files
        for deletefile in [self.__send_file_list, self.__ofile_list, self.__efile_list]:
            self.__FileDelete(deletefile)

        # Return evaluation values
        self.fp.SolutionRestore(self.__send_value_list,objectives,info)
        self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVED)
        extracted_data = [{str(i):{"objective": solution["objective"], "info": solution["info"]}} for i,solution in zip(self.__send_value_list,res_values)]
        for i, item in enumerate(self.__result_list):
            if item == None:
                self.__result_list[i] = extracted_data.pop(0)
        return self.__result_list

    def __FileDelete(self, filelist):
        for file in filelist:
            # It can also be done using os.unlink()
            os.remove(file)
