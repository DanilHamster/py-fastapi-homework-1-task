from urllib.request import Request

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, MovieModel
from schemas import MovieListResponseSchema, MovieDetailResponseSchema
from schemas.movies import PaginatedMoviesResponseSchema

router = APIRouter()


@router.get("/movies/", response_model=PaginatedMoviesResponseSchema)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> PaginatedMoviesResponseSchema:
    count_result = await db.execute(
        select(func.count()).select_from(MovieModel)
    )
    count = count_result.scalar()
    if count == 0:
        raise HTTPException(status_code=404, detail="No movies found.")

    page_count = (count + per_page - 1) // per_page
    if page > page_count:
        raise HTTPException(status_code=404, detail="No movies found.")

    result = await db.execute(
        select(MovieModel)
        .order_by(MovieModel.id.asc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    raw_movies = result.scalars().all()
    movies = [MovieListResponseSchema.model_validate(m) for m in raw_movies]

    prev_page = None if page == 1 else f"/theater/movies/?page={page - 1}&per_page={per_page}"
    next_page = None if page == page_count else f"/theater/movies/?page={page + 1}&per_page={per_page}"

    return PaginatedMoviesResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=page_count,
        total_items=count,
    )


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie_id(
    movie_id: int, db: AsyncSession = Depends(get_db)
) -> MovieDetailResponseSchema:
    result = await db.execute(
        select(MovieModel).where(MovieModel.id == movie_id)
    )
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return movie
