lines_9250 = {}
lines_9300 = {}


with open("shakeup_debug_9250.txt", "r") as shk_9250:
    for line in shk_9250:
        vals = line.strip().split(": ")
        lines_9250[vals[0]] = [float(vals[1].split(", ")[5]), float(vals[1].split(", ")[7])]


with open("shakeup_debug_9300.txt", "r") as shk_9300:
    for line in shk_9300:
        vals = line.strip().split(": ")
        lines_9300[vals[0]] = [float(vals[1].split(", ")[5]), float(vals[1].split(", ")[7])]



for key in lines_9250:
    if key in lines_9300:
        if lines_9300[key][0] - lines_9250[key][0] < 0.0 or lines_9300[key][1] - lines_9250[key][1] < 0.0:
            print(key + ": " + str(lines_9300[key][0] - lines_9250[key][0]) + ", " + str(lines_9300[key][1] - lines_9250[key][1]))
        if lines_9300[key][0] == 0.0 and lines_9250[key][0] != 0.0:
            print(key + ": " + str(lines_9300[key][0] - lines_9250[key][0]) + ", " + str(lines_9300[key][1] - lines_9250[key][1]))
            
