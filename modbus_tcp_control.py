#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp


def modbus_tcp_control(host,
                       port_number=502,
                       slave_unit=1,
                       timeout=10.0,
                       start_address=0,
                       write_coils=False,
                       write_holding_registers=False,
                       write_values=[],
                       read_count=1,
                       read_coils=False,
                       read_holding_registers=False,
                       read_discrete_inputs=False,
                       read_input_registers=False,
                       ):
    """
    @description:
    Modbus TCP client control.

    Coils and discrete inputs hold 1-bit only. zero value maps to bit 0,
    while the non-zero value map to bit 1. 

    input and holding registers have only 16-bit long. Therefore, if data
    have over 16-bit long, it is necessary to read or write successive,
    multiple values.

    <start_address>, <input_values> and <slave_unit> can be
    represented as binary (0b prefix), octal (0o prefix), decimal and
    hexadeciaml (0x prefix) value.

    <write_coils> and <write_holding_registers> cannot be used together.
    Otherwise an Exception may be generated.

    <read_discrete_inputs>, <read_input_registers, <read_coils> and
    <read_holding_registers> cannot be used together. Otherwise an Exception
    may be generated.

    If <read_count> <= 0, use number of values written.

    If <start_address> is not specified, no read value(s).

    If <start_address> is not specified, no written value(s).

    @param host@H: The hostname / ip address of a modbus server.
    @param port_number@P: The port number to connect <host>.
    @param slave_unit@U: The slave unit this request is targeting.
    @param timeout@T: Timeout in seconds for blocking operations.
    @param start_address@a: The start register address to write value(s) to or read value(s) from.
    @param write_coils@x: Write coils.
    @param write_holding_registers@y: Write holding registers.
    @param write_values@W: The value(s) to be written to <start_address>.
    @param read_count@n: The number of registers to read from <start_address>.
    @param read_coils@s: Read coils.
    @param read_holding_registers@t: Read holding registers.
    @param read_holding_registers@u: Read input registers.

    0: Return read values if <read_discrete_inputs>, <read_input_registers>, <read_coils> or <read_holding_registers> is/are set to True; Otherwise None.
    """



    #/* connect to server */
    master = modbus_tcp.TcpMaster(
        host=host,
        port=port_number,
        timeout_in_sec=timeout,
    )

    #/* set for server timeout */
    master.set_timeout(timeout)

    #/************************************************************************/

    #/* execute ( slave, function_code, start_address,
    # *           quantity_of_x = 0, output_value = 0, data_format="",
    # *           length = 1)
    # */

    #/* select for function code */
    if read_holding_registers:
        func_code = cst.READ_HOLDING_REGISTERS
        
    elif read_input_registers:
        func_code = cst.READ_INPUT_REGISTERS
        
    elif read_coils:
        func_code = cst.READ_COILS
        
    elif read_discrete_inputs: 
        cst.READ_DISCRETE_INPUTS
        
    elif read_holding_registers:
        func_code = cst.READ_INPUT_REGISTERS
        
    elif write_holding_registers:
        func_code = cst.WRITE_MULTIPLE_REGISTERS
        
    elif write_coils:
        func_code = cst.WRITE_MULTIPLE_COILS
        
    else:
        raise Exception("No action specified.")

    #/* select read write operation */
    write_op = True
    if func_code in (
            cst.READ_HOLDING_REGISTERS,
            cst.READ_INPUT_REGISTERS,
            cst.READ_COILS,
            cst.READ_INPUT_REGISTERS,
    ):
        write_op = False

    #/* read/writeinput_registers */
    read_values = None
    try:
        
        if write_op:
            master.execute(
                slave=slave_unit,
                function_code=func_code,
                starting_address=start_address,
                output_value=write_values,
            )
    
        else:
            read_values = master.execute(
                slave=slave_unit,
                function_code=func_code,
                starting_address=start_address,
                quantity_of_x=read_count,
            )
            
    except Exception as e:
        pass

    #/* Note: the return values are packed in a tuple */
    if not (read_values is None):
        read_values = list(read_values)

    return read_values  # CCCsumikko_func_end


if __name__ == '__main__':
    '''
    modbus_tcp_control(host='172.16.1.52',
                       port_number=503,
                       slave_unit=1,
                       start_address=9,
                       write_coils=True,
                       write_holding_registers=False,
                       write_values=[False],
                       )
    '''                       
    print(simple_argparse(modbus_tcp_control, sys.argv[1:]))

