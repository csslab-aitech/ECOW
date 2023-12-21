#!/usr/local/bin/python
from subprocess import check_output, CalledProcessError
from status import StatusEnum
import time
import json
import string

SLEEP_TIME = 60

class OptProcess:
    """
    Class for sending solutions to and receiving evaluations from the OPT server.

    Parameters
    ----------
    sm: StatusManager
        Class for recording and checking statuses.
    fp: FileProcess
        Class for executing file-related processes.
    id: int
        ID of the server to send solutions to.
    username: string
        Registered username.
    script: string
        Command script for executing send and receive operations on the OPT server.
    send_id_list:
        List of sent solution IDs used when re-receiving
    send_value_list:
        List of sent solutions used when re-receiving
    """
    def __init__(self, sm, fp, id, username, script, send_id_list=None, send_value_list = None):
        # Record status using sm
        self.sm = sm
        # Use this variable for file processing
        self.fp = fp

        # Lists to store IDs of sent solutions and received evaluation values
        self.__send_id_list = send_id_list if send_id_list else []
        self.__res_id_list = []

        # Variable to store sent solutions
        self.__send_value_list = send_value_list if send_id_list else []
        
        # Variable to store received
        self.__result_list = []
        # Generate templates
        send = string.Template(script['send']).safe_substitute({"ID": id})
        get = string.Template(script['get']).safe_substitute({"ID": id, "USERNAME": username})
        self.__script = {
            "send": send,
            "get": get
        }

    def SendProcess(self, data: list):
        """
        Sending process: Use the opt command to send data.

        Parameters
        ----------
        data (list): List of solutions.
        """
        self.__send_id_list.clear()
        self.__send_value_list.clear()
        self.__result_list.clear()
        try:
            self.sm.SetStatus(StatusEnum.SOLUTION_SENDING)
            # Remove previously sent solutions
            check_data, self.__result_list = self.fp.CheckSolution(values=data)
            if not check_data:
                self.sm.SetStatus(StatusEnum.PREVIOUSLY_SOLUTION)
                
            else:
                for i in check_data:
                    send_stdout = check_output(
                        args=string.Template(self.__script["send"]).safe_substitute({"SOLUTION": i}),
                        shell=True,
                        text=True
                    )
                    send_data = json.loads(send_stdout)
                    self.__send_id_list.append(send_data['insert_solutions_one']['id'])
                    self.__send_value_list.append(i)
                
                self.fp.SolutionRestore(self.__send_value_list)
                self.sm.SetStatus(StatusEnum.SOLUTION_SENT)
        except Exception as e:
            print(check_data)
            if not check_data:
                self.sm.SetStatus(StatusEnum.PREVIOUSLY_SOLUTION)
                exit()
            else:
                self.sm.SetStatus(StatusEnum.SOLUTION_SENDING_ERROR)
                exit()

    def GetProcess(self):
        """
        Retrieval process: Return results when all solutions are finished.
        Return None if retrieval of solutions fails.
        """
        if not self.__send_value_list:
            return self.__result_list
        
        if not self.__send_id_list:
            return self.__result_list
        
        self.__res_id_list.clear()
        # Receive
        self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVING)
        while True:
            # Wait for 1 minute
            time.sleep(SLEEP_TIME)
            if not self.__send_id_list:
                self.sm.SetStatus(StatusEnum.PREVIOUSLY_SOLUTION)
                exit()
            try:
                stdout = check_output(
                    args=string.Template(self.__script["get"]).safe_substitute({"SENDLISTSIZE": len(self.__send_id_list)}),
                    shell=True,
                    text=True
                )
            except CalledProcessError:
                if not self.__send_id_list:
                    self.sm.SetStatus(StatusEnum.PREVIOUSLY_SOLUTION)
                    exit()
                else:
                    self.fp.ReceivingError(value=self.__send_value_list,id=self.__send_id_list)
                    self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVING_ERROR)
                    exit()

            res = json.loads(stdout)
            # Check for errors and other problems
            err_flag = self.__Opt_check(res)

            if not err_flag:
                res['solutions'] = sorted(res['solutions'], key=lambda x: x['id'])
                break
        
        
        # Return objectives
        values = [x['objective'] for x in res['solutions']]
        info = [x['info'] for x in res['solutions']]
        self.fp.SolutionRestore(self.__send_value_list,values,info=info)
        self.sm.SetStatus(StatusEnum.EVALUATION_RECEIVED)
        # return values
        # Extract objective and info values
        extracted_data = [{str(solution["variable"]):{"objective": solution["objective"], "info": solution["info"]}} for solution in res["solutions"]]
        for i, item in enumerate(self.__result_list):
            if item == None:
                self.__result_list[i] = extracted_data.pop(0)
        return self.__result_list

    def __Opt_check(self, res):
        # If any of the elements "objective", "evaluation_error", and "scoring_error" of the received element is not null,
        # It is assumed that the reception has been completed and is stored in the "id" value list.
        res_id_list = []
        for x in res['solutions']:
            has_valid_objective = x["objective"] is not None
            has_valid_evaluation_error = x['evaluation_error'] is not None
            has_valid_scoring_error = x['scoring_error'] is not None

            if has_valid_objective or has_valid_evaluation_error or has_valid_scoring_error:
                res_id_list.append(x['id'])
        
        # List received IDs
        self.__res_id_list = res_id_list
        
        if len(self.__res_id_list) < len(self.__send_id_list):
            return True

        # Compare sent IDs with received IDs to ensure correctness
        if set(self.__res_id_list) == set(self.__send_id_list):
            return False
        else:
            return True
