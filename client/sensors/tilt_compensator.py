import math


def correct(imu):
    ACCx, ACCy, ACCz, GYRx, GYRy, GYRz = imu.read_accelerometer_gyro_data()
    MAGx, MAGy, MAGz = imu.read_and_calibrate_magnetometer_data()

    MAGx -= (imu.mag_min[0] + imu.mag_max[0]) / 2
    MAGy -= (imu.mag_min[1] + imu.mag_max[1]) / 2
    MAGz -= (imu.mag_min[2] + imu.mag_max[2]) / 2

    AccXangle = math.degrees(math.atan2(ACCy, ACCz))
    AccYangle = math.degrees((math.atan2(ACCz, ACCx) + math.pi))

    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0

    heading = math.degrees(math.atan2(MAGy, MAGx))

    if heading < 0:
        heading += 360

    value = ACCx ** 2 + ACCy ** 2 + ACCz ** 2
    accXnorm = ACCx / math.sqrt(value)
    accYnorm = ACCy / math.sqrt(value)

    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm / math.cos(pitch))

    magXcomp = MAGx * math.cos(pitch) + MAGz * math.sin(pitch)
    magYcomp = MAGx * math.sin(roll) * math.sin(pitch) + MAGy * math.cos(roll) + MAGz * math.sin(roll) * math.cos(pitch)

    tilt_compensated_heading = math.degrees(math.atan2(magYcomp, magXcomp))

    if tilt_compensated_heading < 0:
        tilt_compensated_heading += 360

    return tilt_compensated_heading, AccXangle, AccYangle
