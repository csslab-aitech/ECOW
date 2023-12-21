import os
import csv
import json
import datetime
from enum import Enum, auto

class StatusEnum(Enum):
    # ステータスの状態を表す
    # 待機中
    WAITING = auto()
    # 送信済の解
    PREVIOUSLY_SOLUTION = auto()
    # 解の送信中
    SOLUTION_SENDING = auto()
    # 解の送信完了
    SOLUTION_SENT = auto()
    # 解の送信エラー
    SOLUTION_SENDING_ERROR = auto()
    # 評価値の受信中
    EVALUATION_RECEIVING = auto()
    # 評価値の受信完了
    EVALUATION_RECEIVED = auto()
    # 評価値の受信エラー
    EVALUATION_RECEIVING_ERROR = auto()
    # Ctrl-Cで終了
    EXITED_WITH_CtrlC = auto()
    
    def __str__(self):
        if self == StatusEnum.WAITING:
            return "Waiting"
        elif self == StatusEnum.PREVIOUSLY_SOLUTION:
            return "Previously Sent Solution"
        elif self == StatusEnum.SOLUTION_SENDING:
            return "Solution Sending"
        elif self == StatusEnum.SOLUTION_SENT:
            return "Solution Sent"
        elif self == StatusEnum.SOLUTION_SENDING_ERROR:
            return "Solution Sending Error"
        elif self == StatusEnum.EVALUATION_RECEIVING:
            return "Evaluation Value Receiving"
        elif self == StatusEnum.EVALUATION_RECEIVED:
            return "Evaluation Value Received"
        elif self == StatusEnum.EVALUATION_RECEIVING_ERROR:
            return "Evaluation Value Receiving Error"
        elif self == StatusEnum.EXITED_WITH_CtrlC:
            return "Exited with Ctrl-C"


class StatusManager():
    """Class to check and modify the status of a sent solution.
    Parameters
    ----------
    recipient:
        Recipient of the solution.
    """

    # Variable to store the file directory path
    __FILEDIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Path to the configuration file
    __CONFIGFILE = os.path.normpath(os.path.join(__FILEDIRECTORY, './__config_files/__config.json'))

    # Path to store the status
    __STATUS_FILE = os.path.normpath(os.path.join(__FILEDIRECTORY, './__config_files/__status.csv'))

    def __init__(self, recipient):
        # Store values in the configuration file
        json_load = json.load(open(self.__CONFIGFILE, 'r'))
        status_json = json_load['status']
        self.max_row = status_json['limit']

        # Keep track of the recipient
        self.recipient = recipient

        # Path to store the status in a CSV file
        status_path = os.path.normpath(os.path.join(__file__, '../../__config_files/__status.csv'))
        self.status_file = status_path

        # Store the position in the file
        self.number = self.GetRowCount(self.status_file)

    
    # Function to display the status of solutions in the terminal
    def Show():
        """Function to display the status of solutions in the terminal
        """
        try:
            status_file = os.path.normpath(os.path.join(__file__, '../../__config_files/__status.csv'))
            with open(status_file, mode="r") as file:
                reader = csv.reader(file)
                print(f"{'date':<20} | {'sub_to':<10} | {'status':<15}")
                print("-" * 45)
                # Convert the reader to a list
                data_list = list(reader)
                # Reverse the list and print the first 10 rows
                for row in reversed(data_list):
                    date, recipient, status = row
                    print(f"{date:<20} | {recipient:<10} | {status:<15}")
                print("-" * 45)
        except FileNotFoundError:
            print("Status file not found.")
            exit()

    
    # Function to record the submission of a new solution
    def New(self, status=''):
        try:
            self.TrimCsvFile()
            with open(self.status_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([current_time, self.recipient, status])
                self.number = self.GetRowCount(self.status_file)  # Store the position in the file
        except Exception as e:
            print(f"Unable to set the status. Error: {e}")
            exit()
            
    def NowStatus(self):
        """returns current status
        
        """
        # Read the CSV file
        extracted_rows = []
        with open(self.status_file, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                extracted_rows.append(row)
        
        # Determine the current status
        for i, row in enumerate(extracted_rows):
            if i == self.number:
                return row[2]
        
    
    # Function to modify the status of a sent solution
    def SetStatus(self, new_status):
        # Check if it is an Enum member and convert to string if applicable
        expected_statuses = list(StatusEnum)
        if new_status in expected_statuses:
            new_status = str(new_status)

        # Read the CSV file
        extracted_rows = []
        with open(self.status_file, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                extracted_rows.append(row)

        # Find the specified row and update the status
        for i, row in enumerate(extracted_rows):
            if i == self.number:
                row[0] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row[2] = new_status

        # Write the updated content to the CSV file
        with open(self.status_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            # Write data to the CSV file
            for row in extracted_rows:
                writer.writerow(row)

    # 現在の件数を返す関数
    def GetRowCount(self, file_path):
        try:
            with open(file_path, mode="r") as file:
                reader = csv.reader(file)
                row_count = sum(1 for row in reader)
                return row_count
        except FileNotFoundError:
            return 0  # ファイルが存在しない場合は0を返す
    
    # Adjust the CSV file to a specified number of rows
    def TrimCsvFile(self):
        try:
            with open(self.status_file, mode="r") as file:
                rows = list(csv.reader(file))

            if self.number >= self.max_row:
                with open(self.status_file, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    # Write the last (max_row-1) rows to the file
                    for row in rows[-(self.max_row - 1):]:
                        writer.writerow(row)
        except Exception as e:
            print(f"Unable to trim the CSV file. Error: {e}")
            exit()

    
    # Function to check if it is possible to send a new solution
    def CheckStatus(self):
        try:
            # Open the CSV file and store it in a list
            with open(self.status_file, mode="r") as file:
                rows = list(csv.reader(file))

            checks = [str(StatusEnum.EVALUATION_RECEIVED),
                      str(StatusEnum.EVALUATION_RECEIVING_ERROR),
                      str(StatusEnum.SOLUTION_SENDING_ERROR),
                      str(StatusEnum.PREVIOUSLY_SOLUTION),
                      str(StatusEnum.EXITED_WITH_CtrlC)]
            rows = rows[:self.number]

            for row in reversed(rows):
                if self.recipient == row[1]:
                    if row[2] in checks:
                        return True
                    else:
                        return False
        except Exception as e:
            print(f"Unable to check the CSV file. Error: {e}")
            self.SetStatus(StatusEnum.SOLUTION_SENDING_ERROR)
            exit()

        return True
