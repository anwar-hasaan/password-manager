import os
import sys
import ctypes

def run_as_admin():
    if sys.platform != 'win32':
        raise RuntimeError('This function can only be run on Windows.')
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        script = os.path.abspath(__file__)
        params = ' '.join([script] + sys.argv[1:])
        code = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
        sys.exit(0)


# Check if running on C drive
if os.path.splitdrive(os.getcwd())[0] == 'C:':
    # Check if running from Desktop or Downloads directory
    parent_folder = os.path.split(os.path.dirname(__file__))[-1]
    if parent_folder == 'Desktop' or parent_folder == 'Downloads':
        # print('Running on Desktop or Downloads directory')
        pass
    else:
        # print('Running on C drive')
        # Request admin privileges
        if sys.platform.startswith('win'):
            try:
                run_as_admin()
            except Exception as e:
                # print(e)
                pass
else:
    # print('Not running on C drive')
    pass

print('everythings look good')



parent = os.path.split(os.path.dirname(__file__))[-1]
print(parent)

input()