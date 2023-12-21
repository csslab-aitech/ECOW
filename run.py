from ECOW.comp_module.functions.main import Main

def Run(solutions = None, no_wait=False):
    """Function to run module executable file

    Parameters
    ----------
    value (list):
        the solution you want to send
    available (boolean):
        Whether to receive an evaluation value as a return value. True if received
    """
    p = Main()
    result = p.Run(solutions, no_wait)
    return result