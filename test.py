from tbot223_core.AppCore import AppCore

ac = AppCore(is_logging_enabled=False)

while(True):
    input_int = input("Enter an integer (0 to exit, 1 to restart): ")
    if input_int == '0':
        ac.exit_application(pause=True)
    elif input_int == '1':
        ac.restart_application(pause=True)