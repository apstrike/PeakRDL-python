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
from typing import List, Optional

from .memory import Memory
from .base import Base
from .field import FieldDefinition, Field
from ._callbacks import RegisterReadCallback,RegisterWriteCallback

# pylint: disable=too-many-arguments

class BaseRegister(Base, ABC):
    """
    Base class for registers
    """

    __slots__ = ['_width', '_readable', '_writable', 'fields',
                 '__read_callback', '__write_callback']

    def __init__(self, *,
                 width: int,
                 full_inst_name: str,
                 readable: bool,
                 writable: bool,
                 fields: List[FieldDefinition]):
        super().__init__(full_inst_name=full_inst_name)
        self._width = width
        self._readable = readable
        self._writable = writable
        self.fields = [Field(low=field_def.low,
                             high=field_def.high,
                             msb=field_def.msb,
                             lsb=field_def.lsb,
                             inst_name=field_def.inst_name,
                             parent_register=self,
                             parent_width=width) for field_def in fields]
        self.__read_callback: Optional[RegisterReadCallback] = None
        self.__write_callback: Optional[RegisterWriteCallback] = None

    @property
    def read_callback(self) -> Optional[RegisterReadCallback]:
        """
        Callback made during each read operation
        """
        return self.__read_callback

    @read_callback.setter
    def read_callback(self, callback: Optional[RegisterReadCallback]) -> None:
        self.__read_callback = callback

    @property
    def write_callback(self) -> Optional[RegisterWriteCallback]:
        """
        Callback made during each write operation
        """
        return self.__write_callback

    @write_callback.setter
    def write_callback(self, callback: Optional[RegisterWriteCallback]) -> None:
        self.__write_callback = callback

    def _action_read_callback(self) -> None:
        if self.read_callback is not None:
            # pylint does not recognise that the property is returning a callback therefore it
            # is legal to call it.
            # pylint: disable-next=not-callable
            self.read_callback(value=self.value)

        for field in self.fields:
            if field.read_callback is not None:
                field.read_callback(value=field.value)

    def _action_write_callback(self) -> None:
        if self.write_callback is not None:
            # pylint does not recognise that the property is returning a callback therefore it
            # is legal to call it.
            # pylint: disable-next=not-callable
            self.write_callback(value=self.value)

        for field in self.fields:
            if field.write_callback is not None:
                field.write_callback(value=field.value)

    @abstractmethod
    def read(self) -> int:
        """
        Read the register

        Returns:
            register content

        """

    @abstractmethod
    def write(self, data: int) -> None:
        """
        Write the register

        Args:
            data (int): new register content

        Returns:
            None

        """

    @property
    @abstractmethod
    def value(self) -> int:
        """
        Access the register value without triggering the callbacks
        """

    @value.setter
    @abstractmethod
    def value(self, value:int) -> None:
        ...


class Register(BaseRegister):
    """
    Class for Register that is created in normal logic
    """

    __slots__ = ['__value']

    def __init__(self, *,
                 width: int,
                 full_inst_name: str,
                 readable: bool,
                 writable: bool,
                 fields: List[FieldDefinition]):
        super().__init__(width=width, full_inst_name=full_inst_name,
                         readable=readable, writable=writable, fields=fields)
        self.__value = 0

    def read(self) -> int:

        self._action_read_callback()
        return self.__value

    def write(self, data: int) -> None:

        self.__value = data
        self._action_write_callback()

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        self.__value = value


class MemoryRegister(BaseRegister):
    """
    Class for Register that maps onto a memory
    """

    __slots__ = ['__memory', '__offset']

    def __init__(self, *,
                 width: int,
                 full_inst_name: str,
                 readable: bool,
                 writable: bool,
                 memory: Memory,
                 memory_address_offset: int,
                 fields: List[FieldDefinition]):
        super().__init__(width=width, full_inst_name=full_inst_name,
                         readable=readable, writable=writable, fields=fields)
        if not isinstance(memory, Memory):
            raise TypeError(f'memory type is wrong, got {type(memory)}')
        self.__memory = memory
        self.__offset = memory.byte_offset_to_word_offset(memory_address_offset)

    def read(self) -> int:
        self._action_read_callback()
        return self.__memory.read(self.__offset)

    def write(self, data: int) -> None:
        self.__memory.write(self.__offset, data)
        self._action_write_callback()

    @property
    def value(self) -> int:
        return self.__memory.value[self.__offset]

    @value.setter
    def value(self, value: int) -> None:
        self.__memory.value[self.__offset] = value
