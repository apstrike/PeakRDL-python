"""
peakrdl-python is a tool to generate Python Register Access Layer (RAL) from SystemRDL
Copyright (C) 2021 - 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This module is intended to distributed as part of automatically generated code by the
peakrdl-python tool. It provides a set of base classes used by the autogenerated code
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Union
from array import array as Array
import asyncio

from .register import Register, MemoryRegister
from .memory import Memory

from ..lib.utility_functions import get_array_typecode

@dataclass
class MemoryEntry:
    """
    Class for an entry in the list of memories in the simulator
    """
    start_address: int
    end_address: int
    memory: Memory

    def memory_offset(self, address: int) -> int:
        """
        Convert an absolute address to word offset within a memory

        Args:
            address: byte address

        Returns: memory word offset

        """
        return self.memory.byte_offset_to_word_offset(address - self.start_address)


    def address_in_memory(self, address: int) -> bool:
        """
        Determine if an address is within a memory or not

        Args:
            address: byte address

        Returns:
            if address is within the range of the memory

        """
        return self.start_address <= address <= self.end_address


class BaseSimulator(ABC):
    """
    Base class of a simple simulate that can be used to test and debug peakrdl-python generated
    register access layer (RAL)
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, address: int):
        self._registers: dict[int, Union[MemoryRegister, Register]] = {}
        self._memories: list[MemoryEntry] = []

        # it is important to build the memories first as some registers may be within memories
        self._build_memories()
        self._build_registers()
        self.address = address

    @abstractmethod
    def _build_registers(self) -> None:
        """
        populate the register structure, this method is intended to written by the generated code
        based on then design
        """

    @abstractmethod
    def _build_memories(self) -> None:
        """
        populate the memory structure, this method is intended to written by the generated code
        based on then design
        """

    def memory_for_address(self, address: int) -> Optional[MemoryEntry]:
        """
        Find a memory entry for a given address

        Args:
            address: byte address

        Returns:
            None or matching memory entry

        """

        memory_subset = list(filter(lambda x : x.address_in_memory(address=address),
                                    self._memories))

        if len(memory_subset) > 1:
            raise RuntimeError(f'multiple memory matches on address 0x{address:X}({address:d})')

        if len(memory_subset) == 1:
            return memory_subset[0]

        return None

    def _read(self, addr: int,
             width: int, # pylint: disable=unused-argument
             accesswidth: int) -> int: # pylint: disable=unused-argument
        """
        function to simulate a device read, this needs to match the protocol for the callbacks
        """

        # see if the address is a register first this ensures that registers in memories are
        # accessed directly
        if addr in self._registers:
            return self._registers[addr].read()

        potential_memory = self.memory_for_address(address=addr)
        if potential_memory is not None:
            return potential_memory.memory.read(offset=potential_memory.memory_offset(addr))

        # catch all for other addresses
        return 0

    def _write(self, addr: int,
               width: int,  # pylint: disable=unused-argument
               accesswidth: int,  # pylint: disable=unused-argument
               data: int) -> None:
        """
        function to simulate a device write, this needs to match the protocol for the callbacks
        """
        # see if the address is a register first this ensures that registers in memories are
        # accessed directly
        if addr in self._registers:
            self._registers[addr].write(data)
        else:
            potential_memory = self.memory_for_address(address=addr)
            if potential_memory is not None:
                potential_memory.memory.write(offset=potential_memory.memory_offset(addr),
                                              data=data)

    def _read_block(self, addr: int, width: int, accesswidth: int, length: int) -> Array:
        """
        function to simulate a device block read, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        addresses = self._block_access_addresses(start_address=addr, width=width, length=length)
        data = [self._read(element_addr, width=width, accesswidth=accesswidth)
                for element_addr in addresses]
        return Array(get_array_typecode(width),data)

    def _write_block(self, addr: int, width: int, accesswidth: int, data: Array) -> None:
        """
        function to simulate a device block write, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        addresses = self._block_access_addresses(start_address=addr,
                                                  width=width,
                                                  length=len(data))
        for (element_address, element_data) in zip(addresses, data):
            self._write(addr=element_address,
                       data=element_data,
                       width=width,
                       accesswidth=accesswidth)

    @staticmethod
    def _block_access_addresses(start_address: int, width: int, length: int) -> range:
        """

        Args:
            start_address: start byte address
            width: word width
            length: number of word in the block

        Returns: range iterator for the addresses in the block
        """
        address_increment = width >> 3
        end_address = start_address + (length * address_increment)
        return range(start_address, end_address, address_increment)


class Simulator(BaseSimulator, ABC):
    """
    Base class of a simple simulator that uses non-async callbacks that can be used to test and
    debug peakrdl-python generated register access layer (RAL)
    """

    def read(self, addr: int,
             width: int, # pylint: disable=unused-argument
             accesswidth: int) -> int: # pylint: disable=unused-argument
        """
        function to simulate a device read, this needs to match the protocol for the callbacks
        """
        return self._read(addr, width, accesswidth)

    def write(self, addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        function to simulate a device write, this needs to match the protocol for the callbacks
        """
        return self._write(addr, width, accesswidth, data)

    def read_block(self, addr: int, width: int, accesswidth: int, length: int) -> Array:
        """
        function to simulate a device block read, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        return self._read_block(addr, width, accesswidth, length)

    def write_block(self, addr: int, width: int, accesswidth: int, data: Array) -> None:
        """
        function to simulate a device block write, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        return self._write_block(addr, width, accesswidth, data)


class AsyncSimulator(BaseSimulator, ABC):
    """
    Base class of a simple simulator that uses async callbacks that can be used to test and
    debug peakrdl-python generated register access layer (RAL)
    """

    async def read(self, addr: int,
                   width: int,  # pylint: disable=unused-argument
                   accesswidth: int) -> int:  # pylint: disable=unused-argument
        """
        function to simulate a device read, this needs to match the protocol for the callbacks
        """
        await asyncio.sleep(0)
        return self._read(addr, width, accesswidth)

    async def write(self, addr: int, width: int, accesswidth: int, data: int) -> None:
        """
        function to simulate a device write, this needs to match the protocol for the callbacks
        """
        await asyncio.sleep(0)
        return self._write(addr, width, accesswidth, data)

    async def read_block(self, addr: int, width: int, accesswidth: int, length: int) -> Array:
        """
        function to simulate a device block read, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        await asyncio.sleep(0)
        return self._read_block(addr, width, accesswidth, length)

    async def write_block(self, addr: int, width: int, accesswidth: int, data: Array) -> None:
        """
        function to simulate a device block write, this needs to match the protocol for the
        callbacks

        This currently uses a simplified implementation of converting all the block operations
        to discrete operations, a future enhancement could be to access slices of memories
        """
        await asyncio.sleep(0)
        return self._write_block(addr, width, accesswidth, data)
