import asyncio
import logging
import socket
import unittest

from lsst.ts import mtaircompressor
from pymodbus.client.tcp import AsyncModbusTcpClient as ModbusClient


class MTAirCompressorModelTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.log = logging.getLogger()
        self.log.addHandler(logging.StreamHandler())
        self.log.setLevel(logging.INFO)

        self.simulator = mtaircompressor.simulator.create_server()
        self.simulator_task = asyncio.create_task(self.simulator.serve_forever())

        await self.simulator.serving
        sock = [
            s for s in self.simulator.transport.sockets if s.family == socket.AF_INET
        ][0]
        host, port = socket.getnameinfo(sock.getsockname(), 0)
        assert host is not None
        assert port is not None

        self.client = ModbusClient(host, port)
        assert self.client is not None
        await self.client.connect()

    async def asyncTearDown(self) -> None:
        assert self.client is not None
        assert self.simulator is not None
        await self.simulator.shutdown()
        self.simulator_task.cancel()

    async def test_get_status(self) -> None:
        model = mtaircompressor.MTAirCompressorModel(self.client, 1)
        assert await model.get_status() == [0x01, 0x00, 0x01]

    async def test_analog_data(self) -> None:
        model = mtaircompressor.MTAirCompressorModel(self.client, 1)
        analog_data = await model.get_analog_data()
        assert analog_data[0:10] == [2, 6, 7, 8, 9, 10, 11, 12, 13, 14]
