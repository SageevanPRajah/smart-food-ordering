from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    user_id: str = Field(..., min_length=1)
    item_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comments: str = Field(..., min_length=3, max_length=500)


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = Field(None, min_length=3, max_length=500)


class ReviewResponse(ReviewBase):
    review_id: str


class ReviewSummary(BaseModel):
    item_id: str
    average_rating: float
    total_reviews: int
