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

    interval = 0.08  # Output only 0.05 seconds

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
        self.gotCenterYaw = False;
        self.centerYaw = 0;
        self.YawDeadZone = 0;
        self.centerRoll = 0;
        self.centerRollSet = False;
        #le._ramp_motors()
    def output(self):
        ctime = time.time()
        if (ctime - self.last_time) < self.interval:
            return
        self.last_time = ctime

        parts = []
        multiplier = 100000
        print(self.pose)
        if self.orientation:
            for comp in self.orientation:
                parts.append(comp)
            
            x = self.orientation.x;
            y = self.orientation.y;
            z = self.orientation.z;
            w = self.orientation.w;
            armband_yaw = math.atan2(2.0* (y*z  + w*x ), w*w - x*x - y*y + z*z )
            
            armband_pitch = math.asin(-2.0*(x*z - w*y))
            armband_roll = math.atan2(2.0*(x*y + w*z), w*w + x*x - y*y - z*z )

            if (not self.gotCenterYaw):
                self.gotCenterYaw = True;
                self.centerYaw = armband_yaw*multiplier;
                self.YawDeadZone = self.centerYaw + 10000;
                print(self.YawDeadZone)
                print(self.centerYaw)
                return  False;
            #print("Roll: " + str(roll))
            print(" roll: " + str(armband_roll))
            #print(" Yaw: " + str(yaw) + "\n")    


            
                #thrust = math.floor(130000 * math.fabs([0]))
                
            thrust = math.ceil(armband_pitch*multiplier)
            #crazy_roll = math.ceil(armband_yaw*multiplier)
            #print("thrust: "+ str(thrust))
            #print("roll: "+ str(crazy_roll))
            #print("DeadZone: " +str(self.YawDeadZone))
            #print("CenterYaw: "+str(self.centerYaw))
            if ( thrust < 0.0):
                thrust = 0
            if ( thrust < 55000):
                self.le.thrust = thrust
            print(self.le.thrust)

            
            

            

            if ( self.pose == libmyo.Pose.double_tap):
                self.centerRoll = armband_roll;
                self.centerRollSet = True;

            if ( self.centerRollSet ):
                if ( armband_roll > self.centerRoll + 0.15):
                    self.le.roll = ( armband_roll - ( self.centerRoll + 0.15) ) *40;
                elif ( armband_roll < self.centerRoll - 0.15):
                    self.le.roll = (armband_roll - (self.centerRoll - 0.15 )) * 40;
                else :
                    self.le.roll = 0 ;  









            """
            if ( self.pose == libmyo.Pose.fist):
                if(self.centerYaw == 0 ):
                    self.centerYaw = armband_yaw*multiplier;
                if ( crazy_roll > self.centerYaw + 10000):
                    self.le.roll = crazy_roll - (self.centerYaw + 10000)  ;
                if ( crazy_roll < self.centerYaw - 10000):
                    self.le.roll = crazy_roll - (self.centerYaw - 10000);

                self.le.roll = self.le.roll * 0.0003
                print(self.le.roll)
            else :
                self.le.roll = 0;
                self.centerYaw = 0;
            """

            """
            if ( self.pose == libmyo.Pose.wave_out):
                self.le.roll = 100
            elif( self.pose == libmyo.Pose.wave_in):
                self.le.roll = -100
            else:    
                self.le.roll = 0

            if(self.pose == libmyo.Pose.fist):
                self.le.pitch = 10;
            else:
                self.le.pitch = 0;
            """


            """
            if ( self.le.roll > 30000 or self.le.roll < -30000):
                self.le.roll = 0; 
            """
            print("Roll Center :"+str(self.centerRoll))
            print ( self.le.roll)



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
            if ( self.TakeOff):
                self.TakeOff = True
            else:
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
