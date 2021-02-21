#/* name of this backup server
# * This will be shown on the email subject.
# */
BACKUP_SERVER_NAME = 'MEEPMEEP'  # <<<


#/* ip or hostname of a PLC
# */
PLC_HOST = '127.0.0.1'  # <<<


#/* Port number to a PLC (502)
# */
PLC_PORT_NUMBER = 502  # <<<


#/* Slave id for a PLC's Modbus protocal
# */
PLC_SLAVE_UNIT = 1  # <<<


#/* max allowance time limit to connect a PLC, in seconds
# */
PLC_TIMEOUT_SECONDS = 10


#/* (technician use only)
# * The start address (0-indexed) of the LW holding register
# * The end address will be set to PLC_RW_MIN - 1
# */
PLC_LW_MIN = 0


#/* (technician use only)
# * The start end address (0-indexed) of the RW holding register
# * The end address will be set to 65565
# */
PLC_RW_MIN = 9999


#/* (technician use only)
# * list of backup status register address locations
# * these are relative to PLC_RW_MIN
# */
PLC_RWADDR_BACKUP_STATUS = 0
PLC_RWADDR_SERVER_STATUS = 1


#/* (technician use only)
# * This values will be set to address PLC_RW_BACKUP_STATUS
# */
PLC_RWCODE_BACKUP_STATUS_OK = 0
PLC_RWCODE_BACKUP_STATUS_FAILED = 1
PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS = 2


#/* (technician use only)
# * This values will be set to address PLC_RWADDR_SERVER_STATUS
# */
PLC_RWCODE_SERVER_STATUS_OK = 0
PLC_RWCODE_SERVER_STATUS_FAILED = 1

