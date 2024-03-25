# Copyright © 2024 MiroZ.
# You are free to use/modify/distribute the code as you see fit
# as long as this copyright notice stays in place.
#
# Oh, yeah, use at your own risk!
#
# Verify the number of digits for offset and step size. If you 
# fatfinger incorrect values, there is a good chance you'll be
# buying a new build surface and/or nozzle. Program will output
# offsets it applies to the objects (those are also embedded in
# the output file), make sure those are ok before pushing 
# 'Print' button.

import sys
from functools import cmp_to_key

# number of objects should be odd and they need to have names
# n_xx and p_xx where xx are numbers (00, 01, 02, ...) and will be
# sorted in the following fashion:

# n_02 z offset -0.006
# n_01 z offset -0.003
# p_00 z offset 0.0
# p_01 z offset 0.003
# p_02 z offset 0.006

# OFFSET_START should be negative in such way that p_00 has zero offset. Or not.
# For 25 objects (12 positive, 12 negative and 1 zero) and 
# 0.003mm step, OFFSET_START should be -0.036

START_STR = "; printing object" #; printing object flowrate_m6 id:6 copy 0
END_STR = "; stop printing object"
OFFSET_STR = "SET_GCODE_OFFSET Z_ADJUST"

OFFSET_STEP = 0.005
OFFSET_START = (-OFFSET_STEP * 12) 

def find_objects(file):
    objects = []
    with open(file, "r") as f:
        for l in f:
            if START_STR in l:
                parts = l.split(" ")
                objName = parts[3]
                if not objName in objects:
                    objects.append(objName)
    return objects

def calc_offset(index):
    offset = round(OFFSET_START + index * OFFSET_STEP, 3)
    return offset

def get_offset_cmd(offset):
    return f"SET_GCODE_OFFSET Z_ADJUST={offset} MOVE=1"

def offset_gcode_object(inFile, outFile, objects):
    with open(inFile, "r") as fIn, open(outFile, "w", newline="\n") as fOut:

        for i, o in enumerate(objects):
            fOut.write(f"; {o} z offset {calc_offset(i)}\n")
        fOut.write("\n")

        for l in fIn:
            if START_STR in l:
                fOut.write(l)
                parts = l.split(" ")
                objName = parts[3]
                offset = calc_offset(objects.index(objName))

                if offset != 0:
                    fOut.write(f"; setting offset {offset} for object {objName}\n")
                    fOut.write(get_offset_cmd(offset)+"\n")
            
            elif END_STR in l:
                parts = l.split(" ")
                objName = parts[4]
                offset = -calc_offset(objects.index(objName))

                if offset != 0:
                    fOut.write(f"; resetting offset to 0 {offset} for object {objName}\n")
                    fOut.write(get_offset_cmd(offset)+"\n")

                fOut.write(l)

            else:
                fOut.write(l)

def compare(item1, item2):
    val = ord(item1[0])-ord(item2[0])
    
    if(val != 0):   # compare n to p
        return val
        
    # these are either all p or n
    # if n, sort descending, if p sort ascending
    v1 = int(item1[2:])
    v2 = int(item2[2:])
    if(item1[0] == 'p'):
        return v1-v2
    else:
        return v2-v1

def compare_dict(item1, item2):
    i1 = item1[0]
    i2 = item2[0]
    return compare(i1, i2)

def verify_file(file):
    print(f"Verifying file {file}")

    #objs = dict("m_01", mins=[1,2,3], maxs=[3,4,5])
    objs = {}

    with open(file, "r") as fIn:
        search_window = False
        occurence = 0
        for l in fIn:
            if START_STR in l:
                parts = l.split(" ")
                objName = parts[3]
                search_window = True
                occurence = 0
                if not objName in objs:
                    objs[objName] = { "mins" : [], "maxs" : [] }

            elif END_STR in l:
                parts = l.split(" ")
                objName = parts[4]
                search_window = False
                if not(occurence == 2 or occurence == 0):
                    print(f"there should be 2 set offsets per object (found {occurence} {objName})")

            elif OFFSET_STR in l:
                if search_window:
                    # SET_GCODE_OFFSET Z_ADJUST={offset} MOVE=1
                    parts = l.split(" ")
                    parts = parts[1].split("=")
                    z_offset = float(parts[1])
                    if occurence == 0:      # set
                        mins = objs[objName]["mins"]
                        if not z_offset in mins:
                            mins.append(z_offset)
                            objs[objName]["mins"] = mins

                    elif occurence == 1:    # reset
                        maxs = objs[objName]["maxs"]
                        if not z_offset in maxs:
                            maxs.append(z_offset)
                            objs[objName]["maxs"] = maxs
                    else:
                        print(f"too many set offsets ({occurence}) for object {objName}")

                    occurence += 1

                else:
                    print("offset cmd outside of the search window")

    objs = sorted(objs.items(), key=cmp_to_key(compare_dict))

    ok = True

    for o in objs:
        mins = o[1]["mins"]
        maxs = o[1]["maxs"]

        if not(len(mins) != 1 or len(mins) != 2):
            print(f"object {o[0]} has multiple set values: {mins}")
            ok = False

        if not(len(maxs) != 1 or len(maxs) != 2):
            print(f"object {o[0]} has multiple reset values: {maxs}")
            ok = False

        if(len(mins)==len(maxs)==1):
            if(mins[0]+maxs[0] != 0):
                print(f"Object {o[0]} does not reset it's offset to 0!")
                ok = False
        elif(len(mins)==len(maxs)==0):
            print(f"Note: Object {o[0]} doesn't specify offset.")
        else:
            print(f"Different number of sets vs resets")
            ok = False

    if not ok:
        print(f"failed")
    else:
        print("OK")

def main():
    global OFFSET_START, OFFSET_STEP

    if len(sys.argv) < 4:
        print("offset.py <infile> <offset start> <offset step> [<outfile>]")
        exit(0)

    IN_FILE = sys.argv[1]
    OUT_FILE = ""

    if len(sys.argv) > 2:
        OFFSET_START = float(sys.argv[2])

    if len(sys.argv) > 3:
        OFFSET_STEP = float(sys.argv[3])

    if len(sys.argv) > 4:
        OUT_FILE = sys.argv[4]

    gcode_objects = find_objects(IN_FILE)
    gcode_objects = sorted(gcode_objects, key=cmp_to_key(compare))

    if OUT_FILE == "":
        print("Found following objects:")
        for i, o in enumerate(gcode_objects):
            z_offset = calc_offset(i)
            print(f"{o} offset {z_offset}")

    if OUT_FILE != "":
        offset_gcode_object(IN_FILE, OUT_FILE, gcode_objects)

        for o, i in enumerate(gcode_objects):
            print(f"{i} z offset {round(OFFSET_START+o*OFFSET_STEP,3)}")

        print("")
        verify_file(OUT_FILE)


if __name__ == "__main__":
    main()