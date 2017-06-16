import logging
import time

from modules import cbpi
from modules.core.controller import KettleController
from modules.core.props import Property

@cbpi.controller
class SimpleBoilLogic(KettleController):

    ramp_power = Property.Number("Ramp Up Power %", True, 100)
    boil_power = Property.Number("Boil Power %", True, 70)

    def run(self):

        r_power = int(self.ramp_power)
        r_limit = self.get_target_temp()
        b_power = int(self.boil_power)


        while self.is_running():
            temp = self.get_temp()
            if temp < r_limit:
                self.heater_on(r_power)
            if temp >= r_limit:
                self.heater_on(b_power)
            self.sleep(5)
            self.heater_off()
