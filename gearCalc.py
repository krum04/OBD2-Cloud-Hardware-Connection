# define function to calculate transmission gear
def gearDisp(rpm, speed):
    curGear = ''
    gearRatio = int(float(rpm)/float(speed))
    if 105 <= gearRatio <= 120:
        curGear = '1'
    elif 65 <= gearRatio <= 75:
        curGear = '2'
    elif 45 <= gearRatio <= 55:
        curGear = '3'
    elif 35 <= gearRatio <= 40:
        curGear = '4'
    elif 28 <= gearRatio <= 31:
        curGear = '5'
    elif 22 <= gearRatio <= 26:
        curGear = '6'
    else:
        curGear = 'N'
    return curGear
