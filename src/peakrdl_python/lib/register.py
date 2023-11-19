"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code to represent register
"""
from enum import Enum
from typing import List, Union, Iterator, TYPE_CHECKING, Tuple, cast, Optional, Dict
from typing import AsyncGenerator, Generator
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from array import array as Array

from .base import Node, AddressMap, RegFile, NodeArray, get_array_typecode
from .base import AsyncAddressMap, AsyncRegFile
from .memory import  MemoryReadOnly, MemoryWriteOnly, MemoryReadWrite, \
    MemoryAsyncReadOnly, MemoryAsyncWriteOnly, MemoryAsyncReadWrite, BaseMemory, \
    Memory, AsyncMemory, ReadableAsyncMemory, WritableAsyncMemory, ReadableMemory, WritableMemory
from .callbacks import NormalCallbackSet, AsyncCallbackSet

if TYPE_CHECKING:
    from .fields import FieldReadOnly, FieldWriteOnly, FieldReadWrite
    from .fields import FieldAsyncReadOnly, FieldAsyncWriteOnly, FieldAsyncReadWrite

# pylint: disable=redefined-slots-in-subclass


class RegisterWriteVerifyError(Exception):
    """
    Exception that occurs when the read after a write does not match the expected value
    """


class BaseReg(Node, ABC):
    """
    base class of register wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__width', '__accesswidth']

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, AsyncAddressMap, RegFile, AsyncRegFile, BaseMemory]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)
        if not isinstance(width, int):
            raise TypeError(f'width should be int but got {(type(width))}')
        if width not in (8, 16, 32, 64, 128, 256, 512, 1024, 2048):
            raise ValueError('currently only support 8, 16, 32, 64, 128, 256, 512, 1024 or 2048 '
                             f'width registers, got {width:d}')
        self.__width = width
        if not isinstance(accesswidth, int):
            raise TypeError(f'accesswidth should be int but got {(type(accesswidth))}')
        if accesswidth not in (8, 16, 32, 64):
            raise ValueError(f'currently only support 8, 16, 32 or 64 accesswidth, got {width:d}')
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments,duplicate-code

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the register

        For example:

        * 8-bit register returns 0xFF (255)
        * 16-bit register returns 0xFFFF (65535)
        * 32-bit register returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def width(self) -> int:
        """
        The width of the register in bits, this uses the `regwidth` systemRDL property

        Returns: register width

        """
        return self.__width

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property

        Returns: register access width
        """
        return self.__accesswidth

    @property
    def size(self) -> int:
        """
        Total Number of bytes of address the node occupies
        """
        return self.__width >> 3

class Reg(BaseReg, ABC):
    """
        base class of non-async register wrappers

        Note:
            It is not expected that this class will be instantiated under normal
            circumstances however, it is useful for type checking
        """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, Memory]):

        if not isinstance(parent, (AddressMap, RegFile,
                                   MemoryReadOnly, MemoryWriteOnly, MemoryReadWrite)):
            raise TypeError(f'bad parent type got: {type(parent)}')

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(address=address, width=width, accesswidth=accesswidth,
                         logger_handle=logger_handle, inst_name=inst_name, parent=parent)

    @property
    def _callbacks(self) -> NormalCallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # This cast is OK because the type was checked in the __init__
        # pylint: disable-next=protected-access
        return cast(NormalCallbackSet, self.parent._callbacks)

class AsyncReg(BaseReg, ABC):
    """
        base class of async register wrappers

        Note:
            It is not expected that this class will be instantiated under normal
            circumstances however, it is useful for type checking
        """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AsyncAddressMap, AsyncRegFile, AsyncMemory]):

        if not isinstance(parent, (AsyncAddressMap, AsyncRegFile,
                                   MemoryAsyncReadOnly, MemoryAsyncWriteOnly,
                                   MemoryAsyncReadWrite)):
            raise TypeError(f'bad parent type got: {type(parent)}')

        if not isinstance(parent._callbacks, AsyncCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(parent._callbacks)}')

        super().__init__(address=address, width=width, accesswidth=accesswidth,
                         logger_handle=logger_handle, inst_name=inst_name, parent=parent)

    @property
    def _callbacks(self) -> AsyncCallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # This cast is OK because the type was checked in the __init__
        # pylint: disable-next=protected-access
        return cast(AsyncCallbackSet, self.parent._callbacks)


class RegReadOnly(Reg, ABC):
    """
    class for a read only register

    Args:
        callbacks: set of callback to be used for accessing the hardware or simulator
        address: address of the register
        width: width of the register in bits
        accesswidth: minimum access width of the register in bits
        logger_handle: name to be used logging messages associate with this
            object

    """

    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, ReadableMemory]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: int = 0

    # pylint: enable=too-many-arguments, duplicate-code

    @contextmanager
    def single_read(self) -> Generator['RegReadOnly', None, None]:
        """
        Context manager to allow multiple field accesses to be performed with a single
        read of the register

        Returns:

        """
        self.__register_state = self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register

        """
        if self.__in_context_manager:
            return self.__register_state

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            return read_callback(addr=self.address,  # type: ignore[call-arg]
                                 width=self.width,  # type: ignore[call-arg]
                                 accesswidth=self.accesswidth)  # type: ignore[call-arg]

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            return read_block_callback(addr=self.address,  # type: ignore[call-arg]
                                       width=self.width,  # type: ignore[call-arg]
                                       accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                       length=1)[0]  # type: ignore[call-arg]

        raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def readable_fields(self) -> Iterator[Union['FieldReadOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """

    def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        with self.single_read() as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = field.read()

        return return_dict


class RegWriteOnly(Reg, ABC):
    """
    class for a write only register
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments, duplicate-code, useless-parent-delegation
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, WritableMemory]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)
    # pylint: enable=too-many-arguments, duplicate-code

    def write(self, data: int) -> None:
        """Writes a value to the register

        Args:
            data: data to be written

        Raises:
            ValueError: if the value provided is outside the range of the
                permissible values for the register
            TypeError: if the type of data is wrong
        """
        if not isinstance(data, int):
            raise TypeError(f'data should be an int got {type(data)}')

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info('Writing data:%X to %X', data, self.address)

        block_callback = self._callbacks.write_block_callback
        single_callback = self._callbacks.write_callback

        if single_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            single_callback(addr=self.address,  # type: ignore[call-arg]
                            width=self.width,  # type: ignore[call-arg]
                            accesswidth=self.accesswidth,  # type: ignore[call-arg]
                            data=data)  # type: ignore[call-arg]

        elif block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            data_as_array = Array(get_array_typecode(self.width), [data])
            block_callback(addr=self.address,  # type: ignore[call-arg]
                           width=self.width,  # type: ignore[call-arg]
                           accesswidth=self.accesswidth,  # type: ignore[call-arg]
                           data=data_as_array)  # type: ignore[call-arg]

        else:
            raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def writable_fields(self) -> Iterator[Union['FieldWriteOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """

    @abstractmethod
    def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Do a write to the register, updating any field included in
        the arguments
        """


class RegReadWrite(RegReadOnly, RegWriteOnly, ABC):
    """
    class for a read and write only register

    """
    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, MemoryReadWrite]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: Optional[int] = None

    # pylint: enable=too-many-arguments, duplicate-code

    @contextmanager
    def single_read_modify_write(self, verify: bool = False, skip_write: bool = False) -> \
            Generator['RegReadWrite', None, None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:
            verify (bool): very the write with a read afterwards
            skip_write (bool): skip the write back at the end

        Returns:

        """
        self.__register_state = self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False
        if not skip_write:
            self.write(self.__register_state, verify)

        # clear the register states at the end of the context manager
        self.__register_state = None

    def write(self, data: int, verify: bool = False) -> None:  # pylint: disable=arguments-differ
        """
        Writes a value to the register

        Args:
            data: data to be written
            verify: set to True to read back the register to verify the read has occurred correctly

        Raises:
            ValueError: if the value provided is outside the range of the
                        permissible values for the register
            TypeError: if the type of data is wrong
            RegisterWriteVerifyError: the read back data after the write does not match the
                                      expected value
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            self.__register_state = data
        else:
            super().write(data)
            if verify:
                read_back = self.read()
                if read_back != data:
                    raise RegisterWriteVerifyError(f'Readback {read_back:X} '
                                                   f'after writing {data:X}')

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            return self.__register_state

        return super().read()

    def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Do a read-modify-write to the register, updating any field included in
        the arguments
        """
        if len(kwargs) == 0:
            raise ValueError('no command args')

        with self.single_read_modify_write() as reg:
            for field_name, field_value in kwargs.items():
                if field_name not in reg.systemrdl_python_child_name_map.values():
                    raise ValueError(f'{field_name} is not a member of the register')

                field = getattr(reg, field_name)
                field.write(field_value)

    def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        with self.single_read_modify_write(skip_write=True) as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = field.read()

        return return_dict


class RegAsyncReadOnly(AsyncReg, ABC):
    """
    class for an async read only register

    Args:
        callbacks: set of callback to be used for accessing the hardware or simulator
        address: address of the register
        width: width of the register in bits
        accesswidth: minimum access width of the register in bits
        logger_handle: name to be used logging messages associate with this
            object

    """

    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AsyncAddressMap, AsyncRegFile, ReadableAsyncMemory]):


        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: int = 0
    # pylint: enable=too-many-arguments, duplicate-code

    @asynccontextmanager
    async def single_read(self) -> AsyncGenerator['RegAsyncReadOnly', None]:
        """
        Context manager to allow multiple field accesses to be performed with a single
        read of the register

        Returns:

        """
        self.__register_state = await self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False

    async def read(self) -> int:
        """Asynchronously read value from the register

        Returns:
            The value from register

        """
        if self.__in_context_manager:
            return self.__register_state

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            return await read_callback(addr=self.address,  # type: ignore[call-arg]
                                       width=self.width,  # type: ignore[call-arg]
                                       accesswidth=self.accesswidth)  # type: ignore[call-arg]

        if read_block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            array_read_result = \
                await read_block_callback(addr=self.address,  # type: ignore[call-arg]
                                          width=self.width,  # type: ignore[call-arg]
                                          accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                          length=1)  # type: ignore[call-arg]
            return array_read_result[0]

        raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def readable_fields(self) -> Iterator[Union['FieldAsyncReadOnly', 'FieldAsyncReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """

    async def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        asynchronously read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        async with self.single_read() as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = await field.read()

        return return_dict


class RegAsyncWriteOnly(AsyncReg, ABC):
    """
    class for an asynchronous write only register
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments, duplicate-code, useless-parent-delegation
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AsyncAddressMap, AsyncRegFile, WritableAsyncMemory]):


        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)
    # pylint: enable=too-many-arguments, duplicate-code

    async def write(self, data: int) -> None:
        """Asynchronously writes a value to the register

        Args:
            data: data to be written

        Raises:
            ValueError: if the value provided is outside the range of the
                permissible values for the register
            TypeError: if the type of data is wrong
        """
        if not isinstance(data, int):
            raise TypeError(f'data should be an int got {type(data)}')

        if data > self.max_value:
            raise ValueError('data out of range')

        if data < 0:
            raise ValueError('data out of range')

        self._logger.info('Writing data:%X to %X', data, self.address)

        block_callback = self._callbacks.write_block_callback
        single_callback = self._callbacks.write_callback

        if single_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            await single_callback(addr=self.address,  # type: ignore[call-arg]
                                  width=self.width,  # type: ignore[call-arg]
                                  accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                  data=data)  # type: ignore[call-arg]

        elif block_callback is not None:
            # python 3.7 doesn't have the callback defined as protocol so mypy doesn't recognise
            # the arguments in the call back functions
            data_as_array = Array(get_array_typecode(self.width), [data])
            await block_callback(addr=self.address,  # type: ignore[call-arg]
                                 width=self.width,  # type: ignore[call-arg]
                                 accesswidth=self.accesswidth,  # type: ignore[call-arg]
                                 data=data_as_array)  # type: ignore[call-arg]

        else:
            raise RuntimeError('This function does not have a useable callback')

    @property
    @abstractmethod
    def writable_fields(self) -> Iterator[Union['FieldAsyncWriteOnly', 'FieldAsyncReadWrite']]:
        """
        generator that produces has all the writable fields within the register
        """

    @abstractmethod
    async def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        Do an async write to the register, updating any field included in
        the arguments
        """


class RegAsyncReadWrite(RegAsyncReadOnly, RegAsyncWriteOnly, ABC):
    """
    class for an async read and write only register

    """
    __slots__: List[str] = ['__in_context_manager', '__register_state']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self, *,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AsyncAddressMap, AsyncRegFile, MemoryAsyncReadWrite]):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent, width=width, accesswidth=accesswidth)

        self.__in_context_manager: bool = False
        self.__register_state: Optional[int] = None

    # pylint: enable=too-many-arguments, duplicate-code

    @asynccontextmanager
    async def single_read_modify_write(self, verify: bool = False, skip_write: bool = False) -> \
        AsyncGenerator['RegAsyncReadWrite', None]:
        """
        Context manager to allow multiple field reads/write to be done with a single set of
        field operations

        Args:
            verify (bool): very the write with a read afterwards
            skip_write (bool): skip the write back at the end

        Returns:

        """
        self.__register_state = await self.read()
        self.__in_context_manager = True
        yield self
        self.__in_context_manager = False
        if not skip_write:
            await self.write(self.__register_state, verify)

        # clear the register states at the end of the context manager
        self.__register_state = None

    async def write(self, data: int, verify: bool = False) -> None:
        """
        Writes a value to the register

        Args:
            data: data to be written
            verify: set to True to read back the register to verify the read has occurred correctly

        Raises:
            ValueError: if the value provided is outside the range of the
                        permissible values for the register
            TypeError: if the type of data is wrong
            RegisterWriteVerifyError: the read back data after the write does not match the
                                      expected value
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            self.__register_state = data
        else:
            await super().write(data)
            if verify:
                read_back = await self.read()
                if read_back != data:
                    raise RegisterWriteVerifyError(f'Readback {read_back:X} '
                                                   f'after writing {data:X}')

    async def read(self) -> int:
        """Asynchronously read value from the register

        Returns:
            The value from register
        """
        if self.__in_context_manager:
            if self.__register_state is None:
                raise RuntimeError('The internal register state should never be None in the '
                                   'context manager')
            return self.__register_state

        return await super().read()

    async def read_fields(self) -> Dict['str', Union[bool, Enum, int]]:
        """
        asynchronously read the register and return a dictionary of the field values
        """
        return_dict: Dict['str', Union[bool, Enum, int]] = {}
        async with self.single_read_modify_write(skip_write=True) as reg:
            for field in reg.readable_fields:
                return_dict[field.inst_name] = await field.read()

        return return_dict

    async def write_fields(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """
        asynchronously read-modify-write to the register, updating any field included in
        the arguments
        """
        if len(kwargs) == 0:
            raise ValueError('no command args')

        async with self.single_read_modify_write() as reg:
            for field_name, field_value in kwargs.items():
                if field_name not in reg.systemrdl_python_child_name_map.values():
                    raise ValueError(f'{field_name} is not a member of the register')

                field = getattr(reg, field_name)
                await field.write(field_value)


ReadableRegister = Union[RegReadOnly, RegReadWrite]
WritableRegister = Union[RegWriteOnly, RegReadWrite]
ReadableAsyncRegister = Union[RegAsyncReadOnly, RegAsyncReadWrite]
WritableAsyncRegister = Union[RegAsyncWriteOnly, RegAsyncReadWrite]


class RegReadOnlyArray(NodeArray, ABC):
    """
    base class for a array of read only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, ReadableMemory],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegReadOnly]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryReadOnly, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, '
                            'MemoryReadOnly, MemoryReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


