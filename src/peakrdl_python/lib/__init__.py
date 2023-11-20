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
from .callbacks import NormalCallbackSet
from .callbacks import AsyncCallbackSet
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

from .register import RegAsyncReadOnly
from .register import RegAsyncWriteOnly
from .register import RegAsyncReadWrite
from .register import ReadableAsyncRegister
from .register import WritableAsyncRegister
from .register import RegAsyncReadOnlyArray
from .register import RegAsyncWriteOnlyArray
from .register import RegAsyncReadWriteArray
from .register import ReadableAsyncRegisterArray
from .register import WriteableAsyncRegisterArray

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

from .memory import MemoryReadOnly
from .memory import MemoryWriteOnly
from .memory import MemoryReadWrite
from .memory import MemoryReadOnlyArray
from .memory import MemoryWriteOnlyArray
from .memory import MemoryReadWriteArray
from .memory import MemoryAsyncReadOnly
from .memory import MemoryAsyncWriteOnly
from .memory import MemoryAsyncReadWrite
from .memory import MemoryAsyncReadOnlyArray
from .memory import MemoryAsyncWriteOnlyArray
from .memory import MemoryAsyncReadWriteArray
from .memory import ReadableMemory
from .memory import WritableMemory
from .memory import Memory
from .memory import ReadableAsyncMemory
from .memory import WritableAsyncMemory
from .memory import AsyncMemory
from .memory import MemoryArray
from .memory import AsyncMemoryArray

from .base import get_array_typecode
from .base import Node
