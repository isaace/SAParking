#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, stat, sys, getopt, commands, datetime
from parking_consts import debug_print
from parking_consts import sys_and_log
from parking_consts import set_park_file
from parking_consts import get_all_parking_data
from parking_consts import grep_all_parking
from parking_consts import set_as_jason
from parking_consts import free_path
from parking_consts import pending_path
from parking_consts import reserved_path
from parking_consts import taken_path
from parking_consts import blocking_path
from parking_consts import no_output
from parking_consts import ls
from parking_consts import rm
from parking_consts import touch
from parking_consts import echo
from parking_consts import no_free_parking

def update_park_file(leavat,user,slotID):
    print "inside update"
    if os.path.isfile(taken_path+str(slotID)):
        sys_and_log(rm + taken_path+str(slotID))
        print "inside if 6"
        f = open(taken_path +  str(slotID), 'w')
        print "after open"
        data = '"slotID":"' + str(slotID) + '", "status":"taken", "modified":' +  str(datetime.datetime.now()) + '", "user":"' + user + '","leaveat":"' + leavat + '"'
        #data = '"slotID":"' + str(slotID) + '", "status":"taken", "modified":' + '", "user":"' + user + '","leaveat":"' + leavat + '"' #+  str(datetime.datetime.now())
        print data
        f.write(data)
        f.close()
    else:
        print "ELSE???"

def usage():
    print("usage: static_funcs.py [option] ... ")
    print("-h help")
    print("-g get  | get free parking")
    print("-d  | data per parking spot")
    print("")

def get_free_parking():
    debug_print("get_free_parking called")
    free_list = os.listdir(free_path)
    if free_list != []:
        free_spot = free_list[0]
        debug_print("will return spot " + free_spot)
        sys_and_log(rm + free_path + free_spot)
        set_park_file(pending_path,free_spot)
        print set_as_jason(open(pending_path+free_spot,"r").read())
    else:
        debug_print("No free spot, lets look for blocking spots ")
        blocking_list = os.listdir(blocking_path)
        if blocking_list != []:
            free_spot = blocking_list[0]
            sys_and_log(rm + blocking_path + free_spot)
            set_park_file(pending_path,free_spot)
            print set_as_jason(open(pending_path+free_spot,"r").read())
        else:
            print no_free_parking

    #status, output = commands.getstatusoutput(ls + pending_path)
    return 0

def get_parking_content(park_id):
    path = None
    if os.path.isfile(pending_path+str(park_id)):
        path = pending_path+str(park_id)
    elif os.path.isfile(free_path+str(park_id)):
        path = free_path+str(park_id)
    elif os.path.isfile(taken_path+str(park_id)):
        path = taken_path+str(park_id)
    elif os.path.isfile(reserved_path+str(park_id)):
        path = reserved_path+str(park_id)
    elif os.path.isfile(blocking_path+str(park_id)):
        path = blocking_path+str(park_id)

    if path == None:
        print no_free_parking
    else:
        data = open(path,"r").read()
        print set_as_jason(data)
    sys.exit(0)


    debug_print(park_id + " status is: " + status)

def get_user_parking(user):
    grep_all_parking(user)


debug_print("external_rest_sudoers executed: " + '[%s]' % ' '.join(map(str, sys.argv)))
try:
    opts, args = getopt.getopt(sys.argv[1:], 'gs:d:u:l:i:ha', ['get', 'set=', 'data=', 'user=', "leave=", "slotID=", 'help', 'all'])
except getopt.GetoptError:
    usage()
    sys.exit(2)

user = None
leavat = None
slotID = None

for opt, arg in opts:
    if opt in ("-h", "--help"):
        usage()
        sys.exit(2)
    elif opt in ('-g', '--get'):
        ans = get_free_parking()
    elif opt in ('-s', '--set'):
        user = arg
    elif opt in ('-l', '--leave'):
        leavat = arg
    elif opt in ('-d', '--data'):
        get_parking_content(arg)
    elif opt in ('-u', '--user'):
        user = arg
    elif opt in ('-a', '--all'):
        get_all_parking_data()
    elif opt in ('-i', '--slotID'):
        slotID = arg
    else:
        usage()
        sys.exit(2)

if leavat != None and user != None and slotID != None:
    update_park_file(leavat,user,slotID)

sys.exit(0)

