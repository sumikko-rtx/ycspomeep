#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from modbus_tcp_control import modbus_tcp_control
from constants import PLC_HOST, PLC_PORT_NUMBER, PLC_SLAVE_UNIT,\
    PLC_TIMEOUT_SECONDS
from constants import PLC_LW_MIN, PLC_RW_MIN, PLC_LB_MIN, PLC_RB_MIN


def plc_report(write_lb_values=list(),
               write_rb_values=list(),
               write_lw_values=list(),
               write_rw_values=list(),
               sep=',',
               ):

    #/* write_lw_values and write_rw_values must have the following pattern
    # *
    # * [address_1, value_1, address_2, value_2, ..., address_n, value_n]
    # */

    #/* split write_lb_values argument, if any */
    if isinstance(write_lb_values, str):
        write_lb_values = write_lb_values.split(sep)
    write_lb_values = list(write_lb_values)

    #/* split write_rb_values argument, if any */
    if isinstance(write_rb_values, str):
        write_rb_values = write_rb_values.split(sep)
    write_rb_values = list(write_rb_values)

    #/* split write_lw_values argument, if any */
    if isinstance(write_lw_values, str):
        write_lw_values = write_lw_values.split(sep)
    write_lw_values = list(write_lw_values)

    #/* split write_rw_values argument, if any */
    if isinstance(write_rw_values, str):
        write_rw_values = write_rw_values.split(sep)
    write_rw_values = list(write_rw_values)

    #/*---------------------------------------------------------------------*/

    #/* write lb values */
    j = 0
    k = int(len(write_lb_values) / 2)
    while j < k:

        j1 = j * 2
        j2 = j * 2 + 1

        address = write_lb_values[j1]
        value = write_lb_values[j2]

        modbus_tcp_control(
            host=PLC_HOST,
            port_number=PLC_PORT_NUMBER,
            slave_unit=PLC_SLAVE_UNIT,
            timeout=PLC_TIMEOUT_SECONDS,
            start_address=PLC_LB_MIN + address,
            write_coils=True,
            write_values=[value],
        )

        j = j + 1


    #/*---------------------------------------------------------------------*/

    #/* write rb values */
    j = 0
    k = int(len(write_rb_values) / 2)
    while j < k:

        j1 = j * 2
        j2 = j * 2 + 1

        address = write_rb_values[j1]
        value = write_rb_values[j2]

        modbus_tcp_control(
            host=PLC_HOST,
            port_number=PLC_PORT_NUMBER,
            slave_unit=PLC_SLAVE_UNIT,
            timeout=PLC_TIMEOUT_SECONDS,
            start_address=PLC_RB_MIN + address,
            write_coils=True,
            write_values=[value],
        )

        j = j + 1


    #/*---------------------------------------------------------------------*/

    #/* write lw values */
    j = 0
    k = int(len(write_lw_values) / 2)
    while j < k:

        j1 = j * 2
        j2 = j * 2 + 1

        address = write_lw_values[j1]
        value = write_lw_values[j2]

        modbus_tcp_control(
            host=PLC_HOST,
            port_number=PLC_PORT_NUMBER,
            slave_unit=PLC_SLAVE_UNIT,
            timeout=PLC_TIMEOUT_SECONDS,
            start_address=PLC_LW_MIN + address,
            write_holding_registers=True,
            write_values=[value],
        )

        j = j + 1

    #/*---------------------------------------------------------------------*/

    #/* write rw values */
    j = 0
    k = int(len(write_rw_values) / 2)
    while j < k:

        j1 = j * 2
        j2 = j * 2 + 1

        address = write_rw_values[j1]
        value = write_rw_values[j2]

        modbus_tcp_control(
            host=PLC_HOST,
            port_number=PLC_PORT_NUMBER,
            slave_unit=PLC_SLAVE_UNIT,
            timeout=PLC_TIMEOUT_SECONDS,
            start_address=PLC_RW_MIN + address,
            write_holding_registers=True,
            write_values=[value],
        )

        j = j + 1


if __name__ == '__main__':
    print(simple_argparse(plc_report, sys.argv[1:]))
