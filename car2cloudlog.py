from time import sleep, gmtime, strftime

from firebase_admin import credentials, db, initialize_app
from obd import OBD, commands
from gpiozero import LED

from pids import pidSens
from gearCalc import gearDisp

# Initiate debug file
timeStamp = (strftime("%Y-%m-%d %H:%M:%S", gmtime()))
fileName = timeStamp + '-debug.txt'
f = open(fileName,  "w")
f.write("Initiate debug log \n")

# Blink display led 5 times to show device has started
# led will blink at 2500ms intervals while data is uploaded
# to firebase
led = LED(17)
led.off()
for i in range(0, 4):
    led.on()
    sleep(.5)
    led.off()
    sleep(.5)

# Connect to Car ECU
ecuAttempt = 1
try:
    f.write('Attempting Connection to OBD \n')
    connection = OBD()
    f.write(str(connection) + '\n')
except:
    sleep(.25)
    f.write("Connection to ECU #:{} unsuccsesfull, retrying...\n".format(
        str(ecuAttempt)))
    ecuAttempt += 1
    break

# Fetch the service account key for firebase from JSON file contents & initilize
cred = credentials.Certificate('OBDII.json')

initialize_app(
    cred, {'databaseURL': 'https://obdiidata.firebaseio.com/'})

ref = db.reference('/')

# Send test data to Firebase to establish connection.
fbAttempt = 1
try:
    ref.set({
            ('devID01'): {
                'data': {
                    ('TIME_STAMP'): (timeStamp),
                }
            }})

except:
    f.write('Connection to FB #{} unsuccesful, retrying...\n'.format(str(fbAttempt)))
    fbAttempt += 1
    break

# Script will query ECU with all PIDs and store supported PIDs in the supportedPids dictionary
supportedPids = {}

for pid in pidSens():
    cmd = commands[pid]
    response = connection.query(cmd)
    if str(response) != 'None':
        f.write(k + '\n\t\t\tSupported\n')
        supportedPids[k] = v

    else:
        f.write(item + '\n\t\t\tNot supported \n')
    # 'GEAR' is a custom PID calculated by the gearDisp
    supportedPids['GEAR'] = 'N'


# loop will query ECU and upload data as a single dictionary to Firebase
while True:
    for k, v in supportedPids.items():
        if k != 'GEAR':
            cmd = commands[k]
            response = connection.query(cmd)
            if not response.is_null():
                supportedPids[k] = str(response.value.magnitude)

    # if the speed value is above 1, we will assume that the car is in a gear
    # and we will run the gearDisp function and calclate the gear
    speed = supportedPids['SPEED']
    if int(speed) > 1:
        supportedPids['GEAR'] = gearDisp(
            supportedPids['RPM'], pidSens['SPEED'])
    else:
        supportedPids['GEAR'] = 'N'

    # push our completed dictionary to firebase
    try:
        ref.set({
            ('devID01'): {
                'data':
                supportedPids
            })
        led.on()
    except:
        f.write("error uploading")
        break
    # set delay to query ECU every 2500ms
    sleep(.25)
    led.off()
