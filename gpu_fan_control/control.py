import argparse
from nvitop import Device
import os
import sys

def temperature_to_fan_speed(temp_c, min_temp, max_temp):
    if temp_c <= min_temp:
        return 0
    elif temp_c >= max_temp:
        return 1000
    else:
        # Linear interpolation
        return int((temp_c - min_temp) * (1000 / (max_temp - min_temp)))

def set_fan_speed(fan_speed, pwm_path):
    pwm_enable_path = os.path.join(os.path.dirname(pwm_path), 'pwm1_enable')
    with open(pwm_enable_path, 'w') as f:
        f.write('1')  # Manual mode

    with open(pwm_path, 'w') as f:
        f.write(str(fan_speed))

def main():
    parser = argparse.ArgumentParser(description='GPU Fan Control Script')
    parser.add_argument('--min_temp', type=int, default=30, help='Minimum temperature')
    parser.add_argument('--max_temp', type=int, default=80, help='Maximum temperature')
    parser.add_argument('--pwm_path', type=str, default='/sys/class/hwmon/hwmon2/pwm1', help='Path to pwm1 file')
    args = parser.parse_args()

    devices = Device.all()
    for device in devices:
        temp_c = device.temperature()
        fan_speed = temperature_to_fan_speed(temp_c, args.min_temp, args.max_temp)
        print(f"Device {device.index}: Temperature = {temp_c}°C, Setting fan speed to {fan_speed}")
        set_fan_speed(fan_speed, args.pwm_path)

if __name__ == '__main__':
    main()
