from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
import time


@cbpi.controller
class SimpleBoilLogic(KettleController):

    ramp_power = Property.Number("Ramp Up Power %", True, 100)
    boil_power = Property.Number("Boil Power %", True, 70)

    def stop(self):

        super(KettleController, self).stop()
        self.heater_off()

    def run(self):

        r_power = int(self.ramp_power)
        b_power = int(self.boil_power)


        while self.is_running():
            temp = self.get_temp()
            r_limit = self.get_target_temp()
            if temp < r_limit:
                self.heater_on(r_power)
                self.actor_power(r_power)
            if temp >= r_limit:
                self.heater_on(b_power)
                self.actor_power(b_power)
            self.sleep(5)

@cbpi.step
class BoilStep(StepBase):
    '''
    Just put the decorator @cbpi.step on top of a method
    '''
    # Properties
    temp = Property.Number("Ramp Temperature", configurable=True)
    kettle = StepProperty.Kettle("Kettle")
    timer = Property.Number("Timer in Minutes", configurable=True)

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        # set target tep
        self.set_target_temp(self.temp, self.kettle)

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        Custom Action which can be execute form the brewing dashboard.
        All method with decorator @cbpi.action("YOUR CUSTOM NAME") will be available in the user interface
        :return:
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.temp, self.kettle)

    def finish(self):
        self.set_target_temp(0, self.kettle)

    def execute(self):
        '''
        This method is execute in an interval
        :return:
        '''

        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= int(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)

        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            cbpi.notify("Boil Finished", "Your Boil Step Has Finished", timeout=None)
            self.next()
