"""
Shoplytics: Orders API Router
Handles order lookups, paginated listings, order status filtering, and recent orders.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import OrderResponse, PaginatedResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get(
    "",
    response_model=PaginatedResponse[OrderResponse],
    summary="List Orders",
    description="Retrieve paginated orders with optional order status filtering."
)
def list_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. delivered, shipped, canceled)"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_orders(
        db=db,
        page=page,
        page_size=page_size,
        status=status
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
    "/recent",
    response_model=List[OrderResponse],
    summary="Get Recent Orders",
    description="Retrieve most recent orders based on order purchase timestamp."
)
def get_recent_orders(
    limit: int = Query(10, ge=1, le=100, description="Number of recent orders to return"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_recent_orders(db, limit=limit)


@router.get(
    "/status/{status}",
    response_model=PaginatedResponse[OrderResponse],
    summary="Get Orders by Status",
    description="Retrieve paginated orders for a specific order status."
)
def get_orders_by_status(
    status: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_orders(
        db=db,
        page=page,
        page_size=page_size,
        status=status
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
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get Order by ID",
    description="Retrieve order lifecycle timestamps and delivery details by order ID."
)
def get_order_by_id(
    order_id: str,
    db: Session = Depends(get_db)
):
    ord_record = AnalyticsService.get_order_by_id(db, order_id)
    if not ord_record:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return ord_record
