from __future__ import annotations

from abc import ABC, abstractmethod


class RestaurantDomainUseCase(ABC):
    @abstractmethod
    def get_detail(self, *args, **kwargs):
        pass

    @abstractmethod
    def list_category_page(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_card_dict(self, *args, **kwargs):
        pass

