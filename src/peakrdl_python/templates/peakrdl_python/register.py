"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code to represent register
"""
from typing import List, Union, Iterator, TYPE_CHECKING, Tuple, cast
from abc import ABC, abstractmethod

from .base import Node, AddressMap, RegFile, BaseArray
from .memory import Memory
from .callbacks import CallbackSet

if TYPE_CHECKING:
    from .fields import FieldReadOnly, FieldWriteOnly, FieldReadWrite


class Reg(Node, ABC):
    """
    base class of register wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__width', '__accesswidth']

    # pylint: disable=too-many-arguments, duplicate-code
    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 width: int,
                 accesswidth: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, RegFile, Memory]):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        self.__width = width
        self.__accesswidth = accesswidth
    # pylint: enable=too-many-arguments, duplicate-code

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

    __slots__: List[str] = []

    def read(self) -> int:
        """Read value from the register

        Returns:
            The value from register

        """
        return self._callbacks.read_callback(addr=self.address,
                                             width=self.width,
                                             accesswidth=self.accesswidth)

    @property
    @abstractmethod
    def readable_fields(self) -> Iterator[Union['FieldReadOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """


class RegWriteOnly(Reg, ABC):
    """
    class for a write only register
    """

    __slots__: List[str] = []

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

        self._callbacks.write_callback(addr=self.address,
                                       width=self.width,
                                       accesswidth=self.accesswidth,
                                       data=data)

    @property
    @abstractmethod
    def writable_fields(self) -> Iterator[Union['FieldWriteOnly', 'FieldReadWrite']]:
        """
        generator that produces has all the readable fields within the register
        """


class RegReadWrite(RegReadOnly, RegWriteOnly, ABC):
    """
    class for a read and write only register

    """
    __slots__: List[str] = []


ReadableRegister = Union[RegReadOnly, RegReadWrite]
WritableRegister = Union[RegWriteOnly, RegReadWrite]


class RegReadOnlyArray(BaseArray, ABC):
    """
    base class for a array of read only registers
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, Memory],
                 elements: Tuple[RegReadOnly, ...]):

        for element in elements:
            if not isinstance(element, RegReadOnly):
                raise TypeError(f'All Elements should be of type RegReadOnly, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[RegReadOnly, Tuple[RegReadOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[RegReadOnly, Tuple[RegReadOnly, ...]], super().__getitem__(item))


class RegWriteOnlyArray(BaseArray, ABC):
    """
    base class for a array of write only registers
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, Memory],
                 elements: Tuple[RegWriteOnly, ...]):

        for element in elements:
            if not isinstance(element, RegWriteOnly):
                raise TypeError(f'All Elements should be of type RegWriteOnly, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[RegWriteOnly, Tuple[RegWriteOnly, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[RegWriteOnly, Tuple[RegWriteOnly, ...]], super().__getitem__(item))


class RegReadWriteArray(RegReadOnlyArray, RegWriteOnlyArray, ABC):
    """
    base class for a array of read and write registers
    """
    __slots__: List[str] = []

    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[RegFile, AddressMap, Memory],
                 elements: Tuple[RegReadWrite, ...]):

        for element in elements:
            if not isinstance(element, RegReadWrite):
                raise TypeError(f'All Elements should be of type RegReadWrite, '
                                f'found {type(element)}')

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, elements=elements)

    def __getitem__(self, item) -> Union[RegReadWrite, Tuple[RegReadWrite, ...]]:
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Union[RegReadWrite, Tuple[RegReadWrite, ...]], super().__getitem__(item))

ReadableRegisterArray = Union[RegReadOnlyArray, RegReadWriteArray]
WritableRegisterArray = Union[RegWriteOnlyArray, RegReadWriteArray]