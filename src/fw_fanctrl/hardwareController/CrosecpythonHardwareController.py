from abc import ABC

from cros_ec_python import get_cros_ec
from cros_ec_python.commands.memmap import get_temps, get_battery_values
from cros_ec_python.commands.pwm import pwm_set_fan_duty
from cros_ec_python.commands.thermal import temp_sensor_get_info, thermal_auto_fan_ctrl

from fw_fanctrl.hardwareController.HardwareController import HardwareController


class CrosecpythonHardwareController(HardwareController, ABC):
    noBatterySensorMode = False
    nonBatterySensors = None
    ec = None

    def __init__(self, no_battery_sensor_mode=False):
        if no_battery_sensor_mode:
            self.noBatterySensorMode = True
            self.populate_non_battery_sensors()
        self.ec = get_cros_ec()

    def populate_non_battery_sensors(self):
        self.nonBatterySensors = []
        sensors = temp_sensor_get_info(self.ec)
        for index, (name, type) in enumerate(sensors):
            if not name.startswith("Battery"):
                self.nonBatterySensors.append(index)

    def get_temperature(self):
        temps_raw = get_temps(self.ec)
        if self.noBatterySensorMode:
            temps = [temps_raw[i] for i in self.nonBatterySensors if i < len(temps_raw)]
        else:
            temps = temps_raw
        # safety fallback to avoid damaging hardware
        if len(temps) == 0:
            return 50
        return max(temps)

    def set_speed(self, speed):
        pwm_set_fan_duty(self.ec, speed)

    def is_on_ac(self):
        battery = get_battery_values(self.ec)
        return battery["ac_present"]

    def pause(self):
        thermal_auto_fan_ctrl(self.ec)

    def resume(self):
        # Empty for ectool, as setting an arbitrary speed disables the automatic fan control
        pass
