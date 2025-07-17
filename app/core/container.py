from typing import Dict, Type, TypeVar, Callable, Any, Union
import asyncio

T = TypeVar('T')


class Container:
    """Dependency injection container"""

    def __init__(self):
        self._services: Dict[Type, Union[Callable[[], Any], Callable[[], Any]]] = {}
        self._async_services: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type[T], implementation: Callable[[], T], singleton: bool = False):
        """Register service implementation"""
        self._services[interface] = implementation
        if singleton:
            self._singletons[interface] = None

    def register_async(self, interface: Type[T], implementation: Callable[[], T], singleton: bool = False):
        """Register async service implementation"""
        self._async_services[interface] = implementation
        if singleton:
            self._singletons[interface] = None

    def resolve(self, interface: Type[T]) -> T:
        """Resolve service instance"""
        if interface in self._singletons:
            if self._singletons[interface] is None:
                if interface in self._async_services:
                    # For async services, we need to handle this differently
                    # This is a limitation - async services should be resolved in async context
                    raise ValueError(f"Async service {interface} cannot be resolved synchronously")
                self._singletons[interface] = self._services[interface]()
            return self._singletons[interface]

        if interface in self._async_services:
            raise ValueError(f"Async service {interface} cannot be resolved synchronously")

        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")

        return self._services[interface]()

    async def resolve_async(self, interface: Type[T]) -> T:
        """Resolve async service instance"""
        if interface in self._singletons:
            if self._singletons[interface] is None:
                if interface in self._async_services:
                    self._singletons[interface] = await self._async_services[interface]()
                else:
                    self._singletons[interface] = self._services[interface]()
            return self._singletons[interface]

        if interface in self._async_services:
            return await self._async_services[interface]()

        if interface not in self._services:
            raise ValueError(f"Service {interface} not registered")

        return self._services[interface]()

    def register_instance(self, interface: Type[T], instance: T):
        """Register service instance"""
        self._singletons[interface] = instance


# Global container instance
_container = Container()


def get_container() -> Container:
    """Get global container instance"""
    return _container


def register_service(interface: Type[T], implementation: Callable[[], T], singleton: bool = False):
    """Register service in global container"""
    _container.register(interface, implementation, singleton)


def register_async_service(interface: Type[T], implementation: Callable[[], T], singleton: bool = False):
    """Register async service in global container"""
    _container.register_async(interface, implementation, singleton)


def resolve_service(interface: Type[T]) -> T:
    """Resolve service from global container"""
    return _container.resolve(interface)


async def resolve_async_service(interface: Type[T]) -> T:
    """Resolve async service from global container"""
    return await _container.resolve_async(interface)
