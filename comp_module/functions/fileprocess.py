#!/usr/local/bin/python
import json
import os

NO_EXISTING = None


class FileProcess:
    # Variable to store the file directory path
    FILE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Append matchID or jobID to the end of the saved file name
    RESULT_RESTORE_FILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__results_files/ResultFile.json'))
    # File path where the solution to be sent is stored
    SEND_FILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__config_files/__send_data.json'))
    # File path where unsubmitted solutions are stored
    UNRECEIVE_FILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__error_files/UnReceiveData.json'))

    def __init__(self, sendfile=SEND_FILE, resultID=RESULT_RESTORE_FILE):
        """
        Classes that work with files

        Parameters
        ----------
        sendfile: string
            Defaults to SEND_FILE.
        resultID: string
            efaults to RESULT_RESTORE_FILE.
        """
        self.send_data = self.getValue(sendfile)
        self.resultID = resultID
        if resultID is not self.RESULT_RESTORE_FILE:
            self.RESULT_RESTORE_FILE = os.path.normpath(os.path.join(self.FILE_DIRECTORY, f'./__restore_files/resultFile_{resultID}.json'))

    def CheckSolution(self, values: list):
        """When sending a solution, check if it has already been sent.

        Parameters
        ----------
        values (list):
            list to check

        Returns
        --------
        add_data (list):
            Data list to send
        previously (list):
            A data list that stores the results of solutions that have already been sent.
        """
        # Variable to store the result of the already submitted solution
        previously = [NO_EXISTING for _ in values]
        # Variable to store the data list to send
        add_data = []
        # Perform the check process only if the following conditions are met
        # 1. Save file exists
        # 2. The contents of the saved file are not empty
        if os.path.exists(self.RESULT_RESTORE_FILE) and os.path.getsize(self.RESULT_RESTORE_FILE) != 0:
            # Get data (saved data) from the saved file
            with open(self.RESULT_RESTORE_FILE, 'r') as file:
                    now_data = json.load(file)

            # Store only keys of saved data in list
            solutions_list = [list(d.keys())[0] for d in now_data]
            now_list = []
            for s in solutions_list:
                item_list = eval(s)
                if isinstance(item_list, list):
                    now_list.append(item_list)

            # Store solutions that are not in the saved data in the list as data to be sent
            add_data = [v for v in values if v not in now_list]
            # Solutions that existed in the saved data are stored in the list as existing data
            previously = [v for v in values if v in now_list]
            
            # If there is existing data, retrieve the corresponding results from the saved file.
            if previously:
                target_keys = previously.copy()
                # Convert list to string
                converted_keys = [str(key) for key in target_keys]
                # Extract only elements with specified key
                previously.clear()
                for converted_key in converted_keys:
                    tmp_item = None
                    for item in now_data:
                        if converted_key in item:
                            tmp_item = item
                            break
                    previously.append(tmp_item)
            else:
                # If there is no existing data, store None for the number of solutions to be sent.
                for _ in values:
                    previously.append(NO_EXISTING)

            return add_data, previously
        else:
            add_data = values
            return add_data, previously

    def SolutionRestore(self, datum, values = None, info = None):
        """Save evaluation values for sent solutions.

        Parameters
        ----------
        datum (list) :
            Sent solutions
        values (list) :
            Evaluation values for sent solutions
        info (list) :
            'info' of received evaluation value data item
        """
        if values is None:
            values = []
            for _ in datum:
                values.append(NO_EXISTING)
        
        if info is None:
            info = []
            for _ in datum:
                info.append(NO_EXISTING)
        
        # Prepare data for storage
        add_data = [{str(s): {"objective": v, "info": i}} for s, v, i in zip(datum, values, info)]

        # If the save file does not exist, generate it
        if not os.path.exists(self.RESULT_RESTORE_FILE) or os.path.getsize(self.RESULT_RESTORE_FILE) == 0:
            self.NewCreateFile(self.RESULT_RESTORE_FILE, add_data)
        else:
            with open(self.RESULT_RESTORE_FILE, 'r') as f:
                now_data = json.load(f)
                
            # Add only data that does not exist in the existing data
            for data in add_data:
                key = list(data.keys())[0]
                # If there is no data in the solution save file
                if key not in [list(d.keys())[0] for d in now_data]:
                    now_data.append(data)
                else:
                    # If there is data in the solution save file
                    # If the required key value is None, replace it with a new value
                    for d in now_data:
                        # get list of keys
                        keys = list(d.keys())
                        # Access the value using the first key
                        first_key = keys[0]
                        # Get the required key
                        nested_data = d[first_key]
                        # Get list of keys as a list
                        nested_keys = list(nested_data.keys())
                        for nested_key in nested_keys:
                            if nested_data[nested_key] is None:
                                # Update the data if the required data is None
                                for i in range(len(add_data)):
                                    if first_key in add_data[i]:
                                        change_index = i
                                        nested_data[nested_key] = add_data[change_index][first_key][nested_key]
                        d[first_key] = nested_data

            # Write JSON data to the file
            with open(self.RESULT_RESTORE_FILE, 'w') as f:
                json.dump(now_data, f, indent=4)

    def NewCreateFile(self, filename, data=None):
        """Function for creating a new file.

        Parameters
        ----------
        filename (string):
            File name
        data (list):
            Data to be stored in the file
        """
        if data is None:
            open(filename, "w")
        else:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)

    def getValue(self, filename):
        """Function for reading files for sent solutions.

        Parameters
        ----------
        filename (string):
            File name
        """
        # Read JSON file
        with open(filename, 'r') as file:
            solutions = json.load(file)
            return solutions['value']
    
    
    def ReceivingError(self, value, id):
        """If an error occurs during reception, store the unreceived solution

        Parameters
        ----------
            value (list):
                Unreceived solution
            id (list):
                ID you should have received
        """
        trans_data = [{"id":i, "value" : v} for i,v in zip(id,value)]
        output_data = {
            str(self.RESULT_RESTORE_FILE): trans_data
        }
        
        with open(self.UNRECEIVE_FILE, 'w') as f:
            f.write(json.dumps(output_data, indent=4))

    def setValue(self, values, filename=None):
        """Function to write solutions to the JSON file used for sending.

        Parameters
        ----------
        values : list
            Solutions to be written
        filename : string
            File used for sending
        """
        if filename is None:
            filename = self.SEND_FILE
        else:
            filename = os.path.normpath(os.path.join(self.FILE_DIRECTORY, filename))

        # Read JSON file
        with open(filename, 'r') as file:
            json_values = json.load(file)
        
        # Check if there are no lists in the list
        contains_no_list = all(not isinstance(item, list) for item in values)
        
        # What to do if the argument is not a double list
        set_list = []
        if contains_no_list:
            set_list.append(values)
        else:
            set_list = values.copy()

        json_values['value'] = set_list

        with open(filename, "w") as f:
            json.dump(json_values, f, indent=4)
