from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class MovieBase(BaseModel):
    id: int
    name: str
    date: date
    score: float
    genre: str


class MovieListResponseSchema(MovieBase):
    pass

    class Config:
        from_attributes = True


class MovieDetailResponseSchema(MovieBase):
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str

    class Config:
        from_attributes = True


class PaginatedMoviesResponseSchema(BaseModel):
    movies: List[MovieListResponseSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    class Config:
        from_attributes = True
