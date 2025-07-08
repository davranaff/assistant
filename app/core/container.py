from typing import Dict, Type, TypeVar, Callable, Any
from functools import lru_cache

T = TypeVar('T')


class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._services: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register(self, interface: Type[T], implementation: Callable[[], T], singleton: bool = False):
        """Register service implementation"""
        self._services[interface] = implementation
        if singleton:
            self._singletons[interface] = None
    
    def resolve(self, interface: Type[T]) -> T:
        """Resolve service instance"""
        if interface in self._singletons:
            if self._singletons[interface] is None:
                self._singletons[interface] = self._services[interface]()
            return self._singletons[interface]
        
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


def resolve_service(interface: Type[T]) -> T:
    """Resolve service from global container"""
    return _container.resolve(interface) 