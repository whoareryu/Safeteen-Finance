from __future__ import annotations

from abc import ABC, abstractmethod


class RestaurantDetailRepository(ABC):
    @abstractmethod
    def get_detail(self, *args, **kwargs):
        pass

    @abstractmethod
    def exists(self, *args, **kwargs):
        pass

    @abstractmethod
    def display_name(self, *args, **kwargs):
        pass

