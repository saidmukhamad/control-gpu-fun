#!/usr/bin/env python3

import os
import glob
import time
from typing import Dict, List, Optional

class GPUFanController:
    def __init__(self):
        self.hwmon_path = "/sys/class/hwmon"
        self.gpu_fan = None
        self.min_rpm_threshold = 2000  # Minimum RPM to identify GPU fan

    def read_file(self, path: str) -> Optional[str]:
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except (IOError, PermissionError):
            return None

    def write_file(self, path: str, value: str) -> bool:
        try:
            with open(path, 'w') as f:
                f.write(value)
            return True
        except (IOError, PermissionError) as e:
            print(f"Error writing to {path}: {e}")
            return False

    def get_fan_speed(self, speed_path: str) -> Optional[int]:
        speed = self.read_file(speed_path)
        return int(speed) if speed and speed.isdigit() else None

    def find_gpu_fan(self) -> Optional[Dict]:
        """Find GPU fan based on RPM threshold."""
        for hwmon in glob.glob(os.path.join(self.hwmon_path, "hwmon*")):
            for fan_path in glob.glob(os.path.join(hwmon, "fan*_input")):
                speed = self.get_fan_speed(fan_path)
                
                if speed and speed > self.min_rpm_threshold:
                    fan_num = int(''.join(filter(str.isdigit, os.path.basename(fan_path))))
                    pwm_path = os.path.join(hwmon, f"pwm{fan_num}")
                    temp_path = os.path.join(hwmon, "temp1_input")  # Usually the first temp sensor
                    
                    if os.path.exists(pwm_path):
                        print(f"Found GPU fan: Speed {speed} RPM")
                        return {
                            "fan_number": fan_num,
                            "pwm_path": pwm_path,
                            "speed_path": fan_path,
                            "temp_path": temp_path
                        }
        return None

    def get_temperature(self) -> Optional[float]:
        """Get GPU temperature in Celsius."""
        if not self.gpu_fan or not os.path.exists(self.gpu_fan["temp_path"]):
            return None
            
        temp = self.read_file(self.gpu_fan["temp_path"])
        return float(temp) / 1000 if temp and temp.isdigit() else None

    def calculate_fan_speed(self, temp: float) -> int:
        """Calculate fan speed based on temperature."""
        if temp < 40:
            return 0
        elif temp < 50:
            return 30
        elif temp < 60:
            return 50
        elif temp < 70:
            return 70
        elif temp < 80:
            return 85
        else:
            return 100

    def set_fan_speed(self, speed_percentage: int) -> bool:
        """Set fan speed as percentage (0-100)."""
        if not self.gpu_fan:
            return False
            
        speed = max(0, min(100, speed_percentage))
        pwm_value = int((speed / 100) * 255)
        
        # Set manual mode
        enable_path = f"{self.gpu_fan['pwm_path']}_enable"
        if os.path.exists(enable_path):
            self.write_file(enable_path, "1")
        
        return self.write_file(self.gpu_fan['pwm_path'], str(pwm_value))

    def run_temp_control(self):
        """Run continuous temperature-based control."""
        if not self.gpu_fan:
            print("No GPU fan found!")
            return

        print("Starting temperature-based fan control (Ctrl+C to stop)")
        try:
            while True:
                temp = self.get_temperature()
                if temp is not None:
                    speed_percent = self.calculate_fan_speed(temp)
                    current_rpm = self.get_fan_speed(self.gpu_fan["speed_path"])
                    
                    self.set_fan_speed(speed_percent)
                    print(f"\rTemp: {temp:.1f}°C | Fan: {speed_percent}% | RPM: {current_rpm}", 
                          end='', flush=True)
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopping fan control")
            # Set a safe default speed before exiting
            self.set_fan_speed(50)

def main():
    if os.geteuid() != 0:
        print("Error: Must run as root (sudo)")
        return

    controller = GPUFanController()
    controller.gpu_fan = controller.find_gpu_fan()
    
    if controller.gpu_fan:
        controller.run_temp_control()
    else:
        print("No GPU fan found (looking for fans > 2000 RPM)")

if __name__ == "__main__":
    main()
