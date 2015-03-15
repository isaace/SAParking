#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, stat, datetime
import RPi.GPIO as GPIO

from parking_consts import debug_print
from parking_consts import sys_and_log
from parking_consts import set_park_file
from parking_consts import set_as_jason
from parking_consts import mv
from parking_consts import rm
from parking_consts import touch
from parking_consts import echo
from parking_consts import free_path
from parking_consts import pending_path
from parking_consts import taken_path
from parking_consts import blocking_path
from parking_consts import no_output
from parking_consts import no_free_parking
#from parking_consts import update_park_file



# Which GPIO's are used [0]=BCM Port Number [1]=BCM Name [2]=Use [3]=Pin
# ----------------------------------------------------------------------
GPIO_ECHO = 17
GPIO_TRIG = 4
GPIO_ECHO = 22
GPIO_TRIG = 27
arrgpio = [(17,"GPIO0","Echo",11),(4,"GPIO7","Trig",7),(22,"GPIO1","Echo",11),(27,"GPI27","Trig",7)]

def file_age_in_seconds(file_path_name):
    return int(time.time() - os.stat(file_path_name)[stat.ST_MTIME])

def move_to_take(park_id):
    #sys_and_log(rm + free_path + str(park_id) + no_output)
    #sys_and_log(rm + pending_path + str(park_id) + no_output)
    #sys_and_log(rm + blocking_path + str(park_id) + no_output)
    if not os.path.isfile(taken_path+str(park_id)):
        set_park_file(taken_path,park_id)

def set_free(park_id):
    if park_id == 2:
        set_blocking(park_id)
        return
    #in case that the parkig spot was actually take, mark it as free. happend physicaly
    if os.path.isfile(taken_path+str(park_id)):
        #sys_and_log(rm + taken_path + str(park_id) + no_output)
        set_park_file(free_path,park_id)
    #handle the pending case
    elif os.path.isfile(pending_path+str(park_id)):
        print("file in sec is " + str(file_age_in_seconds(pending_path+str(park_id))) + ", id is " + str(park_id))
        if file_age_in_seconds(pending_path+str(park_id)) > max_pending_time:
            #sys_and_log(rm + pending_path + str(park_id) + no_output)
            set_park_file(free_path,park_id)


def set_blocking(park_id):
    #in case that the parkig spot was actually take, mark it as free. happend physicaly
    if os.path.isfile(taken_path+str(park_id)):
        #sys_and_log(rm + taken_path + str(park_id) + no_output)
        set_park_file(blocking_path,park_id)
    #handle the pending case
    elif os.path.isfile(pending_path+str(park_id)):
        print("file in sec is " + str(file_age_in_seconds(pending_path+str(park_id))) + ", id is " + str(park_id))
        if file_age_in_seconds(pending_path+str(park_id)) > max_pending_time:
            #sys_and_log(rm + pending_path + str(park_id) + no_output)
            set_park_file(blocking_path,park_id)

    
def distance(GPIO_ECHO,GPIO_TRIG):
    debug_print ("GPIO_TRIG = " + str(GPIO_TRIG) + ",GPIO_ECHO = " + str(GPIO_ECHO))
    # Set GPIO Channels
    # -----------------
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_TRIG, GPIO.OUT)
    GPIO.output(GPIO_TRIG, False)


    # A couple of variables
    # ---------------------
    EXIT = 0                        # Infinite loop
    decpulsetrigger = 0.0001        # Trigger duration
    inttimeout = 1000               # Number of loop iterations before timeout called


    # Wait for 2 seconds to allow the ultrasonics to settle (probably not needed)
    # ---------------------------------------------------------------------------
    #print "Waiting for 2 seconds....."
    #time.sleep(2)


    # Go
    # --
    debug_print("Running....")
    min_dist = 100

    # Never ending loop
    # -----------------
    while EXIT < 10:

        # Trigger high for 0.0001s then low
        GPIO.output(GPIO_TRIG, True)
        time.sleep(decpulsetrigger)
        GPIO.output(GPIO_TRIG, False)

        # Wait for echo to go high (or timeout)
        i_countdown = inttimeout

        while (GPIO.input(GPIO_ECHO) == 0 and i_countdown > 0):
            i_countdown -=  1

        # If echo is high than the i_countdown not zero
        if i_countdown > 0:

            # Start timer and init timeout countdown
            echostart = time.time()
            i_countdown = inttimeout

            # Wait for echo to go low (or timeout)
            while (GPIO.input(GPIO_ECHO) == 1 and i_countdown > 0):
                i_countdown -= 1

            # Stop timer
            echoend = time.time()


            # Echo duration
            echoduration = echoend - echostart

        # Display distance
        if i_countdown > 0:
            i_distance = (echoduration*1000000)/58
            debug_print("Distance = " + str(i_distance) + "cm")
            min_dist = min(min_dist,i_distance)
        else:
            debug_print("Distance - timeout")

            # Wait at least .01s before re trig (or in this case .1s)
            time.sleep(.1)

        EXIT +=1
        return min_dist
#S1
#distance(17,4)
#print "lets switch sensors"
#S2
#distance(22,27)

#Inint the arrays & the const's
traushold_accupide = 50
point = 0
arr_size = 8 #size of samples array, i.e. X last samples that we take in count
arr_range = 3 # number of sensors, each sensor requies it's own array
sleep_const = 0.5 #sleep period between each sampling
max_pending_time = 18 # time that a parking can be at pending state before marked as free
arr_arr = []
for i in xrange(arr_range):
    arr_arr.append([0 for i in xrange(arr_size)])

tmp = 0

print ("Hello easy parking")

while 1:
    #set the current slot pointer
    point = divmod((point + 1),arr_size)[1]
    debug_print("working on slot " + str(point))
    arr_arr[0][point] = distance(17,4)
    arr_arr[1][point] = distance(22,27)
    arr_arr[2][point] = distance(23,24)

    for i in xrange(arr_range):
        if sum(arr_arr[i])/arr_size > traushold_accupide:
            print"spot " + str(i) + " is free"
            set_free(i)
        else:
            print"spot " + str(i) + " is taken"
            move_to_take(i)

    debug_print("sleeping for " + str(sleep_const) +  " seconds",True)
    time.sleep(sleep_const)
    '''
    tmp += 1
    if tmp > 4:
        for i in xrange(arr_range):
            print "arr" + str(i) + " " + str(arr_arr[i])
        exit(0)
    '''

