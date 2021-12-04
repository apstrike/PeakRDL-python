"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of types used by the autogenerated code to callbacks
"""
import sys

from array import array as Array

from typing import Optional

if sys.version_info >= (3, 8):
    # Python 3.8 introduced the Protocol class to the typing module which is more powerful than the
    # previous method because it also check the argument names

    from typing import Protocol

    class ReadCallback(Protocol):
        """
        Callback definition for a single register read operation
        """
        def __call__(self, addr: int, width: int, accesswidth: int) -> int:
            pass


    class WriteCallback(Protocol):
        """
        Callback definition for a single register write operation
        """
        def __call__(self, addr: int, width: int, accesswidth: int, data: int) -> None:
            pass


    class ReadBlockCallback(Protocol):
        """
        Callback definition for a block read operation
        """
        def __call__(self, addr: int, width: int, accesswidth: int, length: int) -> Array:
            pass


    class WriteBlockCallback(Protocol):
        """
        Callback definition for a block write operation
        """
        def __call__(self, addr: int, width: int, accesswidth: int, data: Array) -> None:
            pass
else:
    from typing import Callable

    ReadCallback = Callable[[int, int, int], int]
    WriteCallback = Callable[[int, int, int, int], None]
    ReadBlockCallback = Callable[[int, int, int, int], Array]
    WriteBlockCallback = Callable[[int, int, int, Array], None]


class CallbackSet:
    """
    Class to hold a set of callbacks, this reduces the number of callback that need to be passed
    around
    """

    __slots__ = ['__write_callback', '__read_callback',
                 '__write_block_callback', '__read_block_callback']

    def __init__(self,
                 write_callback: Optional[WriteCallback] = None,
                 read_callback: Optional[ReadCallback] = None,
                 write_block_callback: Optional[WriteBlockCallback] = None,
                 read_block_callback: Optional[ReadBlockCallback] = None):

        self.__read_callback = read_callback
        self.__read_block_callback = read_block_callback
        self.__write_callback = write_callback
        self.__write_block_callback = write_block_callback

    @property
    def read_callback(self) -> Optional[ReadCallback]:
        """
        single read callback function

        Returns: call back function

        """
        return self.__read_callback

    @property
    def write_callback(self) -> Optional[WriteCallback]:
        """
        single write callback function

        Returns: call back function

        """
        return self.__write_callback

    @property
    def read_block_callback(self) -> Optional[ReadBlockCallback]:
        """
        block read callback function

        Returns: call back function

        """
        return self.__read_block_callback

    @property
    def write_block_callback(self) -> Optional[WriteBlockCallback]:
        """
        block read callback function

        Returns: call back function

        """
        return self.__write_block_callback
