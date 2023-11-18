"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of base classes used by the autogenerated code
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional, Tuple, Union, Iterator, TYPE_CHECKING, Type, TypeVar,\
    Sequence, cast
from abc import ABC, abstractmethod
from itertools import product
from functools import reduce
from operator import mul

from .callbacks import CallbackSet, NormalCallbackSet, AsyncCallbackSet

if TYPE_CHECKING:
    from .memory import Memory
    from .register import WritableRegister, ReadableRegister
    from .register import ReadableAsyncRegister, WritableAsyncRegister
    from .register import ReadableRegisterArray, WriteableRegisterArray
    from .register import ReadableAsyncRegisterArray, WriteableAsyncRegisterArray


class Base(ABC):
    """
    base class of for all types
    """
    __slots__: List[str] = ['__logger', '__inst_name', '__parent']

    def __init__(self, *,
                 logger_handle: str, inst_name: str, parent: Optional['Node']):

        if not isinstance(logger_handle, str):
            raise TypeError(f'logger_handle should be str but got {type(logger_handle)}')

        self.__logger = logging.getLogger(logger_handle)
        self._logger.debug('creating instance of %s', self.__class__)

        if not isinstance(inst_name, str):
            raise TypeError(f'inst_name should be str but got {type(inst_name)}')
        self.__inst_name = inst_name

        if parent is not None:
            if not isinstance(parent, Node):
                raise TypeError(f'parent should be Node but got {type(parent)}')
        self.__parent = parent

    @property
    def _logger(self) -> logging.Logger:
        return self.__logger

    @property
    def inst_name(self) -> str:
        """
        systemRDL name of the instance in the parent
        """
        return self.__inst_name

    @property
    def parent(self) -> Optional['Node']:
        """
        parent of the node or field, or None if it has no parent
        """
        return self.__parent

    @property
    def full_inst_name(self) -> str:
        """
        The full hierarchical systemRDL name of the instance
        """
        if self.parent is not None:
            return self.parent.full_inst_name + "." + self.inst_name

        return self.inst_name


