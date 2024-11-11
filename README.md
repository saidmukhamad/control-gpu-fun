I'm using this to control speed of the fan that attached to my gpu (P40), and i do this by writing the temps into /sys/class/hwmon/hwmon2/pwm1

This can be done by

`echo <speed> | sudo tee /sys/class/hwmon/hwmon2/pwm1`


Also needs this if you found what you need to adjust, right now i do this manually

`sh
echo 1 | sudo tee /sys/class/hwmon/hwmon2/pwm1_mode
`
