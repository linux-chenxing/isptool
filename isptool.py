#!/usr/bin/env python3
import argparse
from periphery import I2C

chipids = {
    0xf0: "infinity2m - SSD20x",
    0xf5: "pioneer3 - SSD212",
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

REG_PM_UARTDISABLE = 0xe12  # 0x1c24
PM_UARTDISABLE_BIT = 1 << 11
REG_PM_CHIPID = 0x1ecc  # 0x3d98


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


def create_set_address_message_bytes(addr):
    return [0x10, (addr >> 24) & 0xff, (addr >> 16) & 0xff, (addr >> 8) & 0xff, addr & 0xff]


def set_address(addr):
    # txfr = [I2C.Message([0x10, 0x00, 0x00, 0x30, 0x00])]
    txfr = [I2C.Message(create_set_address_message_bytes(addr))]
    i2c.transfer(i2caddr, txfr)


def read_pm_byte(i2c, bank):
    set_channel(CHANNEL_PM)
    set_address(bank)
    msgs = [I2C.Message([0x0], read=True)]
    i2c.transfer(i2caddr, msgs)
    return msgs[0].data[0]


def read_pm_word(i2c, bank):
    set_channel(CHANNEL_PM)
    set_address(bank)
    msgs = [I2C.Message([0, 0], read=True)]
    i2c.transfer(i2caddr, msgs)
    return msgs[0].data[0] | msgs[0].data[1] << 8


def write_pm_word(i2c, bank, word):
    set_channel(CHANNEL_PM)
    data = create_set_address_message_bytes(bank)
    data.append(word & 0xff)
    data.append((word >> 8) & 0xff)
    msgs = [I2C.Message(data)]
    i2c.transfer(i2caddr, msgs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MStar/SigmaStar i2c ISP tool.')
    parser.add_argument('--i2cdev', type=str, required=True, help='Path to the i2cdev file')

    args = parser.parse_args()

    i2c = I2C(args.i2cdev)

    # The vendor tools seem to do a handshake then a disconnect
    # maybe to make sure everything is in sync. Not sure if
    # it's needed but whatever.
    serial_debug_handshake()
    disconnect()

    # Enable serial debug
    serial_debug_handshake()

    chipid = read_pm_byte(i2c, REG_PM_CHIPID)

    if chipid in chipids:
        print("Chip id: %s (%02x)" % (chipids[chipid], chipid))
    else:
        print("Unknown chip id: %02x" % chipid)

    # Disable the UART
    uartdisable = read_pm_word(i2c, REG_PM_UARTDISABLE)
    write_pm_word(i2c, REG_PM_UARTDISABLE, uartdisable & ~PM_UARTDISABLE_BIT)

    # Reenable UART
    write_pm_word(i2c, REG_PM_UARTDISABLE, uartdisable | PM_UARTDISABLE_BIT)

    # Disconnect
    disconnect()

    i2c.close()
