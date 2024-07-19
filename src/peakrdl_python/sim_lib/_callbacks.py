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
peakrdl-python tool.  It provides a set of types used by the autogenerated code to callbacks
"""

import sys

if sys.version_info >= (3, 8):
    # Python 3.8 introduced the Protocol class to the typing module which is more powerful than the
    # previous method because it also check the argument names

    from typing import Protocol

    class RegisterReadCallback(Protocol):
        """
        Callback definition software read to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, value: int) -> None:
            pass


    class RegisterWriteCallback(Protocol):
        """
        Callback definition software write to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, value: int) -> None:
            pass

    class FieldReadCallback(Protocol):
        """
        Callback definition software read to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, value: int) -> None:
            pass


    class FieldWriteCallback(Protocol):
        """
        Callback definition software write to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, value: int) -> None:
            pass

    class MemoryReadCallback(Protocol):
        """
        Callback definition software read to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, offset: int, value: int) -> None:
            pass


    class MemoryWriteCallback(Protocol):
        """
        Callback definition software write to a field, register or memory
        """

        # pylint: disable=too-few-public-methods
        def __call__(self, offset: int, value: int) -> None:
            pass

else:
    from typing import Callable

    RegisterReadCallback = Callable[[int], None]
    RegisterWriteCallback = Callable[[int], None]
    FieldReadCallback = Callable[[int], None]
    FieldWriteCallback = Callable[[int], None]
    MemoryReadCallback = Callable[[int], None]
    MemoryWriteCallback = Callable[[int], None]
