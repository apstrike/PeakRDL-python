"""
This module is intended to distributed as part of automatically generated code by the PeakRDL
Python tool. It provides a set of base classes used by the autogenerated code
"""
from __future__ import annotations
import logging
from typing import Dict, List, Optional, Tuple, Union, Iterator, TYPE_CHECKING, Type, \
    overload, TypeVar, Sequence, cast
from abc import ABC, abstractmethod

from .callbacks import CallbackSet

if TYPE_CHECKING:
    from .memory import Memory


class Base(ABC):
    """
    base class of for all types
    """
    __slots__: List[str] = ['__logger', '__inst_name', '__parent']

    def __init__(self, logger_handle: str, inst_name: str, parent: Optional[Base]):
        self.__logger = logging.getLogger(logger_handle)
        self._logger.debug('creating instance of %s', self.__class__)

        self.__inst_name = inst_name
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
    def parent(self) -> Optional[Base]:
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

    __slots__ = ['__address', '__callbacks']

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional[Base]):
        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        self.__address = address
        self.__callbacks = callbacks

    @property
    def address(self) -> int:
        """
        address of the node
        """
        return self.__address

    @property
    def _callbacks(self) -> CallbackSet:
        return self.__callbacks

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


# pylint: disable-next=invalid-name
NodeArrayElementType = TypeVar('NodeArrayElementType', bound=Node)


class NodeArray(Base, Sequence[Union[NodeArrayElementType, Sequence[NodeArrayElementType]]]):
    """
    base class of for all array types
    """

    # pylint: disable=too-few-public-methods
    __slots__: List[str] = ['__elements', '__address', '__callbacks',
                            '__stride', '__dimensions' ]

    # pylint: disable-next=too-many-arguments
    def __init__(self, logger_handle: str,
                 inst_name: str,
                 parent: Node,
                 callbacks: CallbackSet,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name, parent=parent)

        if not isinstance(address, int):
            raise TypeError(f'address should be a int but got {type(dimensions)}')
        self.__address = address
        self.__callbacks = callbacks
        if not isinstance(stride, int):
            raise TypeError(f'stride should be a int but got {type(dimensions)}')
        self.__stride = stride

        if not isinstance(dimensions, tuple):
            raise TypeError(f'dimensions should be a tuple but got {type(dimensions)}')
        for dimension in dimensions:
            if not isinstance(dimension, int):
                raise TypeError(f'dimension should be a int but got {type(dimension)}')
        self.__dimensions = dimensions

        self.__elements: Tuple[Union[NodeArrayElementType, NodeArray[NodeArrayElementType]], ...]

        if len(dimensions) > 1:
            inner_size = stride
            for dimension in dimensions[1:]:
                if not isinstance(dimension, int):
                    raise TypeError(f'dimension should be a int but got {type(dimension)}')
                inner_size *= dimension
            self.__elements = tuple(
                self.__class__(logger_handle=logger_handle + '[' + str(index) + ']',
                               parent=parent,
                               callbacks=callbacks,
                               dimensions=dimensions[1:],
                               address=address + (index * inner_size),
                               stride=stride,
                               inst_name=inst_name + '[' + str(index) + ']')
                for index in range(dimensions[0]))
        else:
            self.__elements = tuple(
                self._element_datatype(logger_handle=logger_handle + '[' + str(index) + ']',
                                       callbacks=self._callbacks,
                                       address=address + (index * stride),
                                       inst_name=inst_name + '[' + str(index) + ']',
                                       parent=self.parent)
                         for index in range(dimensions[0]))


    @overload
    def __getitem__(self, item: int) -> NodeArrayElementType:
        ...

    @overload
    def __getitem__(self, item: slice) -> Tuple[NodeArrayElementType, ...]:
        ...

    @overload
    def __getitem__(self, item: Tuple[int, ...]) -> Tuple[NodeArrayElementType, ...]:
        ...

    @overload
    def __getitem__(self, item: Tuple[Union[int, slice], ...]) -> Tuple[NodeArrayElementType , ...]:
        ...

    def __getitem__(self, item):  # type: ignore[no-untyped-def]
        if len(self.dimensions) > 1:
            if isinstance(item, tuple):
                if len(item) != len(self.dimensions):
                    raise ValueError('When using a multidimensional access, the size must match the'
                                     ' dimensions of the array, array dimensions '
                                     f'are {len(self.dimensions)}')

                return_data = self.__elements[item[0]]
                for index in item[1:]:
                    return_data = return_data[index]
                return return_data

        if isinstance(item, tuple):
            raise TypeError('attempting a multidimensional arrya access on a single dimension'
                             ' array')

        if not isinstance(item, (tuple, int)):
            raise TypeError(f'Array index must either being an int or a slice, got {type(item)}')

        return self.__elements[item]

    def __len__(self) -> int:
        return len(self.__elements)

    def __iter__(self) -> Iterator[Union[NodeArrayElementType, Sequence[NodeArrayElementType]]]:
        return cast(Iterator[Union[NodeArrayElementType, Sequence[NodeArrayElementType]]],
                    self.__elements.__iter__())

    @property
    def dimensions(self) -> Tuple[int, ...]:
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
        return self.__callbacks




class AddressMap(Node, ABC):
    """
    base class of address map wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Optional['AddressMap']):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union[Union['AddressMap', RegFile],
                           Tuple[Union['AddressMap', RegFile], ...]]]:
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


class AddressMapArray(NodeArray, ABC):
    """
    base class for a array of address maps
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, logger_handle: str, inst_name: str,
                 parent: AddressMap,
                 callbacks: CallbackSet,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, callbacks=callbacks, address=address,
                         stride=stride, dimensions=dimensions)


class RegFile(Node, ABC):
    """
    base class of register file wrappers

    Note:
        It is not expected that this class will be instantiated under normal
        circumstances however, it is useful for type checking
    """

    __slots__: List[str] = []

    def __init__(self,
                 callbacks: CallbackSet,
                 address: int,
                 logger_handle: str,
                 inst_name: str,
                 parent: Union[AddressMap, 'RegFile']):

        super().__init__(callbacks=callbacks,
                         address=address,
                         logger_handle=logger_handle,
                         inst_name=inst_name,
                         parent=parent)

    @abstractmethod
    def get_sections(self, unroll: bool = False) -> \
            Iterator[Union['RegFile', Tuple['RegFile', ...]]]:
        """
        generator that produces all the RegFile children of this node

        Args:
            unroll: Whether to unroll child array or not

        Returns:

        """


class RegFileArray(NodeArray, ABC):
    """
    base class for a array of register files
    """
    __slots__: List[str] = []

    # pylint: disable-next=too-many-arguments
    def __init__(self, logger_handle: str, inst_name: str,
                 parent: Union[AddressMap, RegFile],
                 callbacks: CallbackSet,
                 address: int,
                 stride: int,
                 dimensions: Tuple[int, ...]):

        super().__init__(logger_handle=logger_handle, inst_name=inst_name,
                         parent=parent, callbacks=callbacks, address=address,
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
