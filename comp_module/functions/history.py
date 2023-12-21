import json
import os
import subprocess

class History:
    # Variable to store the file directory path
    FILE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the configuration file
    CONFIGFILE = os.path.normpath(os.path.join(FILE_DIRECTORY, './__config_files/__config.json'))

    # Path to store history
    RESTORE_DIRC = os.path.normpath(os.path.join(FILE_DIRECTORY, './__results_files'))

    def __init__(self):
        json_load = json.load(open(self.CONFIGFILE, 'r'))
        self.user_name = json_load['main']['opt']['user_name']
        history_json = json_load['history']
        self.max_row = history_json['limit']


    def GetHist(self, output_file=''):
        # Display using print
        # Enter matchID or job ID to display
        history_data = []
        
        print("Specify matchID")
        search_id = input()
        send_stdout = subprocess.check_output(  # Run a command and get the output
                args=f"opt list solutions --limit {self.max_row} --query \"_and: [{{match_id: {{_eq: {search_id}}}}}, {{owner: {{name: {{_eq: {self.user_name}}}}}}}]\"",
                shell=True,
                text=True
            )
        search_data = json.loads(send_stdout) 
        print("-" * 45)
        for x in search_data['solutions']:
            print(f"{'date':<15} : {x['created_at']}")
            print(f"{'objective':<15} : {x['objective']}")
            print(f"{'variable':<15} : {x['variable']}")
            print(f"{'info':<15} : {x['info']}")
            print("-" * 45)
        if output_file:
            for x in search_data['solutions']:
                history_data.append({str(x['variable']): {"objective": x['objective'], "date": x['created_at'], "info": x['info']}})
            self.setjson(history_data, output_file)
        # result = ["variable:" + str(x['variable']) + ", objective:" + str(x['objective']) for x in search_data['solutions']]
        # print(result)
        # self.setjson(history_data)



    def setjson(self, setdata, filename):
        filepath = os.path.normpath(os.path.join(self.RESTORE_DIRC, f'./{filename}.json'))
        if not os.path.exists(filepath):
            if setdata is None:
                open(filepath, "w")
            else:
                with open(filepath, "w") as f:
                    json.dump(setdata, f, indent=4)
        else:
            with open(filepath, 'r') as f:
                now_data = json.load(f)
                
            # Add only data that does not exist in the existing data
            for data in setdata:
                key = list(data.keys())[0]
                if key not in [list(d.keys())[0] for d in now_data]:
                    now_data.append(data)
                
            # Write JSON data to the file
            with open(filepath, 'w') as f:
                json.dump(now_data, f, indent=4)
