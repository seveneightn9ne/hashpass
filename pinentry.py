import subprocess

class PinEntryException(Exception):
    """Error while getting pin entry."""

def get_pin(description="", prompt="", errormsg=""):
    """Run pinentry to get a password from the user.

    Return value:
        User password as a string. Could be empty.
        None if the user pressed cancel.

    Raises:
        PinEntryException if something went wrong communicating with pinentry.
    """
    try:
        # Run pinentry, ignoring stderr.
        pinentry = subprocess.Popen(["pinentry"],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    except OSError:
        # Could not launch pinentry.
        raise PinEntryException("Could not launch pinentry")

    commands = ""
    commands += "SETDESC {}\n".format(description)
    commands += "SETPROMPT {}\n".format(prompt)
    commands += "SETERROR {}\n".format(errormsg)
    commands += "OPTION grab\n"
    commands += "GETPIN\n"
    commands += "BYE\n"

    output, _ = pinentry.communicate(input=commands)
    output_lines = output.split("\n")

    # Verify output.
    if len(output_lines) < 8:
        raise PinEntryException("Unexpected pinentry process output.")

    xline = output_lines[-4]
    yline = output_lines[-3]
    if xline[:2] == "D ":
        # User entered valid input.
        return xline[2:].replace("%25", "%")
    elif yline[:3] == "ERR":
        # User cancelled.
        return None
    elif xline == "OK":
        # User entered empty string.
        return ""
    else:
        raise PinEntryException("Unexpected pinentry process output.")
