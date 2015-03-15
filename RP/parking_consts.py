#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, datetime, re
debug = False

mv = '/bin/mv -f '
ls = '/bin/ls -1 '
rm = '/bin/rm -f '
touch = '/usr/bin/touch '
echo = '/bin/echo '

root_path = '/var/www/parkings/'
free_path = root_path + 'free/'
pending_path = root_path + 'pending/'
taken_path = root_path + 'taken/'
blocking_path = root_path + 'blocking/'
reserved_path = root_path + 'reserved/'
paths = {free_path, pending_path, taken_path, blocking_path, reserved_path}
no_output = ' > /dev/null 2>&1'

no_free_parking = '{"slotID":"-1"}'



def debug_print(my_line,must_print = False):
    if debug or must_print:
        print my_line

def sys_and_log(cmd):
    debug_print(cmd)
    os.system(cmd)


def set_park_file(new_path,park_id):
    if new_path == free_path:
        status = "free"
    elif new_path == taken_path:
        status = "taken"
    elif new_path == pending_path:
        status = "pending"
    elif new_path == reserved_path:
        status = "reserved"
    elif new_path == blocking_path:
        status = "blocking"

    for path in paths:
        if path == new_path:
            f = open(new_path +  str(park_id), 'w')
            f.write("\"slotID\":\"" + str(park_id) + "\",\"status\":\"" + status + "\",\"modified\":\"" +  str(datetime.datetime.now()) +"\"")
            f.close()
        else:
            sys_and_log(rm + path + str(park_id) + no_output)

def set_as_jason(data):
    return "{ " + str(data) + " }"

def grep_all_parking(pattern):
    found = False
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            data = open(root+'/'+filename,"r").read()
            if re.search(pattern, data):
                print set_as_jason(data)
                found = True
    if not found:
        print no_free_parking

def get_all_parking_data():
    data = '{ "slots" '
    deliminator = ':'
    for root, dirs, files in os.walk(root_path):
        for filename in files:
            data += deliminator +  "[ " + open(root+'/'+filename,"r").read() + " ] "
            deliminator = ', '
    data += ' }'
    print data

def update_park_file2(leavat,user,slotID):
    print "inside update"
    if os.path.isfile(taken_path+str(slotID)):
        print "inside if"
        f = open(taken_path +  str(slotID), 'w')
        print "after if"
        if not f:
            print "WTF"
        else:
            print str(f)
        data = '"slotID":"' + str(slotID) + '", "status":"taken", "modified":' +  str(datetime.datetime.now()) + '", "user":"' + user + '","leaveat":"' + leavat + '"'
        print data
        f.write(data)
        f.close()
    else:
        print "ELSE???"
    print "bye"