class Node(Base, ABC):
    """
    base class of for all types with an address i.e. not fields

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__ = ['__address']

    def __init__(self, *,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['Node']):
        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        if not isinstance(address, int):
            raise TypeError(f'address should be int but got {type(address)}')

        self.__address = address

    @property
    def address(self) -> int:
        """
        address of the node
        """
        return self.__address

    @property
    @abstractmethod
    def _callbacks(self) -> CallbackSet:
        ...

    @property
    @abstractmethod
    def systemrdl_python_child_name_map(self) -> Dict[str, str]:
        """
        In some cases systemRDL names need to be converted make them python safe, this dictionary
        is used to map the original systemRDL names to the names of the python attributes of this
        class

        Returns: dictionary whose key is the systemRDL names and value it the property name
        """

    def get_child_by_system_rdl_name(self, name: str) -> Base:
        """
        returns a child node by its systemRDL name

        Args:
            name: name of the node in the systemRDL

        Returns: Node

        """
        return getattr(self, self.systemrdl_python_child_name_map[name])

    @property
    @abstractmethod
    def size(self) -> int:
        """
        Total Number of bytes of address the node occupies
        """


# pylint: disable-next=invalid-name
NodeArrayElementType = TypeVar('NodeArrayElementType', bound=Node)


class NodeArray(Base, Sequence[NodeArrayElementType]):
    """
    base class of for all array types
    """

    # pylint: disable=too-few-public-methods
    __slots__: List[str] = ['__elements', '__address',
                            '__stride', '__dimensions' ]

    # pylint: disable-next=too-many-arguments
    def __init__(self, *, logger_handle: str,
                 inst_name: str,
                 parent: Node,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...],
                 elements: Optional[Dict[Tuple[int, ...], NodeArrayElementType]] = None):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        if not isinstance(address, int):
            raise TypeError(f'address should be a int but got {type(dimensions)}')
        self.__address = address
        if not isinstance(stride, int):
            raise TypeError(f'stride should be a int but got {type(dimensions)}')
        self.__stride = stride

        if not isinstance(dimensions, tuple):
            raise TypeError(f'dimensions should be a tuple but got {type(dimensions)}')
        for dimension in dimensions:
            if not isinstance(dimension, int):
                raise TypeError(f'dimension should be a int but got {type(dimension)}')
        self.__dimensions = dimensions

        # There are two use cases for this class:
        # 1. Initial creation - elements is None in which case the data is populated
        # 2. Creating a recursive version of itself, this happens when it is sliced by the parent
        #    in which case a subset of the elements is presented and a new instance

        if elements is not None:
            self.__check_init_element(elements)
            self.__elements = elements
        else:
            new_elements: Dict[Tuple[int, ...], NodeArrayElementType] = {}
            for indices in product(*[range(dim) for dim in self.dimensions]):
                new_elements[indices] = self._element_datatype(
                    logger_handle=logger_handle +
                                  '[' + ','.join([str(item) for item in indices]) + ']',
                    address=self.__address_calculator(indices),
                    inst_name=inst_name + '[' + ']['.join([str(item) for item in indices]) + ']',
                    parent=self.parent)

            self.__elements = new_elements

    def __check_init_element(self, elements:Dict[Tuple[int, ...], NodeArrayElementType]) -> None:
        """
        Used in the __init__ to check that the elements passed in are valid
        Args:
            elements: proposed element of the array

        Returns:

        """
        if not isinstance(elements, dict):
            raise TypeError(f'elements should be a dictionary but got {type(elements)}')

        for index, item in elements.items():
            if not isinstance(index, tuple):
                raise TypeError(f'element index should be a tuple but got {type(index)}')

            if len(index) != len(self.dimensions):
                raise ValueError(f'size of index does not match index length = {len(index)}')

            for index_pos, index_item in enumerate(index):
                if not isinstance(index_item, int):
                    raise TypeError(f'element index_item should be a int '
                                    f'but got {type(index_item)}')

                if not 0 <= index_item < self.dimensions[index_pos]:
                    raise ValueError('index outside of range of dimensions')

            if not isinstance(item, self._element_datatype):
                raise TypeError(f'elements should be a {self._element_datatype} '
                                f'but got {type(item)}')

    def __address_calculator(self, indices: Tuple[int, ...]) -> int:
        def cal_addr(dimensions: Tuple[int,...], indices: Tuple[int, ...], base_address: int,
                     stride: int) -> int:
            """
            Calculates the address of an register within an array

            :param dimensions: list of the array dimensions
            :param indices: list of the array indices (length must match the dimensions)
            :param base_address: base address of the array
            :param stride: address stride of of the array
            :return: address of the register
            """
            if len(dimensions) == 1:
                return (indices[0] * stride) + base_address

            outer_offset = reduce(mul, dimensions[1::], 1) * stride * indices[0]
            return outer_offset + cal_addr(dimensions=dimensions[1::],
                                           indices=indices[1::],
                                           stride=self.stride,
                                           base_address=self.address)

        return cal_addr(self.dimensions, base_address=self.address,
                        stride=self.stride, indices=indices)

    def __getitem__(self, item):  # type: ignore[no-untyped-def]
        if len(self.dimensions) > 1:
            return self.__getitem_nd(item)

        if isinstance(item, tuple):
            raise IndexError('attempting a multidimensional array access on a single dimension'
                             ' array')

        if isinstance(item, slice):

            valid_items = [(i,) for i in range(*item.indices(self.dimensions[0]))]
            def filter_1d_func(to_filter:Tuple[Tuple[int, ...], NodeArrayElementType]) -> bool:
                index, _ = to_filter
                if index in valid_items:
                    return True
                return False

            return self.__class__(logger_handle=self._logger.name,
                                  inst_name=self.inst_name,
                                  parent=self.parent,
                                  address=self.address,
                                  stride=self.stride,
                                  dimensions=self.dimensions,
                                  elements=dict(filter(filter_1d_func, self.items())))

        if isinstance(item, int):
            if (item, ) not in self.__elements:
                raise IndexError(f'{item:d} in in the array')
            return self.__elements[(item, )]

        raise TypeError(f'Array index must either being an int or a slice, got {type(item)}')

    def __getitem_nd(self, item): # type: ignore[no-untyped-def]

        if isinstance(item, tuple):

            if len(item) != len(self.dimensions):
                raise ValueError('When using a multidimensional access, the size must match the'
                                 ' dimensions of the array, array dimensions '
                                 f'are {len(self.dimensions)}')

            if all(isinstance(i, int) for i in item):
                # single item access
                if item not in self.__elements:
                    msg = 'index[' + ','.join([str(i) for i in item]) + '] not in array'
                    raise IndexError(msg)
                return self.__elements[item]

            unpack_index_set = []
            for axis, sub_index in enumerate(item):
                if isinstance(sub_index, int):
                    if not 0 <= sub_index < self.dimensions[axis]:
                        raise IndexError(f'{sub_index:d} out of range for dimension {axis}')
                    unpack_index_set.append((sub_index,))
                    continue

                if isinstance(sub_index, slice):
                    unpack_index_set.append(range(*sub_index.indices(self.dimensions[axis])))
                    continue

                raise TypeError(f'unhandle index of {type(sub_index)} in position {axis:d}')

            valid_items = tuple(product(*unpack_index_set))

            def filter_nd_func(to_filter: Tuple[Tuple[int, ...], NodeArrayElementType]) -> bool:
                index, _ = to_filter
                if index in valid_items:
                    return True
                return False

            return self.__class__(logger_handle=self._logger.name,
                                  inst_name=self.inst_name,
                                  parent=self.parent,
                                  address=self.address,
                                  stride=self.stride,
                                  dimensions=self.dimensions,
                                  elements=dict(filter(filter_nd_func, self.items())))

        raise IndexError('attempting a signledimensional array access on a multidimension'
                         ' array')

    def __len__(self) -> int:
        return len(self.__elements)

    def __iter__(self) -> Iterator[NodeArrayElementType]:

        for item in self.__elements.values():
            yield item

    def items(self) -> Iterator[Tuple[Tuple[int, ...], NodeArrayElementType]]:
        """
        iterate through all the items in an array but also return the index of the array
        """
        for index, item in self.__elements.items():
            yield  index, item

    @property
    def dimensions(self) -> Union[Tuple[int, ...], Tuple[int]]:
        """
        Dimensions of the array
        """
        return self.__dimensions

    @property
    @abstractmethod
    def _element_datatype(self) -> Type[NodeArrayElementType]:
        ...

    @property
    def address(self) -> int:
        """
        address of the node
        """
        return self.__address

    @property
    def stride(self) -> int:
        """
        address stride of the array
        """
        return self.__stride

    @property
    def _callbacks(self) -> CallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # pylint: disable-next=protected-access
        return self.parent._callbacks

    @property
    def size(self) -> int:
        """
        Total Number of bytes of address the array occupies
        """
        return reduce(mul, self.dimensions, 1) * self.stride



class BaseAddressMap(Node, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__callbacks']

    def __init__(self, *,
                 callbacks: Optional[CallbackSet],
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['AddressMap']):



        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @property
    def _callbacks(self) -> NormalCallbackSet:
        if self.parent is None:
            return self.__callbacks
        # pylint: disable-next=protected-access
        return self.parent._callbacks


class AddressMap(BaseAddressMap, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """
    def __init__(self, *,
                 callbacks: Optional[NormalCallbackSet],
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['AddressMap']):

        # only the top-level address map should have callbacks assigned, everything else should
        # use its parent callback
        if parent is None:
            if not isinstance(callbacks, NormalCallbackSet):
                raise TypeError(f'callback type wrong, got {type(callbacks)}')
            self.__callbacks = callbacks
        else:
            if not callbacks is None:
                raise RuntimeError('Callbacks must be None when a parent is set')

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union['AddressMap', RegFile, AddressMapArray, RegFileArray]]:
        """
        generator that produces all the AddressMap and RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @abstractmethod
    def get_memories(self, unroll: bool = False) -> \
            Iterator[Union['Memory', Tuple['Memory', ...]]]:
        """
        generator that produces all the Memory children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @abstractmethod
    def get_writable_registers(self, unroll:bool=False) -> \
            Iterator[Union[WritableRegister, WriteableRegisterArray]]:
        """
        generator that produces all the readable_registers of this node
        """
    
    @abstractmethod
    def get_readable_registers(self, unroll:bool=False) ->\
            Iterator[Union[ReadableRegister, ReadableRegisterArray]]:
        """
        generator that produces all the readable_registers of this node
        """

    @property
    def _callbacks(self) -> NormalCallbackSet:
        return cast(NormalCallbackSet, super()._callbacks)

    def size(self) -> int:
        raise NotImplementedError('To go in the next phase')