class RegWriteOnlyArray(NodeArray, ABC):
    """
    base class for a array of write only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, WritableMemory],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegWriteOnly]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryWriteOnly, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, MemoryWriteOnly, '
                            'MemoryReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


class RegReadWriteArray(NodeArray, ABC):
    """
    base class for a array of read and write registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, MemoryReadWrite],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegReadWrite]] = None):

        if not isinstance(parent, (RegFile, AddressMap, MemoryReadWrite)):
            raise TypeError('parent should be either RegFile, AddressMap, MemoryReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


class RegAsyncReadOnlyArray(NodeArray, ABC):
    """
    base class for a array of async read only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AsyncRegFile, AsyncAddressMap, ReadableAsyncMemory],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegAsyncReadOnly]] = None):

        if not isinstance(parent, (AsyncRegFile, AsyncAddressMap,
                                   MemoryAsyncReadOnly, MemoryAsyncReadWrite)):
            raise TypeError('parent should be either AsyncRegFile, AsyncAddressMap, '
                            'MemoryAsyncReadOnly, MemoryAsyncReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


class RegAsyncWriteOnlyArray(NodeArray, ABC):
    """
    base class for a array of async write only registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AsyncRegFile, AsyncAddressMap, WritableAsyncMemory],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegAsyncWriteOnly]] = None):

        if not isinstance(parent, (AsyncRegFile, AsyncAddressMap,
                                   MemoryAsyncWriteOnly, MemoryAsyncReadWrite)):
            raise TypeError('parent should be either AsyncRegFile, AsyncAddressMap, '
                            'MemoryAsyncWriteOnly, MemoryAsyncReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


class RegAsyncReadWriteArray(NodeArray, ABC):
    """
    base class for a array of read and write registers
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments,duplicate-code
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AsyncRegFile, AsyncAddressMap, MemoryAsyncReadWrite],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], RegAsyncReadWrite]] = None):

        if not isinstance(parent, (AsyncRegFile, AsyncAddressMap, MemoryAsyncReadWrite)):
            raise TypeError('parent should be either AsyncRegFile, AsyncAddressMap, '
                            'MemoryAsyncReadWrite '
                            f'got {type(parent)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions, elements=elements)
    # pylint: enable=too-many-arguments,duplicate-code


ReadableRegisterArray = Union[RegReadOnlyArray, RegReadWriteArray]
WriteableRegisterArray = Union[RegWriteOnlyArray, RegReadWriteArray]
ReadableAsyncRegisterArray = Union[RegAsyncReadOnlyArray, RegAsyncReadWriteArray]
WriteableAsyncRegisterArray = Union[RegAsyncWriteOnlyArray, RegAsyncReadWriteArray]
