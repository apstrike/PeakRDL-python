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

This package is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of classes used by the autogenerated code
"""

from .callbacks import ReadCallback
from .callbacks import ReadBlockCallback
from .callbacks import WriteCallback
from .callbacks import WriteBlockCallback
from .callbacks import NormalCallbackSet,NormalCallbackSetLegacy
from .callbacks import AsyncCallbackSet,AsyncCallbackSetLegacy
from .callbacks import CallbackSet

from .base import AddressMap
from .base import RegFile
from .base import AddressMapArray
from .base import RegFileArray

from .base import AsyncAddressMap
from .base import AsyncRegFile
from .base import AsyncAddressMapArray
from .base import AsyncRegFileArray

from .register import Reg
from .register import RegArray
from .register import RegisterWriteVerifyError

from .register import RegReadOnly
from .register import RegWriteOnly
from .register import RegReadWrite
from .register import WritableRegister
from .register import ReadableRegister

from .register import RegReadOnlyArray
from .register import RegWriteOnlyArray
from .register import RegReadWriteArray
from .register import ReadableRegisterArray
from .register import WriteableRegisterArray

from .async_register import AsyncReg
from .async_register import AsyncRegArray
from .async_register import RegAsyncReadOnly
from .async_register import RegAsyncWriteOnly
from .async_register import RegAsyncReadWrite
from .async_register import ReadableAsyncRegister
from .async_register import WritableAsyncRegister
from .async_register import RegAsyncReadOnlyArray
from .async_register import RegAsyncWriteOnlyArray
from .async_register import RegAsyncReadWriteArray
from .async_register import ReadableAsyncRegisterArray
from .async_register import WriteableAsyncRegisterArray

from .fields import FieldSizeProps
from .fields import FieldMiscProps
from .fields import FieldReadOnly
from .fields import FieldWriteOnly
from .fields import FieldReadWrite
from .fields import Field
from .fields import FieldEnumReadOnly
from .fields import FieldEnumWriteOnly
from .fields import FieldEnumReadWrite
from .fields import FieldEnum

from .fields import FieldAsyncReadOnly
from .fields import FieldAsyncWriteOnly
from .fields import FieldAsyncReadWrite
from .fields import FieldEnumAsyncReadOnly
from .fields import FieldEnumAsyncWriteOnly
from .fields import FieldEnumAsyncReadWrite

from .memory import MemoryReadOnly, MemoryReadOnlyLegacy
from .memory import MemoryWriteOnly, MemoryWriteOnlyLegacy
from .memory import MemoryReadWrite, MemoryReadWriteLegacy
from .memory import MemoryReadOnlyArray
from .memory import MemoryWriteOnlyArray
from .memory import MemoryReadWriteArray
from .memory import MemoryAsyncReadOnly, MemoryAsyncReadOnly
from .memory import MemoryAsyncWriteOnly, MemoryAsyncWriteOnly
from .memory import MemoryAsyncReadWrite, MemoryAsyncReadWrite
from .memory import MemoryAsyncReadOnlyArray
from .memory import MemoryAsyncWriteOnlyArray
from .memory import MemoryAsyncReadWriteArray
from .memory import ReadableMemory, ReadableMemoryLegacy
from .memory import WritableMemory, WritableMemoryLegacy
from .memory import Memory
from .memory import ReadableAsyncMemory, ReadableAsyncMemoryLegacy
from .memory import WritableAsyncMemory, ReadableAsyncMemoryLegacy
from .memory import AsyncMemory
from .memory import MemoryArray
from .memory import AsyncMemoryArray

from .utility_functions import get_array_typecode
from .base import Node
