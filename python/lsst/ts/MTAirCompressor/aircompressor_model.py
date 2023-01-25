# This file is part of ts_MTAirCompressor.
#
# Developed for the Vera Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["MTAirCompressorModel"]

import enum

import pymodbus.exceptions
import pymodbus.pdu
from pymodbus.client.base import ModbusBaseClient


class Register(enum.IntEnum):
    """Address of registers of interest.

    Please see Delcos XL documentation for details.
    https://confluence.lsstcorp.org/display/LTS/Datasheets (you need LSST
    login)
    """

    # telemetry block
    WATER_LEVEL = 0x1E

    TARGET_SPEED = 0x22
    MOTOR_CURRENT = 0x23
    HEATSINK_TEMP = 0x24
    DCLINK_VOLTAGE = 0x25
    MOTOR_SPEED_PERCENTAGE = 0x26
    MOTOR_SPEED_RPM = 0x27
    MOTOR_INPUT = 0x28
    COMPRESSOR_POWER_CONSUMATION = 0x29
    COMPRESSOR_VOLUME_PERCENTAGE = 0x2A
    COMPRESSOR_VOLUME = 0x2B
    GROUP_VOLUME = 0x2C
    STAGE_1_OUTPUT_PRESSURE = 0x2D
    LINE_PRESSURE = 0x2E
    STAGE_1_OUTPUT_TEMPERATURE = 0x2F

    RUNNING_HOURS = 0x39  # 64bit, 2 registers
    LOADED_HOURS = 0x3B  # 64 bit, 2 registers
    LOWEST_SERVICE_COUNTER = 0x3D
    RUN_ON_TIMER = 0x3E
    LOADED_HOURS_50_PERCENT = 0x3F  # 64 bit, 2 registers

    STATUS = 0x30  # flags - started, ..
    INHIBIT = 0x32  # inhibits - remote start, ..

    ERROR_E400 = 0x63  # 16 registers with error and warning flags

    SOFTWARE_VERSION = 0xC7  # 14 ASCII registers
    SERIAL_NUMER = 0xD5  # 9 ASCII registers

    REMOTE_CMD = 0x12B  # power on/off, if remote commanding is enabled
    RESET = 0x12D  # reset errors & warnings


class MTAirCompressorModel:
    """Model for compressor.

    Handles compressor communication. Throws ModbusException on errors.

    Parameters
    ----------
    host : `str`
        Connection to compresor controller.
    port : `int`
    unit : `int`
        Compressor unit (address on modbus).
    """

    def __init__(self, connection: ModbusBaseClient, unit: int = 1):
        self.connection = connection
        self.unit = unit

    async def set_register(self, address, value, error_status):
        """Set ModBus register value.

        Parameters
        ----------
        address : `int(0xffff)`
            Address of register to be set.
        value : `int(0xffff)`
            New register value (16-bit integer).

        Returns
        -------
        response : `class`
            PyModbus response to call.

        Raises
        ------
        ModbusException
            When register cannot be set.
        """
        result = await self.connection.write_registers(
            address, [value], slave=self.unit
        )
        if isinstance(result, pymodbus.pdu.ExceptionResponse):
            if result.function_code == 144:
                raise pymodbus.exceptions.ModbusException(
                    f"Cannot set register at address {address} to {value} "
                    f"({value:X}), most likely compressor isn't in remote mode."
                )
            raise pymodbus.exceptions.ModbusException(str(result))
        return result

    async def reset(self):
        """Reset compressor errors.

        Returns
        -------
        response : `class`
            PyModbus response to call to set reset register.

        Raises
        ------
        ModbusException
            When reset cannot be performed.
        """
        return await self.set_register(
            Register.RESET, 0xFF01, "Cannot reset compressor"
        )

    async def power_on(self):
        """Power on compressor.

        Returns
        -------
        response : `class`
            PyModbus response to call to power on compressor.

        Raises
        ------
        ModbusException
            When compressor cannot be powered on. That includes power not
            configured to operate remotely - original_code in return then
            equals 16.
        """
        return await self.set_register(
            Register.REMOTE_CMD, 0xFF01, "Cannot power on compressor"
        )

    async def power_off(self):
        """Power off compressor.

        Returns
        -------
        response : `class`
            PyModbus response to call to power off compressor.

        Raises
        ------
        ModbusException
            When compressor cannot be powered off. That includes power not
            configured to operate remotely - original_code in return then
            equals 16.
        """
        return await self.set_register(
            Register.REMOTE_CMD, 0xFF00, "Cannot power down compressor"
        )

    async def get_registers(self, address, count, error_status):
        """
        Returns registers.

        Parameters
        ----------
        address : `int`
            Register address.
        count : `int`
            Number of registers to read.
        error_status : `str`
            Error status to fill in ModbusException raised on error.

        Raises
        ------
        ModbusException
            When register(s) cannot be retrieved.
        """
        result = await self.connection.read_holding_registers(
            address, count, slave=self.unit
        )
        if isinstance(result, pymodbus.pdu.ExceptionResponse):
            raise pymodbus.exceptions.ModbusException(str(result))
        return result.registers

    async def get_status(self):
        """Read compressor status - 3 status registers starting from address
        0x30.

        Raises
        ------
        ModbusException
            When registers cannot be retrieved.
        """
        return await self.get_registers(Register.STATUS, 3, "Cannot read status")

    async def get_error_registers(self):
        """Read compressor errors - 16 registers starting from address 0x63.

        Those are E4xx and A6xx registers, all bit masked. Please see Delcos
        manual for details.

        Raises
        ------
        ModbusException
            When registers cannot be retrieved.
        """
        return await self.get_registers(
            Register.ERROR_E400, 16, "Cannot read error registers"
        )

    async def get_compressor_info(self):
        """Read compressor info - 23 registers starting from address 0x63.

        Includes software version and serial number.

        Raises
        ------
        ModbusException
            When registers cannot be retrieved.
        """
        return await self.get_registers(
            Register.SOFTWARE_VERSION, 23, "Cannot read compressor info"
        )

    async def get_analog_data(self):
        """Read compressor info - register 0x1E and 14 registers starting from
        address 0x22.

        Those form compressor telemetry - includes various measurements. See
        Register and Delcos manual for indices.

        Raises
        ------
        ModbusException
            When registers cannot be retrieved.
        """
        return await self.get_registers(
            Register.WATER_LEVEL, 1, "Cannot read water level"
        ) + await self.get_registers(
            Register.TARGET_SPEED, 14, "Cannot read analog data"
        )

    async def get_timers(self):
        """Read compressor timers - 8 registers starting from address 0x39.

        Those form compressor running hours etc.

        Raises
        ------
        ModbusException
            When registers cannot be retrieved.
        """
        return await self.get_registers(Register.RUNNING_HOURS, 8, "Cannot read timers")
