""" This is a pre and post check python script. Used for server upgrades."""
import pickle, re, platform, os, sys, subprocess
from fabric import Connection
from getpass import getpass

commandOutputs = {}
ce = None
passed = []
failed = []

c1 = None
c2 = None
c3 = None
c4 = None
c5 = None
c6 = None 
c7 = None
c8 = None
with open('file.dat', 'rb') as f:
    c1, c2, c3, c4, c5, c6, c7, c8 = pickle.load(f)

def sv_upgrade_preChecks():
    global passed, failed, c1, c2, c3, c4, c5, c6, c7, c8, ce, commandOutputs
    result = ce.run('show advanced-url /sysinfo/Version')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show advanced-url  /Diagnostics/Hardware/Info')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show interface all')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show system-resource-metrics')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show cpu')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show failover')
    commandOutputs.update({result.command: result.stdout})
    result = subprocess.run(['curl', '-I', '-k', '-L', '-x', 'PROXY_NAME', 'http://apple.com'], capture_output=True, text=True)
    commandOutputs.update({' '.join(result.args): result.stdout})
    result = subprocess.run(['curl', '-k', '-x', 'PROXY_NAME', 'http://www.eicar.org/download/eicar.com.txt'], capture_output=True, text=True)
    commandOutputs.update({' '.join(result.args): result.stdout})

    cmd1 = ' '.join(commandOutputs['show advanced-url /sysinfo/Version'].split('\n')[1].split()[1:])
    cmd2 = [commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n')[2].split(' ')[1]] + [i for i in commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n') if 'Interface' in i]
    cmd3 = commandOutputs['show interface all']
    cmd4 = {
        "Overall Health": commandOutputs['show system-resource-metrics'].split('\n')[5:][:1][0]
    }
    cmd5 = commandOutputs['show cpu']
    cmd6 = commandOutputs['show failover']
    cmd7 = [commandOutputs['$curl -I -k -L -x PROXY_NAME http://apple.com'].split('\n')[14]] + [commandOutputs['$curl -I -k -L -x PROXY_NAME http://apple.com'].split('\n')[16]]
    cmd8 = commandOutputs['$curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt'].split('\n')[2].strip()

    count = 0
    d = {}
    nums = [m.start() for m in re.finditer('Stat:', commandOutputs['show system-resource-metrics'])]

    for i in range(len(nums)):
        d.update({commandOutputs['show system-resource-metrics'][nums[count]:].split('\n')[0]: commandOutputs['show system-resource-metrics'][nums[count]:].split('\n')[1]})
        count += 1

    count = 0

    cmd4.update(d)




    f = []
    for i in commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n'):
        if 'Disk in slot' in i:
            f.append(i)

    count = 0
    for item in f:
        f[count] = item.replace(" ", "")
        count += 1

    a = []
    for item in f:
        a.append(item[item.find("status"):].replace("(", " ("))
        if 'status:present' in item:
            continue
        else:
            if ':empty' in item:
                continue
            else:
                cmd2error = f"""DISK IS OFFLINE: VALUE - {item[item.find("status"):].replace("(", " (")}"""


    a = list(filter(('y').__ne__, a))
    s = {}
    for i in range(len(a)):
        s.update({i: a[i-1]})

    cmd2.append(s.copy())

    print("\n\nRUNNING COMMAND - show advanced-url /sysinfo/Version")
    print(f"COMMAND OUTPUT: {cmd1}")

    # Example Scenario
    passed.append('show advanced-url /sysinfo/Version')
    print('-------------------------- TEST PASSED -------------------------------\n\n')



    print("RUNNING COMMAND - show advanced-url  /Diagnostics/Hardware/Info")
    print("COMMAND OUTPUT: ", end='')
    count = 1
    for s in cmd2:
        if s[0].startswith("status"):
            for l in s:
                print(f"\nDISK IN SLOT {str(count)}: {s[l]}")
                count+=1
        else:
            print(s)

    # Example Scenario
    if not 'cmd2error' in locals():
        passed.append('show advanced-url  /Diagnostics/Hardware/Info')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    else:
        print(f"\nERROR: {cmd2error}")
        failed.append('show advanced-url  /Diagnostics/Hardware/Info')
        print('-------------------------- TEST FAILED -------------------------------\n\n')


    print('RUNNING COMMAND - show system-resource-metrics')
    print('COMMAND OUTPUT: ', end='')
    print(cmd4['Overall Health'])

    if not 'WARNING' in cmd4['Overall Health']:
        passed.append('show system-resource-metrics')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    else:
        for s in cmd4:
            if 'Overall Health' in s:
                continue
            elif 'WARNING' in cmd4[s] or 'ERROR' in cmd4[s]:
                print(f'ERROR: {s} : {cmd4[s]}')
        failed.append('show system-resource-metrics')
        print('-------------------------- TEST FAILED -------------------------------\n\n')


    print('RUNNING COMMAND - show cpu')
    print(f'COMMAND OUTPUT: {cmd5[24:]}')
    if float(cmd5[24:]) > 70:
        print(f'ERROR: CPU IS DANGEROUSLY HIGH - {cmd5[24:]}')
        failed.append('show cpu')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('show cpu')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    
    print('RUNNING COMMAND - show failover')
    print(f'COMMAND OUTPUT: {cmd6}')
    passed.append('show failover')
    print('-------------------------- TEST PASSED -------------------------------\n\n')

    print('RUNNING COMMAND - curl -I -k -L -x PROXY_NAME http://apple.com')
    print('COMMAND OUTPUT: ', end='')
    error = None
    for i in cmd7:
        if not 'Connection established' in i:
            if not 'OK' in i:
                error = i
        print(i, end = ' ')

    if error != None:
        print('\n')
        print(f'ERROR: {error}')
        failed.append('curl -I -k -L -x PROXY_NAME http://apple.com')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('curl -I -k -L -x PROXY_NAME http://apple.com')
        print('\n', end='')
        print('-------------------------- TEST PASSED -------------------------------\n\n')

    print('RUNNING COMMAND - curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
    print(f'COMMAND OUTPUT: {cmd8}')

    if not cmd8 == '<title>Proxy Exception Page - Access Denied </title>':
        print(f'ERROR: EIGTH COMMAND DOES NOT EQUAL CORRECT VALUE. VALUE IS {cmd8}')
        failed.append('curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
        print('-------------------------- TEST PASSED -------------------------------\n\n')

    print(f'TEST VERDICT: {str(len(passed))} TESTS PASSED. {str(len(failed))} TESTS FAILED.')
    passed = []
    failed = []
    c1 = cmd1
    c2 = cmd2
    c3 = cmd3
    c4 = cmd4
    c5 = cmd5
    c6 = cmd6
    c7 = cmd7
    c8 = cmd8
    with open('file.dat', 'wb') as f:
        pickle.dump([cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8], f)

def svUpgradePostChecks():
    global passed, failed, ce
    result = ce.run('show advanced-url /sysinfo/Version')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show advanced-url  /Diagnostics/Hardware/Info')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show interface all')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show system-resource-metrics')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show cpu')
    commandOutputs.update({result.command: result.stdout})
    result = ce.run('show failover')
    commandOutputs.update({result.command: result.stdout})
    result = subprocess.run(['curl', '-I', '-k', '-L', '-x', 'PROXY_NAME', 'http://apple.com'], capture_output=True, text=True)
    commandOutputs.update({' '.join(result.args): result.stdout})
    result = subprocess.run(['curl', '-k', '-x', 'PROXY_NAME', 'http://www.eicar.org/download/eicar.com.txt'], capture_output=True, text=True)
    commandOutputs.update({' '.join(result.args): result.stdout})

    cmd1 = ' '.join(commandOutputs['show advanced-url /sysinfo/Version'].split('\n')[1].split()[1:])
    cmd2 = [commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n')[2].split(' ')[1]] + [i for i in commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n') if 'Interface' in i]
    cmd3 = commandOutputs['show interface all']
    cmd4 = {
        "Overall Health": commandOutputs['show system-resource-metrics'].split('\n')[5:][:1][0]
    }
    cmd5 = commandOutputs['show cpu']
    cmd6 = commandOutputs['show failover']
    cmd7 = [commandOutputs['$curl -I -k -L -x PROXY_NAME http://apple.com'].split('\n')[14]] + [commandOutputs['$curl -I -k -L -x PROXY_NAME http://apple.com'].split('\n')[16]]
    cmd8 = commandOutputs['$curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt'].split('\n')[2].strip()

    count = 0
    d = {}
    nums = [m.start() for m in re.finditer('Stat:', commandOutputs['show system-resource-metrics'])]

    for i in range(len(nums)):
        d.update({commandOutputs['show system-resource-metrics'][nums[count]:].split('\n')[0]: commandOutputs['show system-resource-metrics'][nums[count]:].split('\n')[1]})
        count += 1

    count = 0

    cmd4.update(d)




    f = []
    for i in commandOutputs['show advanced-url  /Diagnostics/Hardware/Info'].split('\n'):
        if 'Disk in slot' in i:
            f.append(i)

    count = 0
    for item in f:
        f[count] = item.replace(" ", "")
        count += 1

    a = []
    for item in f:
        a.append(item[item.find("status"):].replace("(", " ("))
        if 'status:present' in item:
            continue
        else:
            if ':empty' in item:
                continue
            else:
                cmd2error = f"""DISK IS OFFLINE: VALUE - {item[item.find("status"):].replace("(", " (")}"""


    a = list(filter(('y').__ne__, a))
    s = {}
    for i in range(len(a)):
        s.update({i: a[i-1]})

    cmd2.append(s.copy())

    print("\n\nRUNNING COMMAND - show advanced-url /sysinfo/Version")
    print(f"COMMAND OUTPUT: {cmd1}\n Pre Check Value {c1}\n Post Check Value {cmd1}")

    # Example Scenario
    
    
    if c1 == cmd1:
        passed.append('show advanced-url /sysinfo/Version')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    else:
        failed.append('show advanced-url /sysinfo/Version')
        print('ERROR: COMMANDS NOT SAME Pre Check Value {c1}\n Post Check Value {cmd1}')
        print('--------------------------- TEST FAILED -------------------------------\n\n')
        



    print("RUNNING COMMAND - show advanced-url  /Diagnostics/Hardware/Info")
    print("COMMAND OUTPUT: ", end='')
    count = 1
    for s in cmd2:
        if s[0].startswith("status"):
            for l in s:
                print(f"\nDISK IN SLOT {str(count)}: {s[l]}")
                count+=1
        else:
            print(s)

    # Example Scenario
    if not 'cmd2error' in locals() and c2 == cmd2:
        passed.append('show advanced-url  /Diagnostics/Hardware/Info')
        print(f'Pre Check Value: {c2}\n Post Check Value: {cmd2}')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    else:
        print(f"\nERROR: {cmd2error}\nPre Check Value: {c2}\n Post Check Value: {cmd2}")
        failed.append('show advanced-url  /Diagnostics/Hardware/Info')
        print('-------------------------- TEST FAILED -------------------------------\n\n')


    print('RUNNING COMMAND - show system-resource-metrics')
    print('COMMAND OUTPUT: ', end='')
    print(cmd4['Overall Health'])

    if not 'WARNING' in cmd4['Overall Health'] and c4 == cmd4:
        passed.append('show system-resource-metrics')
        print(f'Pre Check Value: {c4}\n Post Check Value: {cmd4}')
        print('-------------------------- TEST PASSED -------------------------------\n\n')

    else:
        for s in cmd4:
            if 'Overall Health' in s:
                continue
            elif 'WARNING' in cmd4[s] or 'ERROR' in cmd4[s]:
                print(f'ERROR: {s} : {cmd4[s]}')
                print(f'Pre Check Value: {c4[s]}\n Post Check Value: {cmd4[s]}')
        
        failed.append('show system-resource-metrics')
        print('-------------------------- TEST FAILED -------------------------------\n\n')


    print('RUNNING COMMAND - show cpu')
    print(f'COMMAND OUTPUT: {cmd5[24:]}')
    if float(cmd5[24:]) > 70:
        print(f'ERROR: CPU IS DANGEROUSLY HIGH - {cmd5[24:]}')
        failed.append('show cpu')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    elif not cmd5 == c5:
        print(f'Pre Check Value: {c5}\n Post Check Value: {cmd5}')
        failed.append('show cpu')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('show cpu')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    
    print('RUNNING COMMAND - show failover')
    print(f'COMMAND OUTPUT: {cmd6}')
    
    if cmd6 == c6:
        passed.append('show failover')
        print('-------------------------- TEST PASSED -------------------------------\n\n')
    else:
        failed.append('show failover')
        print(f'Pre Check Value: {c6}\n Post Check Value: {cmd6}')
        print('-------------------------- TEST FAILED -------------------------------\n\n')

    print('RUNNING COMMAND - curl -I -k -L -x PROXY_NAME http://apple.com')
    print('COMMAND OUTPUT: ', end='')
    error = None
    for i in cmd7:
        if not 'Connection established' in i:
            if not 'OK' in i:
                error = i
        print(i, end = ' ')

    if error != None:
        print('\n')
        print(f'ERROR: {error}')
        failed.append('curl -I -k -L -x PROXY_NAME http://apple.com')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    elif not cmd7 == c7:
        failed.append('curl -I -k -L -x PROXY_NAME http://apple.com')
        print(f'Pre Check Value: {c7}\n Post Check Value: {cmd7}')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('curl -I -k -L -x PROXY_NAME http://apple.com')
        print('\n', end='')
        print('-------------------------- TEST PASSED -------------------------------\n\n')

    print('RUNNING COMMAND - curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
    print(f'COMMAND OUTPUT: {cmd8}')

    if not cmd8 == '<title>Proxy Exception Page - Access Denied </title>':
        print(f'ERROR: EIGTH COMMAND DOES NOT EQUAL CORRECT VALUE. VALUE IS {cmd8}')
        failed.append('curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    elif not c8 == cmd8:
        failed.append('curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
        print('Pre Check Value: {c8}\n Post Check Value: {cmd8')
        print('-------------------------- TEST FAILED -------------------------------\n\n')
    else:
        passed.append('curl -k -x PROXY_NAME http://www.eicar.org/download/eicar.com.txt')
        print('-------------------------- TEST PASSED -------------------------------\n\n')

    print(f'TEST VERDICT: {str(len(passed))} TESTS PASSED. {str(len(failed))} TESTS FAILED.')
    passed = []
    failed = []
    

c = 'sv_upgrade'
def get_key(val):
    for key, value in disk.items():
        if val == value:
            return key
if c == 'sv_upgrade':
    while True:
        print("""-----------------------------------------------------------------------
                        Pre/Post Auto Checker
-----------------------------------------------------------------------

Welcome to the Pre/Post Auto Checker!
Here are the current command groups this script supports:

1) ProxySG Server Upgrade
2) Exit

Choose:""")
        try:
            choose = int(input())
        except:
            print('This is not a choice, please pick again.')
            continue
        if choose == 1:
            while True:
                print("""Are you doing Pre or Post Checks right now?
            
   1) Pre Checks
   2) Post Checks
   3) Exit
            
            """)
                try:
                    choose = int(input())
                except:
                    print('This is not a choice, please pick again.')
                    continue
                if choose == 1:
                    print('Please enter server hostname down below:')
                    hostname = input('>')
                    print('Please enter you password down below (Will not show):')
                    pwd = getpass("Your Password: ")
                    ce = Connection(hostname, connect_kwargs={"password":pwd})
                    sv_upgrade_preChecks()
                    if 'Linux' in platform.platform():
                        os.system('read -n1 -r -p "Press any key to continue . . ."')
                    elif 'Windows' in platform.platform():
                        os.system('pause')
                    

                elif choose == 2:
                    svUpgradePostChecks()
                    if 'Linux' in platform.platform():
                        os.system('read -n1 -r -p "Press any key to continue . . ."')
                    elif 'Windows' in platform.platform():
                        os.system('pause')
                elif choose == 3:
                    sys.exit()

        elif choose == 2:
            sys.exit()
    






