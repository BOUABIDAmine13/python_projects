import paramiko


def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    # policy accept the SSH key for the SSH server -> connecting to and make the connection
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=password)

    # after connection made: run command cmd that passed
    # if get output: print each line of the output
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('---Output---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass
    # user = getpass.getuser()
    user = input('Username: ')
    password = getpass.getpass()

    """ip = input('Enter server IP: ') or '192.168.100.42'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'"""
    ssh_command('127.0.0.1', 22, 'amine13', 'amine071202', 'id')