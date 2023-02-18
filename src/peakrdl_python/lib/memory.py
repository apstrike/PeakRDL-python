"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code to represent memories
"""
from array import array as Array
from typing import List, Union, Tuple, Iterator, TYPE_CHECKING, cast
from abc import ABC, abstractmethod

from .base import Node, AddressMap, BaseArray, get_array_typecode

from .callbacks import CallbackSet, NormalCallbackSet, AysncCallbackSet

if TYPE_CHECKING:
    from .register import ReadableRegister, WritableRegister
    from .register import ReadableAsyncRegister, WritableAsyncRegister

# pylint: disable=duplicate-code

class Memory(Node, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__memwidth', '__entries', '__accesswidth']

    # pylint: disable=too-many-arguments
    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):
        """
        Initialise the class

        Args:
            callbacks: set of callback to be used for accessing the hardware or simulator
            address: address of the register
            width: width of the register in bits
            logger_handle: name to be used logging messages associate with thisobject
        """
        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        self.__memwidth = width
        self.__entries = entries
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments

    @property
    def width(self) -> int:
        """
        The width of the memory in bits, this uses the `memwidth` systemRDL property

        Returns: memory width

        """
        return self.__memwidth

    @property
    def width_in_bytes(self) -> int:
        """
        The width of the memory bytes, i.e. the width in bits divided by 8

        Returns: memory width (in bytes)

        """
        return self.width >> 3

    @property
    def entries(self) -> int:
        """
        The number of entries in the memory, this uses the `mementries` systemRDL property

        Returns: memory entries

        """
        return self.__entries

    @property
    def array_typecode(self) -> str:
        """
        the python array.array type is initialised with a typecode. This property provides the
        recommended typecode to use with this class instance (based on the memwidth)

        Returns: typecode

        """
        return get_array_typecode(self.width)

    @property
    def size_in_bytes(self) -> int:
        """
        size in bytes

        Returns: memory size
        """
        return self.entries * self.width_in_bytes

    def address_lookup(self, entry: int) -> int:
        """
        provides the address for an entry in the memory.

        Examples

        Args:
            entry: entry number to look up the address for

        Returns: Address

        """
        if not isinstance(entry, int):
            raise TypeError(f'entry must be an int but got {type(entry)}')

        if entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries-1:d} but got {entry:d}')

        return self.address + (entry * self.width_in_bytes)

    @property
    def accesswidth(self) -> int:
        """
        The access width of the register in bits, this uses the `accesswidth` systemRDL property

        Returns: register access width
        """
        return self.__accesswidth


class MemoryReadOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 callbacks: NormalCallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):

        if not isinstance(callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(callbacks)}')

        super().__init__(callbacks=callbacks,
                         address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> NormalCallbackSet:
        # This cast is OK because the type was checked in the __init__
        return cast(NormalCallbackSet, super()._callbacks)

    def read(self, start_entry: int, number_entries: int) -> Array:
        """
        Read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of enries to read

        Returns: data read from memory

        """

        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if not isinstance(number_entries, int):
            raise TypeError(f'number_entries should be an int got {type(number_entries)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if number_entries not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'number_entries must be in range 0 to'
                             f' {self.entries - start_entry:d} but got {number_entries:d}')

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_block_callback is not None:

            data_read = read_block_callback(addr=self.address_lookup(entry=start_entry),
                                            width=self.width,
                                            accesswidth=self.width,
                                            length=number_entries)

            if not isinstance(data_read, Array):
                raise TypeError('The read block callback is expected to return an array')

        elif read_callback is not None:
            # there is not read_block_callback defined so we must used individual read
            data_read = Array(self.array_typecode, [0 for _ in range(number_entries)])

            for entry in range(number_entries):
                entry_address = self.address_lookup(entry=start_entry+entry)
                data_entry = read_callback(addr=entry_address,
                                           width=self.width,
                                           accesswidth=self.width)

                data_read[entry] = data_entry
        else:
            raise RuntimeError(f'There is no usable callback, '
                               f'block callback:{read_block_callback}, '
                               f'normal callback:{read_callback}')

        return data_read

    @abstractmethod
    def get_readable_registers(self, unroll: bool = False) -> Iterator[Union['ReadableRegister',
                                                               Tuple['ReadableRegister', ...]]]:
        """
        generator that produces all the readable_registers of this node
        """


class MemoryWriteOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 callbacks: NormalCallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):

        if not isinstance(callbacks, NormalCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(callbacks)}')

        super().__init__(callbacks=callbacks,
                         address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> NormalCallbackSet:
        # This cast is OK because the type was checked in the __init__
        return cast(NormalCallbackSet, super()._callbacks)

    def write(self, start_entry: int, data: Array) -> None:
        """
        Write data to memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            data: data to write

        Returns: None

        """
        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if not isinstance(data, Array):
            raise TypeError(f'data should be an array.array got {type(data)}')

        if len(data) not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'data length must be in range 0 to {self.entries - start_entry:d} '
                             f'but got {len(data):d}')

        write_block_callback = self._callbacks.write_block_callback
        write_callback = self._callbacks.write_callback

        if write_block_callback is not None:

            write_block_callback(addr=self.address_lookup(entry=start_entry),
                                 width=self.width,
                                 accesswidth=self.width,
                                 data=data)


        elif write_callback is not None:
            # there is not write_block_callback defined so we must used individual write
            for entry_index, entry_data in enumerate(data):
                entry_address = self.address_lookup(entry=start_entry+entry_index)
                write_callback(addr=entry_address,
                               width=self.width,
                               accesswidth=self.width,
                               data=entry_data)

        else:
            raise RuntimeError('No suitable callback')

    @abstractmethod
    def get_writable_registers(self, unroll: bool = False) -> \
            Iterator[Union['WritableRegister',Tuple['WritableRegister', ...]]]:
        """
        generator that produces all the readable_registers of this node
        """


class MemoryReadWrite(MemoryReadOnly, MemoryWriteOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []


class MemoryAsyncReadOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 callbacks: AysncCallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):

        if not isinstance(callbacks, AysncCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(callbacks)}')

        super().__init__(callbacks=callbacks,
                         address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> AysncCallbackSet:
        # This cast is OK because the type was checked in the __init__
        return cast(AysncCallbackSet, super()._callbacks)

    async def read(self, start_entry: int, number_entries: int) -> Array:
        """
        Asynchronously read from the memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            number_entries: number of entries to read

        Returns: data read from memory

        """

        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if not isinstance(number_entries, int):
            raise TypeError(f'number_entries should be an int got {type(number_entries)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if number_entries not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'number_entries must be in range 0 to'
                             f' {self.entries - start_entry:d} but got {number_entries:d}')

        read_block_callback = self._callbacks.read_block_callback
        read_callback = self._callbacks.read_callback

        if read_block_callback is not None:

            data_read = await read_block_callback(addr=self.address_lookup(entry=start_entry),
                                                  width=self.width,
                                                  accesswidth=self.width,
                                                  length=number_entries)

            if not isinstance(data_read, Array):
                raise TypeError('The read block callback is expected to return an array')

        elif read_callback is not None:
            # there is not read_block_callback defined so we must used individual read
            data_read = Array(self.array_typecode, [0 for _ in range(number_entries)])

            for entry in range(number_entries):
                entry_address = self.address_lookup(entry=start_entry+entry)
                data_entry = await read_callback(addr=entry_address,
                                                 width=self.width,
                                                 accesswidth=self.width)

                data_read[entry] = data_entry

        else:
            raise RuntimeError('No suitable callback type available')

        return data_read

    @abstractmethod
    def get_readable_registers(self,
                               unroll:bool=False) -> \
            Iterator[Union['ReadableAsyncRegister', Tuple['ReadableAsyncRegister', ...]]]:
        """
        generator that produces all the readable_registers of this node
        """


class MemoryAsyncWriteOnly(Memory, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    # pylint: disable=too-many-arguments
    def __init__(self,
                 callbacks: AysncCallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 entries: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: AddressMap):

        if not isinstance(callbacks, AysncCallbackSet):
            raise TypeError(f'callback set type is wrong, got {type(callbacks)}')

        super().__init__(callbacks=callbacks,
                         address=address,
                         width=width,
                         accesswidth=accesswidth,
                         entries=entries,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    # pylint: enable=too-many-arguments
    @property
    def _callbacks(self) -> AysncCallbackSet:
        # This cast is OK because the type was checked in the __init__
        return cast(AysncCallbackSet, super()._callbacks)

    async def write(self, start_entry: int, data: Array) -> None:
        """
        Asynchronously write data to memory

        Args:
            start_entry: index in the memory to start from, this is not the address
            data: data to write

        Returns: None

        """
        if not isinstance(start_entry, int):
            raise TypeError(f'start_entry should be an int got {type(start_entry)}')

        if start_entry not in range(0, self.entries):
            raise ValueError(f'entry must be in range 0 to {self.entries - 1:d} '
                             f'but got {start_entry:d}')

        if not isinstance(data, Array):
            raise TypeError(f'data should be an array.array got {type(data)}')

        if len(data) not in range(0, self.entries - start_entry + 1):
            raise ValueError(f'data length must be in range 0 to {self.entries - start_entry:d} '
                             f'but got {len(data):d}')

        write_block_callback = self._callbacks.write_block_callback
        write_callback = self._callbacks.write_callback

        if write_block_callback is not None:

            await write_block_callback(addr=self.address_lookup(entry=start_entry),
                                       width=self.width,
                                       accesswidth=self.width,
                                       data=data)

        elif write_callback is not None:
            # there is not write_block_callback defined so we must used individual write
            for entry_index, entry_data in enumerate(data):
                entry_address = self.address_lookup(entry=start_entry+entry_index)
                await write_callback(addr=entry_address,
                                     width=self.width,
                                     accesswidth=self.width,
                                     data=entry_data)

        else:
            raise RuntimeError('No suitable callback')

    @abstractmethod
    def get_writable_registers(self,
                               unroll:bool=False) -> Iterator[Union['WritableAsyncRegister',
                                                         Tuple['WritableAsyncRegister', ...]]]:
        """
        generator that produces all the readable_registers of this node
        """


class MemoryAsyncReadWrite(MemoryAsyncReadOnly, MemoryAsyncWriteOnly, ABC):
    """
    base class of memory wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []


