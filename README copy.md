# ECOW
- [日本語 🇯🇵](./README_JP.md)

## Summary
ECOW (Evolutionary-computation Competition Opt-command Wrapper) is a Python wrapper with solution management functions for the "opt" command.

The "opt" command is designed for the submission and reference of solutions in the [Evolutionary Computation Competition](https://ec-comp.jpnsec.org) (organized by the Evolutionary Computation Society, Real-world Benchmark Problems Subcommittee).

By utilizing ECOW which internally execute the "opt" command, it makes possible to handle tasks such as managing usernames and problem numbers, suppressing the submission of duplicate solutions, and automating the saving of solution and result pairs in a file. This enables users to focus more on the competition.

## Demo
<img src="./docs/images/Tutorial.gif" width= 100%>

## Features
- Submission to opthub and Reference Evaluation Scores
    - Submission methods
        - Taking only the list of solutions as an argument
        - Taking the list of solutions and `no_wait=True` as arguments

    - Reference method
        - Obtaining evaluation scores from the server as the return value
        - Reading evaluation scores saved in a JSON file (If `no_wait=True` is given)

## Convenient Features
- Checking the status
    - Executing with the option `(-s, --status)`

- Displaying the history
    - Executing with the option `(-hi, --history)`

- Saving the history in JSON format
    - Executing with the options `(-hi, --history)` and `(-o filename, --output filename)`

## Usage
Visit the [document](https://csslab-aitech.github.io/Compe_module/) of ECOW.

## SetUp
- `Python` installation is required.
- Module installation is required.
    - `pip install filelock`

## License
- The MIT License (MIT)
- See [License](./LICENSE)

## Contact
- csslab _at_ aitech.ac.jp (replace _at_ with @)
