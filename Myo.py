from __future__ import print_function

import myo as libmyo; libmyo.init('E:\\Documents\\Fall 2015\\Fall 2015_\\CSE442\\crazyflie-clients-python\\raf')
import time
import sys
import sling as Crazy
import math

class Listener(libmyo.DeviceListener):
    """
    Listener implementation. Return False from any function to
    stop the Hub.
    """

    interval = 0.05  # Output only 0.05 seconds

    def __init__(self):
        super(Listener, self).__init__()
        self.orientation = None
        self.pose = libmyo.Pose.rest
        self.emg_enabled = False
        self.locked = False
        self.rssi = None
        self.emg = None
        self.acceleration = None
        self.gyroscope = None
        self.last_time = 0
        self.TakeOff = True
        available = "radio://0/80/2M"
        self.le = Crazy.Sling(available)
        #le._ramp_motors()
    def output(self):
        ctime = time.time()
        if (ctime - self.last_time) < self.interval:
            return
        self.last_time = ctime

        parts = []
        
        
        if self.orientation:
            for comp in self.orientation:
                parts.append(comp)
            print("Roll: " + str(parts[0]))
            print(" Pitch: " + str(parts[1]))
            print(" Yaw: " + str(parts[2]) + "\n")
            if( parts[0] < 0.0 and self.TakeOff ):
                self.le.thrust = math.floor(130000 * math.fabs(parts[0]))
            print(self.le.thrust)

        """
        print('\r a' + ''.join('[{0}]'.format(p) for p in parts), end='')
        """
        """
        #parts.append(str(self.pose).ljust(10))
        #parts.append('E' if self.emg_enabled else ' ')
        #parts.append('L' if self.locked else ' ')
        #parts.append(self.rssi or 'NORSSI')
        if self.emg:
            for comp in self.emg:
                parts.append(str(comp).ljust(5))
        """
        #parts.append(str(self.acceleration))
        #parts.append(str(self.gyroscope))
        
        sys.stdout.flush()

    def on_connect(self, myo, timestamp, firmware_version):
        myo.vibrate('short')
        myo.vibrate('short')
        myo.request_rssi()
        myo.request_battery_level()

    def on_rssi(self, myo, timestamp, rssi):
        self.rssi = rssi
        self.output()

    def on_pose(self, myo, timestamp, pose):
        if pose == libmyo.Pose.double_tap:
            myo.set_stream_emg(libmyo.StreamEmg.enabled)
            self.emg_enabled = True
        elif pose == libmyo.Pose.fist:
            myo.set_stream_emg(libmyo.StreamEmg.disabled)
            self.emg_enabled = False
            self.emg = None
            self.le.thrust = 40000
            self.TakeOff = True
        self.pose = pose
        self.output()

    def on_orientation_data(self, myo, timestamp, orientation):
        self.orientation = orientation
        self.output()

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        self.acceleration = acceleration
        self.output()

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        self.gyroscope = gyroscope
        self.output()

    def on_emg_data(self, myo, timestamp, emg):
        self.emg = emg
        self.output()

    def on_unlock(self, myo, timestamp):
        self.locked = False
        self.output()

    def on_lock(self, myo, timestamp):
        self.locked = True
        self.output()

    def on_event(self, kind, event):
        """
        Called before any of the event callbacks.
        """

    def on_event_finished(self, kind, event):
        """
        Called after the respective event callbacks have been
        invoked. This method is *always* triggered, even if one of
        the callbacks requested the stop of the Hub.
        """

    def on_pair(self, myo, timestamp, firmware_version):
        """
        Called when a Myo armband is paired.
        """

    def on_unpair(self, myo, timestamp):
        """
        Called when a Myo armband is unpaired.
        """

    def on_disconnect(self, myo, timestamp):
        print('Myo Disconnected')

    def on_arm_sync(self, myo, timestamp, arm, x_direction, rotation,
                    warmup_state):
        print('Myo Synced')

    def on_arm_unsync(self, myo, timestamp):
        print('Myo unsynced')

    def on_battery_level_received(self, myo, timestamp, level):
        """
        Called when the requested battery level received.
        """

    def on_warmup_completed(self, myo, timestamp, warmup_result):
        print('Myo warmup completed')


def main():
    print("Connecting to Myo ... Use CTRL^C to exit.")
    print("If nothing happens, make sure the Bluetooth adapter is plugged in,")
    print("Myo Connect is running and your Myo is put on.")
    hub = libmyo.Hub()
    hub.set_locking_policy(libmyo.LockingPolicy.none)
    listener = Listener()
    hub.run(1000, listener)

    # Listen to keyboard interrupts and stop the hub in that case.
    try:
        while hub.running:
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("\nQuitting ...")
        
    finally:
        listener.le.Run = False
        print("Shutting down hub...")
        
        hub.shutdown()


if __name__ == '__main__':
    main()
