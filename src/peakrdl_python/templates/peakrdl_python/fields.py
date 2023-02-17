"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code to represent register
fields
"""
from typing import List, cast, Optional
from abc import ABC, abstractmethod

from .base import Base
from .base import swap_msb_lsb_ordering
from .register import Reg
from .register import RegReadOnly, RegAsyncReadOnly
from .register import RegReadWrite, RegAsyncReadWrite
from .register import RegWriteOnly, RegAsyncWriteOnly
from .register import ReadableRegister, ReadableAsyncRegister
from .register import WritableRegister, WritableAsyncRegister


class FieldSizeProps:
    """
    class to hold the key attributes of a field
    """
    __slots__ = ['__msb', '__lsb', '__width', '__high', '__low']

    def __init__(self, width: int, msb: int, lsb: int, high: int, low: int): #pylint: disable=too-many-arguments
        self.__width = width
        self.__msb = msb
        self.__lsb = lsb
        self.__high = high
        self.__low = low

        if self.width < 1:
            raise ValueError('width must be greater than 0')

        if self.high < self.low:
            raise ValueError('field high bit position can not be less than the '
                             'low bit position')

        if self.lsb < 0:
            raise ValueError('field low bit position cannot be less than zero')

    @property
    def lsb(self) -> int:
        """
        bit position of the least significant bit (lsb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__lsb

    @property
    def msb(self) -> int:
        """
        bit position of the most significant bit (msb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__msb

    @property
    def width(self) -> int:
        """
        The width of the field in bits
        """
        return self.__width

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def high(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__high

    @property
    def low(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__low


class FieldMiscProps:
    """
    Class to hold additional attributes of a field
    """

    __slots__ = ['__default', '__is_volatile']

    def __init__(self, default:Optional[int], is_volatile:bool):
        self.__default = default
        self.__is_volatile = is_volatile

    @property
    def default(self) -> Optional[int]:
        """
        The default (reset) value of the field

        None
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        return self.__default

    @property
    def is_volatile(self) -> bool:
        """
        Volatility of the field. True if the field is hardware-writable.
        """
        return self.__is_volatile


class Field(Base, ABC):
    """
    base class of register field wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = ['__size_props', '__misc_props',
                 '__bitmask', '__msb0', '__lsb0']

    def __init__(self, parent_register: Reg, size_props: FieldSizeProps, misc_props: FieldMiscProps,
                 logger_handle: str, inst_name: str):

        super().__init__(logger_handle=logger_handle,
                         inst_name=inst_name, parent=parent_register)

        if not isinstance(size_props, FieldSizeProps):
            raise TypeError(f'size_props must be of {type(FieldSizeProps)} '
                            f'but got {type(size_props)}')
        self.__size_props = size_props

        if not isinstance(misc_props, FieldMiscProps):
            raise TypeError(f'misc_props must be of {type(FieldMiscProps)} '
                            f'but got {type(misc_props)}')
        self.__misc_props = misc_props

        if not isinstance(parent_register, Reg):
            raise TypeError(f'parent_register must be of {type(Reg)} '
                            f'but got {type(parent_register)}')

        if self.width > self.register_data_width:
            raise ValueError('width can not be greater than parent width')

        if self.high > self.register_data_width:
            raise ValueError(f'field high bit position {self.high:d} must be less than the '
                             f'parent register width ({self.register_data_width:d})')

        if self.low > self.register_data_width:
            raise ValueError('field lsb must be less than the parent '
                             'register width')

        if self.high - self.low + 1 != self.width:
            raise ValueError('field width defined by lsb and msb does not match'
                             ' specified width')

        if (self.msb == self.high) and (self.lsb == self.low):
            self.__lsb0 = True
            self.__msb0 = False
        elif (self.msb == self.low) and (self.lsb == self.high):
            self.__lsb0 = False
            self.__msb0 = True
        else:
            raise ValueError('msb/lsb are inconsistent with low/high')

        self.__bitmask = 0
        for bit_position in range(self.low, self.high+1):
            self.__bitmask |= (1 << bit_position)

    @property
    def lsb(self) -> int:
        """
        bit position of the least significant bit (lsb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__size_props.lsb

    @property
    def msb(self) -> int:
        """
        bit position of the most significant bit (msb) of the field in the
        parent register

        Note:
            fields can be defined as msb in bit 0 or as lsb in bit 0
        """
        return self.__size_props.msb

    @property
    def width(self) -> int:
        """
        The width of the field in bits
        """
        return self.__size_props.width

    @property
    def max_value(self) -> int:
        """maximum unsigned integer value that can be stored in the field

        For example:

        * 8-bit field returns 0xFF (255)
        * 16-bit field returns 0xFFFF (65535)
        * 32-bit field returns 0xFFFF_FFFF (4294967295)

        """
        return (2 ** self.width) - 1

    @property
    def high(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__size_props.high

    @property
    def low(self) -> int:
        """
        low index of the bit range of the field in the
        parent register

        Note:
            The first bit in the register is bit 0
        """
        return self.__size_props.low

    @property
    def bitmask(self) -> int:
        """
        The bit mask needed to extract the field from its register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a bit mask of 0x00F0
        """
        return self.__bitmask

    @property
    def register_data_width(self) -> int:
        """
        The width of the register within which the field resides in bits
        """
        return self.__parent_register.width

    @property
    def inverse_bitmask(self) -> int:
        """
        The bitwise inverse of the bitmask needed to extract the field from its
        register

        For example a register field occupying bits 7 to 4 in a 16-bit register
        will have a inverse bit mask of 0xFF0F
        """
        return self.__parent_register.max_value ^ self.bitmask

    @property
    def msb0(self) -> bool:
        """
        The field can either be lsb0 or msb0

        Returns: true if msb0

        """
        return self.__msb0

    @property
    def lsb0(self) -> bool:
        """
        The field can either be lsb0 or msb0

        Returns: true if lsb0

        """
        return self.__lsb0

    @property
    def default(self) -> Optional[int]:
        """
        The default value of the field

        This returns None:
        - if the field is not reset.
        - if the register resets to a signal value tht can not be determined
        """
        return self.__misc_props.default

    @property
    def is_volatile(self) -> bool:
        """
        The HW volatility of the field
        """
        return self.__misc_props.is_volatile

    @property
    def __parent_register(self) -> Reg:
        """
        parent register the field is placed in
        """
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Reg, self.parent)

class _FieldReadOnlyFramework(Field, ABC):
    """
    base class for a async or normal read only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def decode_read_value(self, value: int) -> int:
        """
        extracts the field value from a register value, by applying the bit
        mask and shift needed

        Args:
            value: value to decode, normally read from a register

        Returns:
            field value
        """
        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be decoded must be greater '
                             'than or equal to 0')

        if value > self.__parent_register.max_value:
            raise ValueError(f'value to bede coded must be less than or equal '
                             f'to {self.__parent_register.max_value:d}')

        if self.msb0 is False:
            return_value = (value & self.bitmask) >> self.low
        else:
            return_value = swap_msb_lsb_ordering(value=(value & self.bitmask) >> self.low,
                                                 width=self.width)

        return return_value

    @property
    def __parent_register(self) -> Reg:
        """
        parent register the field is placed in
        """
        # this cast is OK because an explict typing check was done in the __init__
        return cast(Reg, self.parent)

class FieldReadOnly(_FieldReadOnlyFramework, ABC):
    """
    class for a read only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def __init__(self,
                 parent_register: ReadableRegister,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, (RegReadWrite, RegReadOnly)):
            raise TypeError(f'size_props must be of {type(RegReadWrite)} or {type(RegReadOnly)} '
                            f'but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)

    def read(self) -> int:
        """
        Reads the register that this field is located in and retries the field
        value applying the required masking and shifting

        Returns:
            field value

        """
        return self.decode_read_value(self.parent_register.read())

    @property
    def parent_register(self) -> ReadableRegister:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(ReadableRegister, self.parent)

class _FieldWriteOnlyFramework(Field, ABC):
    """
    class for a write only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def encode_write_value(self, value: int) -> int:
        """
        Check that a value is legal for the field and then encode it in preparation to be written
        to the register

        Args:
            value: field value

        Returns:
            value which can be applied to the register to update the field

        """

        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError(f'value to be written to register must be less '
                             f'than or equal to {self.max_value:d}')

        if self.msb0 is False:
            return_value = value << self.low
        else:
            return_value = swap_msb_lsb_ordering(value=value,  width=self.width) << self.low

        return return_value


class FieldWriteOnly(_FieldWriteOnlyFramework, ABC):
    """
    class for a write only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def __init__(self,
                 parent_register: WritableRegister,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, (RegReadWrite, RegWriteOnly)):
            raise TypeError(f'size_props must be of {type(RegReadWrite)} or {type(RegWriteOnly)} '
                            f'but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)



    def write(self, value: int) -> None:
        """
        The behaviour of this method depends on whether the field is located in
        a readable register or not:

        If the register is readable, the method will perform a read-modify-write
        on the register updating the field with the value provided

        If the register is not writable all other field values will be written
        with zero.

        Args:
            value: field value to update to

        """

        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError(f'value to be written to register must be less '
                             f'than or equal to {self.max_value:d}')

        if self.msb0:
            value = swap_msb_lsb_ordering(value=value, width=self.width)

        if (self.high == (self.register_data_width - 1)) and (self.low == 0):
            # special case where the field occupies the whole register,
            # there a straight write can be performed
            new_reg_value = value
        else:
            # do a read, modify write
            if isinstance(self.parent_register, RegReadWrite):
                reg_value = self.parent_register.read()
                masked_reg_value = reg_value & self.inverse_bitmask
                new_reg_value = masked_reg_value | (value << self.low)
            elif isinstance(self.parent_register, RegWriteOnly):
                new_reg_value = value << self.low
            else:
                raise TypeError('Unhandled parent type')

        self.parent_register.write(new_reg_value)

    @property
    def parent_register(self) -> WritableRegister:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(WritableRegister, self.parent)


class FieldReadWrite(FieldReadOnly, FieldWriteOnly, ABC):
    """
    class for a read/write register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str]  = []

    def __init__(self, parent_register: RegReadWrite,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, RegReadWrite):
            raise TypeError(f'size_props must be of {type(RegReadWrite)} '
                            f'but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)

    @property
    def parent_register(self) -> RegReadWrite:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(RegReadWrite, self.parent)

class FieldAsyncReadOnly(_FieldReadOnlyFramework, ABC):
    """
    class for an asynchronous read only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def __init__(self,
                 parent_register: ReadableAsyncRegister,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, (RegAsyncReadWrite, RegAsyncReadOnly)):
            raise TypeError(f'size_props must be of {type(RegAsyncReadWrite)} or '
                            f'{type(RegAsyncReadOnly)} but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)

    async def read(self) -> int: # pylint: disable=invalid-overridden-method
        """
        Asynchronously reads the register that this field is located in and retries the field
        value applying the required masking and shifting

        Returns:
            field value

        """
        return self.decode_read_value(await self.parent_register.read())

    @property
    def parent_register(self) -> ReadableAsyncRegister:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(ReadableAsyncRegister, self.parent)


class FieldAsyncWriteOnly(_FieldWriteOnlyFramework, ABC):
    """
    class for an asynchronous write only register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def __init__(self,
                 parent_register: WritableAsyncRegister,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, (RegAsyncReadWrite, RegAsyncWriteOnly)):
            raise TypeError(f'size_props must be of {type(RegAsyncReadWrite)} or '
                            f'{type(RegAsyncWriteOnly)} but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)

    async def write(self, value: int) -> None: # pylint: disable=invalid-overridden-method
        """
        The behaviour of this method depends on whether the field is located in
        a readable register or not:

        If the register is readable, the method will perform an async read-modify-write
        on the register updating the field with the value provided

        If the register is not writable all other field values will be asynchronously written
        with zero.

        Args:
            value: field value to update to

        """

        if not isinstance(value, int):
            raise TypeError(f'value must be an int but got {type(value)}')

        if value < 0:
            raise ValueError('value to be written to register must be greater '
                             'than or equal to 0')

        if value > self.max_value:
            raise ValueError(f'value to be written to register must be less '
                             f'than or equal to {self.max_value:d}')

        if self.msb0:
            value = swap_msb_lsb_ordering(value=value, width=self.width)

        if (self.high == (self.register_data_width - 1)) and (self.low == 0):
            # special case where the field occupies the whole register,
            # there a straight write can be performed
            new_reg_value = value
        else:
            # do a read, modify write
            if isinstance(self.parent_register, RegAsyncReadWrite):
                reg_value = await self.parent_register.read()
                masked_reg_value = reg_value & self.inverse_bitmask
                new_reg_value = masked_reg_value | (value << self.low)
            elif isinstance(self.parent_register, RegAsyncWriteOnly):
                new_reg_value = value << self.low
            else:
                raise TypeError('Unhandled parent type')

        await self.parent_register.write(new_reg_value)

    @property
    def parent_register(self) -> WritableAsyncRegister:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(WritableAsyncRegister, self.parent)


class FieldAsyncReadWrite(FieldAsyncReadOnly, FieldAsyncWriteOnly, ABC):
    """
    class for an asyncronous read/write register field

    Args:
        parent_register: register within which the field resides
        size_props: object defining the msb, lsb, high bit, low bit and width
        logger_handle: name to be used logging messages associate with this
            object

    """
    __slots__ : List[str] = []

    def __init__(self, parent_register: RegAsyncReadWrite,
                 size_props: FieldSizeProps,
                 misc_props: FieldMiscProps,
                 logger_handle: str,
                 inst_name: str):

        if not isinstance(parent_register, RegAsyncReadWrite):
            raise TypeError(f'size_props must be of {type(RegAsyncReadWrite)} '
                            f'but got {type(parent_register)}')

        super().__init__(logger_handle=logger_handle,
                         size_props=size_props,
                         misc_props=misc_props,
                         parent_register=parent_register,
                         inst_name=inst_name)

    @property
    def parent_register(self) -> RegAsyncReadWrite:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(RegAsyncReadWrite, self.parent)


class FieldEnum(Field, ABC):
    """
    class for a register field with an enumerated value
    """
    __slots__: List[str] = []

    @property
    @abstractmethod
    def enum_cls(self):
        """
        The enumeration class for this field
        """


class FieldEnumReadWrite(FieldReadWrite, FieldEnum, ABC):
    """
    class for a read/write register field with an enumerated value
    """
    __slots__: List[str] = []

    @property
    def parent_register(self) -> RegReadWrite:
        """
        parent register the field is placed in
        """

        # this cast is OK because an explict typing check was done in the __init__
        return cast(RegReadWrite, self.parent)


class FieldEnumReadOnly(FieldReadOnly, FieldEnum, ABC):
    """
    class for a read only register field with an enumerated value
    """
    __slots__: List[str] = []


class FieldEnumWriteOnly(FieldWriteOnly, FieldEnum, ABC):
    """
    class for a write only register field with an enumerated value
    """
    __slots__: List[str] = []


class FieldEnumAsyncReadWrite(FieldAsyncReadWrite, FieldEnum, ABC):
    """
    class for an async read/write register field with an enumerated value
    """
    __slots__: List[str] = []

class FieldEnumAsyncReadOnly(FieldAsyncReadOnly, FieldEnum, ABC):
    """
    class for an async read only register field with an enumerated value
    """
    __slots__: List[str] = []

class FieldEnumAsyncWriteOnly(FieldAsyncWriteOnly, FieldEnum, ABC):
    """
    class for an async write only register field with an enumerated value
    """
    __slots__: List[str] = []
