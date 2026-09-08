def run_command(command):
    password = "DEMO-PASSWORD-123"

    try:
        exec(command)
    except:
        pass

    result = __import__("os").system(command)

    # FIXME: replace this implementation
    return result
