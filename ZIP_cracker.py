import argparse
import textwrap
import zipfile
import threading
import sys
import os

def type_check(file_name, file_type):
    return file_name.lower().endswith(file_type)

class ZIP_cracker():
    def __init__(self, args):
        self.args =args

    def open_zip_file(self, password):
        try:
            with zipfile.ZipFile(self.args.file, 'r') as zip_file:
                test = zip_file.read(zip_file.namelist()[0],pwd=password.encode("utf-8"))
        except RuntimeError or PermissionError:
            return False
        if test:
            return True
        
    def check_password(self, passwords):
        success = False
        for password in passwords:
            if self.open_zip_file(password=password):
                print(f'the password is {password}')
                success = True
                if self.args.extract:
                    with zipfile.ZipFile(self.args.file, 'r') as zip_file:
                        zip_file.extractall(pwd=password.encode("utf-8")) 
                break
        if not success:
            print('cannot find the password in words list :-(')
    
    def passwords_list(self):
        with open(self.args.wordsList, 'r', encoding='latin-1') as file :
            passwords_list = [password.strip() for password in file.readlines()]
        chunks_passwords = [passwords_list[i:i+self.args.nbThread] for i in range(0, len(passwords_list), self.args.nbThread)]
        return chunks_passwords
    
    def run(self):
        threads= []
        chunks_passwords = self.passwords_list()
        for passwords in chunks_passwords:
            thread = threading.Thread(target=self.check_password, args=(passwords,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def list(self):
        with zipfile.ZipFile(self.args.file, 'r') as zip_file:
            print(f'total: {len(zip_file.namelist())}')
            for file in zip_file.namelist():
                print(f'{file}\t{os.path.getsize(file)} Kb')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='ZIP_cracker',
        description='ZIP file cracker: using words list',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example
    ZIP_cracker.py -f zip_file.zip -wl worlds_list.txt
    ZIP_cracker.py -f zip_file.zip -wl worlds_list.txt -nt 4'''))

    parser.add_argument('-f', '--file', required=True, help='ZIP file name',)
    parser.add_argument('-wl','--wordsList', help='word list using to cracke the zip file')
    parser.add_argument('-nt','--nbThread',type=int, default=4, help='number of threads using in cracking')
    parser.add_argument('-e','--extract',action='store_true', help='extract option')
    parser.add_argument('-l', '--list',action='store_true', help='list all files: no cracke')

    args = parser.parse_args()
    if type_check(args.file, '.zip'):
        zip_cracker = ZIP_cracker(args=args)
        if args.list:
            zip_cracker.list()
        elif type_check(args.wordsList, '.txt'):
            zip_cracker.run()
    else:
        print("error: file extensions of file: .zip and words list: .txt", file=sys.stderr)