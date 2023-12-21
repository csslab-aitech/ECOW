---
layout: default
title: "ECOW Document"
lang: en
next_page: overview
---

# ECOW(Evolutionary Competition Opt Wrapper)

- Module Overview
- Module Features
- Setup
- Usage
- ECOW Tutorial

## Module Overview
In [evolutionary computation competitions](https://ec-comp.jpnsec.org/), solutions are submitted and evaluations are received using the 'opt' command. However, users were required to manually associate the submitted solutions with their corresponding evaluation values. As a result, participants waist not less time for managing solutions and hard to focus on the competition.

To manage solution-evaluation value pairs, we developed ECOW (Evolutionary-computation Competition Opt-command Wrapper), which is a Python module to wrappe for the 'opt' command that includes solution management features. By utilizing the ECOW, users can automatically manage usernames and problem numbers, prevent duplicate solution submissions, and save a list of solution-evaluation value pairs.

## Module Features

- Solution Submission and Evaluation Reception
    The `Run` function which submits a list of solutions is available as follows
    ```python
    from ECOW.comp_module.functions.main import Main

    def Run(solutions = None, no_wait=False):
        p = Main()
        result = p.Run(solutions, no_wait)
        return result

    if __name__ == '__main__':
        res = Run([[2,4],[4,4]])
    ```

    There are two methods for submitting solutions:<br>
    1. If only the list of solutions is passed, it means the argument `no_wait` has default value (False), wait until the evaluation of all solutions is completed.
    2. If both the list of solutions and no_wait=True are passed as arguments, immediately receive the return value None, and the evaluation scores are received in the background and they are saved to a JSON file.

    There are also two methods for receiving evaluation scores.<br>
    1. The evaluation data received from the server is returned as a list (`no_wait=False`).
    2. Reading the evaluation scores saved in a JSON file after the evaluation data is revieved from the server (`no_wait=True`).

- Options
    When Main class gets a specific argument, the following processes are called instead of submitting solutions
    - Display status (`-s, --status`)
        Output the status of the submitted solutions to standard output.
    - Display history (`-hi, --history`)
        Outputs the evaluation scores and submission date/time information of previous solutions sent with the specified matchID to standerd output.
        By adding (`-o, --output`) with a file name, you can save the information to the file instead of printing.

## Setup
- Installation of `opt` is required.
    Instructions for installing opt can be found [here](https://ec-comp.jpnsec.org/competitions/tutorial).

- Installation of `python` is required.
- Module installation is required.
    `pip install filelock`

## Usage
1. Edit __config.json file including username, destination (subto, matchID), etc.
2. Execute the following code

```python
from ECOW.run import Run
Run(list_of_solutions)
```

The results will be saved in the __restore_files directory.

The list_of_solutions should be given manually by yourself or automatically by other codes.

## ECOW Tutorial
Perform the operations outlined in the Evolutionary Computation Competition [tutorial](https://ec-comp.jpnsec.org/competitions/tutorial) using the provided module.

### Configure the destination settings for submission.
Change the value of the `user_name` key in `__config.json` to the one you registered on opthub, and update the value of the `match_id` key to the matchID of the problem you want to submit. Since tutorial matchID is `1`, set `match_id: "1"`.

```json:__config.json
{
    "main" : {
        "sub_to" : "opt",
        "opt" : {
            "user_name" : "#USERNAME",
            "match_id" : "#MATCHID",
            "script" : {
                "send": "echo ${SOLUSION} | opt submit --match=${ID} --no-wait",
                "get": "opt list solutions --limit ${SENDLISTSIZE} --query \"_and: [{match_id: {_eq: ${ID}}}, {owner: {name: {_eq: ${USERNAME}}}}]\""
            }
        },
        "local":{
            "cmd" : "#The command for evaluating solutions using a tool other than `opt`."
        }
    },
    "status" : {
        "limit": 10
    },
    "history" : {
        "limit":3
    }
}
```

By changing the `limit` value of the `status` key, you can specify the number of cases to be saved in the csv file where the status of the sent solutions is stored.<br>

<img src="../images/status_img.png" width= 100%>

Similarly, modifying the value of the `limit` key under the `history` key allows you to retrieve the evaluation scores for the specified matchID when using the `history` option, limited to the specified number set by the `limit` value.

### Solution Submission and Evaluation Score Reception
project
|-- ECOW
`-- module_tutorial1.py

Create a `module_tutorial1.py` file with the directory structure above and write the code below.

```python
from ECOW.run import Run
import cma
import numpy as np

def objective(x):
    if isinstance(x, np.ndarray):
        x = x.tolist()

    res = Run(x)
    print(res)
    return res[0][str(x)]['objective']

es = cma.CMAEvolutionStrategy([0, 0], 0.5)
es.optimize(objective)

```

And then, please execute this file.
```shell
$ python3 module_tutorial1.py
```

If you want to terminate, please input `Ctrl + C`.

### Options
project
|-- ECOW
`-- module_tutorial2.py

Create a `module_tutorial2.py` file with the directory structure above and write the code below.

```python
from ECOW.run import Run

if __name__ =="__main__":
    Run([[2, 5],[9, 4]], no_wait=True)
```

And then, please execute this code. 
This code will run in the background.

### Displaying the status.
If you add `no_wait=True` as an argument in the Run function, you can view the progress of the execution by running the following code in the command-line tool.
```sh
 python3 module_tutorial2.py -s
```

### Displaying History
#### Display on the Command Line
Running the following code will ask you a MatchID in the command line. It will then display information about the submitted solutions, evaluation scores, and submission date/time for the MatchID.
```sh
    python3 module_tutorial2.py -hi 
```
#### Save to JSON File
Running the following code will save information about the submitted solutions, evaluation scores, and submission date/time for the specified MatchID to a JSON file with the given filename.
```sh
    python3 module_tutorial2.py -hi -o filename
```
