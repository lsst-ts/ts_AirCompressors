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

__all__ = ["status_bit_to_bools"]


def status_bit_to_bools(fields: list[str | None], value: int) -> dict[str, int]:
    """Helper function. Converts value bits into boolean fields.

    Parameters
    ----------
    fields : `list [str]`
        Name of fields to extract. Corresponds to bits in value, with lowest
        (0x0001) first. Can be None to specify this bit doesn't have any
        meaning.
    value : `int`
        Bit-masked value. Bits corresponds to named values in fields.

    Returns
    -------
    bits : `dict [ str, bool ]`
        Map where keys are values passed in fields and values are booleans
        corresponding to whenever that bit is set.
    """
    ret = {}
    for field in fields:
        if field is not None:
            ret[field] = value & 0x0001
        value >>= 1
    return ret