class MemoryReadOnlyArray(BaseArray, ABC):
    """
    base class for a array of read only memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryReadOnly, ...]):

        for element in elements:
            if not isinstance(element, MemoryReadOnly):
                raise TypeError(
                    f'All Elements should be of type MemoryReadOnly, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item:Union[int, slice]) -> \
            Union[MemoryReadOnly, Tuple[MemoryReadOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryReadOnly, Tuple[MemoryReadOnly, ...]], super().__getitem__(item))


class MemoryWriteOnlyArray(BaseArray, ABC):
    """
    base class for a array of write only memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryWriteOnly, ...]):

        for element in elements:
            if not isinstance(element, MemoryWriteOnly):
                raise TypeError(
                    f'All Elements should be of type MemoryWriteOnly, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item:Union[slice, int]) ->\
            Union[MemoryWriteOnly, Tuple[MemoryWriteOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryWriteOnly, Tuple[MemoryWriteOnly, ...]], super().__getitem__(item))


class MemoryReadWriteArray(MemoryReadOnlyArray, MemoryWriteOnlyArray, ABC):
    """
    base class for a array of read and write memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryReadWrite, ...]):

        for element in elements:
            if not isinstance(element, MemoryReadWrite):
                raise TypeError(
                    f'All Elements should be of type MemoryReadWrite, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item:Union[int, slice]) -> \
            Union[MemoryReadWrite, Tuple[MemoryReadWrite, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryReadWrite, Tuple[MemoryReadWrite, ...]], super().__getitem__(item))


class MemoryAsyncReadOnlyArray(BaseArray, ABC):
    """
    base class for a array of asynchronous read only memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryAsyncReadOnly, ...]):

        for element in elements:
            if not isinstance(element, MemoryAsyncReadOnly):
                raise TypeError(
                    f'All Elements should be of type MemoryAsyncReadOnly, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item:Union[int, slice]) -> \
            Union[MemoryAsyncReadOnly, Tuple[MemoryAsyncReadOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryAsyncReadOnly, Tuple[MemoryAsyncReadOnly, ...]],
                    super().__getitem__(item))


