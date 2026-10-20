
import time
import argparse

try:
    from raspythoncar.wr_lib2wd import WR2WD
except:
    pass

from raspythoncar.em_lib2wd import WR2WD_emulator, Field
from WDT import PerfTimer


###### EDIT HERE #################################
bottom0 = None
g_timer = PerfTimer()


def main_loop(wr):
    '''
    if( wr.ps.bottom() ):
        # right side is white
        wr.led.blue()
        wr.mc.front_tl()
    else:
        # left side is black
        wr.led.red()
        wr.mc.front_tr()
    '''

    # API reference: https://prod.kyohritsu.com/RASPYTHONCAR/functions/index.html

    global bottom0               # old bottom state
    global g_timer               # timer

    wr.mc.speed(40)

    if( bottom0 is None ):
        # initial setting for bottom0
        bottom0 = wr.ps.bottom()  # bottom sensor output ( True: white, False: black )
        g_timer.start()           # timer start

    bottom = wr.ps.bottom()       # bottom sensor output ( True: white, False: black )
    if( bottom ):
        # bottom is white
        wr.led.blue()             # turn led blue
        wr.mc.front_tl()          # moter front turn left
    else:
        # bottom is black
        wr.led.red()              # turn led red
        wr.mc.front_tr()          # moter front turn right

    if( bottom == bottom0 ):
        if( g_timer.get_time() > 2 ):
            # bottom is same state more than 2 [sec]
            wr.led.green()        # turn led green
            return False          # False -> end
    else:
        g_timer.restart()         # timer restart

    bottom0 = bottom              # copy old bottom state

    return True                   # True -> continue


def go_straight(wr, duration):
    wr.mc.speed(80)
    wr.led.yellow()
    wr.mc.front()
    time.sleep(duration)
    wr.mc.stop()
    return True


def stop(wr):
    wr.mc.stop()
    wr.led.off()

    return True


def turn_right(wr):
    wr.led.yellow()
    wr.mc.turn_right()
    time.sleep(1.4)
    wr.mc.stop()

    return True


def side_track(wr):
    threshold = 100

    wr.mc.speed(40)
    sensor_right = wr.ps.right()
    sensor_left = wr.ps.left()
    diff = sensor_right - sensor_left

    if( diff > 0 ):
        # bottom is white
        wr.led.blue()             # turn led blue
        wr.mc.front_tl()          # moter front turn left
    else:
        # bottom is black
        wr.led.red()              # turn led red
        wr.mc.front_tr()          # moter front turn right

    if( sensor_left < threshold or sensor_right < threshold):
        return False

    return True


def go_right(wr):
    wr.mc.speed(40)

    bottom = wr.ps.bottom()       # bottom sensor output ( True: white, False: black )
    if( bottom ):
        # bottom is white
        wr.led.blue()             # turn led blue
        wr.mc.front_tr()          # moter front turn left
    else:
        wr.mc.stop()
        return False              # moter front turn right

    return True


##################################################


def main(emulator, field):
    if( emulator ):
        wr = WR2WD_emulator(field=Field(field))
    else:
        wr = WR2WD()

    ret = True

    go_straight(wr, 2.0)
    turn_right(wr)

    while( ret ):
        try:
            ret = side_track(wr)
        except KeyboardInterrupt:
            print('\nbye')
            break

    go_straight(wr, 2.0)

    while( ret ):
        try:
            ret = go_right(wr)
        except KeyboardInterrupt:
            print('\nbye')
            break

    while( ret ):
        try:
            ret = main_loop(wr)
        except KeyboardInterrupt:
            print('\nbye')
            break

    go_straight(wr, 1.0)
    stop(wr)

    if( emulator ):
        wr.disp_state()


if( __name__ == '__main__' ):
    parser = argparse.ArgumentParser(description='Line trace')

    parser.add_argument('-e', '--emulator', action='store_true', default=False)
    parser.add_argument('-f', '--field', default='black_white')

    args = parser.parse_args()
    main(**vars(args))
