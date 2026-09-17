"""
Shoplytics: Products API Router
Handles product catalog browsing, category filtering, product details, and top sellers.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ProductResponse, TopProductResponse, PaginatedResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary="List Products",
    description="Retrieve paginated product catalog with optional category filtering."
)
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by English category name"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_products(
        db=db,
        page=page,
        page_size=page_size,
        category=category
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "data": records
    }


@router.get(
    "/top",
    response_model=List[TopProductResponse],
    summary="Get Top Products",
    description="Retrieve top selling products ranked by revenue and units sold."
)
def get_top_products(
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_top_products(db, limit=limit)


@router.get(
    "/category/{category}",
    response_model=PaginatedResponse[ProductResponse],
    summary="Get Products by Category",
    description="Retrieve all products belonging to a specified English category name."
)
def get_products_by_category(
    category: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_products(
        db=db,
        page=page,
        page_size=page_size,
        category=category
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "data": records
    }


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get Product by ID",
    description="Retrieve physical attributes and category details for a specific product ID."
)
def get_product_by_id(
    product_id: str,
    db: Session = Depends(get_db)
):
    prod = AnalyticsService.get_product_by_id(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")
    return prod