class AsyncAddressMap(BaseAddressMap, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = ['__callbacks']

    def __init__(self, *,
                 callbacks: Optional[AsyncCallbackSet],
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['AddressMap']):

        # only the top-level address map should have callbacks assigned, everything else should
        # use its parent callback
        if parent is None:
            if not isinstance(callbacks, AsyncCallbackSet):
                raise TypeError(f'callback type wrong, got {type(callbacks)}')
            self.__callbacks = callbacks
        else:
            if not callbacks is None:
                raise RuntimeError('Callbacks must be None when a parent is set')

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union['AsyncAddressMap', AsyncRegFile, AsyncAddressMapArray, AsyncRegFileArray]]:
        """
        generator that produces all the AddressMap and RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @abstractmethod
    def get_memories(self, unroll: bool = False) -> \
            Iterator[Union['Memory', Tuple['Memory', ...]]]:
        """
        generator that produces all the Memory children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @abstractmethod
    def get_writable_registers(self, unroll: bool = False) -> \
            Iterator[Union[WritableAsyncRegister, WriteableAsyncRegisterArray]]:
        """
        generator that produces all the readable_registers of this node
        """

    @abstractmethod
    def get_readable_registers(self, unroll: bool = False) -> \
            Iterator[Union[ReadableAsyncRegister, ReadableAsyncRegisterArray]]:
        """
        generator that produces all the readable_registers of this node
        """

    @property
    def _callbacks(self) -> AsyncCallbackSet:
        return cast(AsyncCallbackSet, super()._callbacks)

    def size(self) -> int:
        raise NotImplementedError('To go in the next phase')


