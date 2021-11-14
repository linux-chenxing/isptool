#!/usr/bin/env python3
from periphery import I2C

chipids = {
    0xf0: "infinity2m - SSD20x"
}

i2caddr = 0x59

CHANNEL_PM = 3
CHANNEL_NONPM = 4

CMD_BYTE_CHANNEL_BIT0_CLEAR = 0x80
CMD_BYTE_CHANNEL_BIT0_SET = 0x81
CMD_BYTE_CHANNEL_BIT1_CLEAR = 0x82
CMD_BYTE_CHANNEL_BIT1_SET = 0x83
CMD_BYTE_CHANNEL_BIT2_CLEAR = 0x84
CMD_BYTE_CHANNEL_BIT2_SET = 0x85

REG_PM_CHIPID = 0x1ecc  # 0x3D98


def serial_debug_handshake():
    txfr = [I2C.Message([0x53, 0x45, 0x52, 0x44, 0x42])]
    i2c.transfer(i2caddr, txfr)


def disconnect():
    txfr = [I2C.Message([0x34]), I2C.Message([0x45])]
    i2c.transfer(i2caddr, txfr)


def set_channel(channel):
    txfr = []

    if channel & 0x1:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT0_SET]))
    else:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT0_CLEAR]))

    if channel & 0x2:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT1_SET]))
    else:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT1_CLEAR]))

    if channel & 0x4:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT2_SET]))
    else:
        txfr.append(I2C.Message([CMD_BYTE_CHANNEL_BIT2_CLEAR]))

    txfr.append(I2C.Message([0x53]))
    txfr.append(I2C.Message([0x7f]))
    txfr.append(I2C.Message([0x35]))
    txfr.append(I2C.Message([0x71]))

    i2c.transfer(i2caddr, txfr)


def set_address(addr):
    # txfr = [I2C.Message([0x10, 0x00, 0x00, 0x30, 0x00])]
    txfr = [I2C.Message([0x10, (addr >> 24) & 0xff, (addr >> 16) & 0xff, (addr >> 8) & 0xff, (addr >> 26) & 0xff])]
    i2c.transfer(i2caddr, txfr)


def read_pm_byte(i2c, bank):
    set_channel(CHANNEL_PM)
    set_address(bank)
    msgs = [I2C.Message([0x0], read=True)]
    i2c.transfer(i2caddr, msgs)
    return msgs[0].data[0]


if __name__ == '__main__':
    i2c = I2C("/dev/i2c-4")

    # The vendor tools seem to do a handshake then a disconnect
    # maybe to make sure everything is in sync. Not sure if
    # it's needed but whatever.
    serial_debug_handshake()
    disconnect()

    # Enable serial debug
    serial_debug_handshake()

    chipid = read_pm_byte(i2c, REG_PM_CHIPID)
    print("Chip id: %s (%02x)" % (chipids[chipid], chipid))

    i2c.close()