class MemoryAsyncWriteOnlyArray(BaseArray, ABC):
    """
    base class for a array of asynchronous write only memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryAsyncWriteOnly, ...]):

        for element in elements:
            if not isinstance(element, MemoryAsyncWriteOnly):
                raise TypeError(
                    f'All Elements should be of type MemoryAsyncWriteOnly, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item:Union[int, slice]) -> \
            Union[MemoryAsyncWriteOnly, Tuple[MemoryAsyncWriteOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryAsyncWriteOnly, Tuple[MemoryAsyncWriteOnly, ...]],
                    super().__getitem__(item))


class MemoryAsyncReadWriteArray(MemoryAsyncReadOnlyArray, MemoryAsyncWriteOnlyArray, ABC):
    """
    base class for a array of asynchronous read and write memories
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 elements: Tuple[MemoryAsyncReadWrite, ...]):

        for element in elements:
            if not isinstance(element, MemoryAsyncReadWrite):
                raise TypeError(
                    f'All Elements should be of type MemoryAsyncReadWrite, found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item: Union[slice, int]) -> \
            Union[MemoryAsyncReadWrite, Tuple[MemoryAsyncReadWrite, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[MemoryAsyncReadWrite, Tuple[MemoryAsyncReadWrite, ...]],
                    super().__getitem__(item))
