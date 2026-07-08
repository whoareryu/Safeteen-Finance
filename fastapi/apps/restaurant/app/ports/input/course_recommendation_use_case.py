from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.app.dtos.course_recommendation_dto import CourseQuery, CourseView


class CourseRecommendationUseCase(ABC):
    """지역 입력 → 브런치→점심→카페→저녁→술집 하루 코스 (기획서 3-4)."""

    @abstractmethod
    def recommend(self, db: Session, query: CourseQuery) -> CourseView:
        ...