class AddressMapArray(NodeArray, ABC):
    """
    base class for a array of address maps
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)

class AsyncAddressMapArray(NodeArray, ABC):
    """
    base class for a array of address maps
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *, logger_handle: str, inst_name: str,
                 parent: AsyncAddressMap,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)


class RegFile(Node, ABC):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self, *,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'RegFile']):

        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'parent._callbacks type wrong, got {type(parent._callbacks)}')

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union['RegFile', Tuple['RegFile', ...]]]:
        """
        generator that produces all the RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @property
    def _callbacks(self) -> NormalCallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # pylint: disable-next=protected-access
        return cast(NormalCallbackSet, self.parent._callbacks)

    def size(self) -> int:
        raise NotImplementedError('To go in the next phase')


class AsyncRegFile(Node, ABC):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self, *,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'RegFile']):
        super().__init__(address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

        if not isinstance(parent._callbacks, NormalCallbackSet):
            raise TypeError(f'parent._callbacks type wrong, got {type(parent._callbacks)}')

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union['AsyncRegFile', Tuple['AsyncRegFile', ...]]]:
        """
        generator that produces all the RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """

    @property
    def _callbacks(self) -> NormalCallbackSet:
        if self.parent is None:
            raise RuntimeError('Parent must be set')
        # pylint: disable-next=protected-access
        return cast(NormalCallbackSet, self.parent._callbacks)

    def size(self) -> int:
        raise NotImplementedError('To go in the next phase')

class RegFileArray(NodeArray, ABC):
    """
    base class for a array of register files
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)

class AsyncRegFileArray(NodeArray, ABC):
    """
    base class for a array of register files
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, *,
                 logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile],
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, address=address,
                         stride=stride, dimensions=dimensions)


def swap_msb_lsb_ordering(width: int, value: int) -> int:
    """
    swaps the msb/lsb on a integer

    Returns:
        swapped value
    """
    value_to_return = 0
    for bit_positions in zip(range(0, width), range(width-1, -1, -1)):
        bit_value = (value >> bit_positions[0]) & 0x1
        value_to_return |= bit_value << bit_positions[1]

    return value_to_return


def get_array_typecode(width: int) -> str:
    """
        python array typecode

        Args:
            width: in bits

        Returns:
            string to pass into the array generator

        """
    if width == 32:
        return 'L'

    if width == 64:
        return 'Q'

    if width == 16:
        return 'I'

    if width == 8:
        return 'B'

    raise ValueError(f'unhandled width {width:d}')
