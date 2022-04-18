import mariadb
import sys
import RPi.GPIO as gpio
import socket
import subprocess
import threading as Thread

global hatch_status, locked

def lock():
    global hatch_status, locked
    #Lock status boolan
    locked = 1

    # Get Cursor
    broken = False
    cur = conn.cursor()
    locked = 0
    while broken == False:
        swiped = False    
        id = input("Enter ID: ")
        

        #TODO: fix 0 length
        if (id[0] == ';'):
            id = id[1:10]
            swiped = True

        if swiped == True:
            query = "SELECT COUNT('id') FROM swipeid WHERE id=?"
        else:
            query = "SELECT COUNT('id') FROM numid WHERE id=?"

        rows = cur.execute(query,(id,))
        
        #lock status, hatch
        #1 is open
        #0 is locked

        for (res) in cur:
            if res[0] == 0:
                print("Access Denied")

            else: 
                print("Access Granted")
                if hatch_status == 0: #closed
                    if locked == 1: #unlocked
                        locked = 0
                    else:            #locked
                        locked = 1
                else:
                    locked = 1

        if locked == 1:
            gpio.output(26,gpio.HIGH)
            gpio.output(21,gpio.HIGH)
            gpio.output(20,gpio.HIGH)
        else:
            gpio.output(26,gpio.LOW)
            gpio.output(21,gpio.LOW)
            gpio.output(20,gpio.LOW)


def hatch():
    global hatch_status, locked
    cur_hatch_status = 0
    cur_lock_status = 0
    client, addr = sock.accept()
    print(addr)

    while True:
        hatch_status = gpio.input(18)
        if (cur_hatch_status != hatch_status) or (cur_lock_status != locked):
            cur_hatch_status = hatch_status
            cur_lock_status = locked
            packet = str([locked, hatch_status])
            print(packet)
            client.send(packet.encode())

# Connect to MariaDB Platform
gpio.cleanup()
try:
    conn = mariadb.connect(
        user="admin",
        password="raspberry",
        host="127.0.0.1",
        port=3306,
        database="auth"
    )
    
    gpio.setmode(gpio.BCM)
    
    gpio.setup(20,gpio.OUT)
    gpio.setup(21,gpio.OUT)
    gpio.setup(26,gpio.OUT)
    gpio.setup(18,gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(15,gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.output(26,gpio.LOW)
    gpio.output(21,gpio.LOW)
    gpio.output(20,gpio.LOW)

    result = subprocess.run(['hostname', '-I'], capture_output = True)
    byteip = result.stdout
    ip = byteip.decode()
    ip = ip[:13]
    print(ip)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip,1234))
    sock.listen()
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

T1 = Thread(target = lock)
T2 = Thread(target = hatch)
T2.setDaemon(True)

T1.start()
T2.start()