"""
Shoplytics: Sales & Analytics API Router
Provides aggregated analytical endpoints for dashboard charts and visual trends.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import (
    MonthlySalesResponse, CategorySalesResponse,
    TopProductResponse, SellerSalesResponse, OrderStatusCountResponse
)
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/sales", tags=["Sales & Analytics"])


@router.get(
    "/summary",
    summary="Get Sales Overview",
    description="Retrieve overall gross revenue, net sales, order counts, and category statistics."
)
def get_sales_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return AnalyticsService.get_dashboard_summary(db)


@router.get(
    "/monthly",
    response_model=List[MonthlySalesResponse],
    summary="Get Monthly Sales Trends",
    description="Retrieve chronologically ordered monthly revenue, order volume, net product sales, and freight value."
)
def get_monthly_sales(db: Session = Depends(get_db)):
    return AnalyticsService.get_monthly_sales(db)


@router.get(
    "/categories",
    response_model=List[CategorySalesResponse],
    summary="Get Category Sales",
    description="Retrieve product categories ranked by total sales revenue."
)
def get_category_sales(
    limit: int = Query(10, ge=1, le=100, description="Top categories count"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_category_sales(db, limit=limit)


@router.get(
    "/products",
    response_model=List[TopProductResponse],
    summary="Get Product Sales",
    description="Retrieve top selling products by revenue and volume."
)
def get_product_sales(
    limit: int = Query(10, ge=1, le=100, description="Top products count"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_top_products(db, limit=limit)


@router.get(
    "/sellers",
    response_model=List[SellerSalesResponse],
    summary="Get Seller Sales",
    description="Retrieve top sellers ranked by generated revenue."
)
def get_seller_sales(
    limit: int = Query(10, ge=1, le=100, description="Top sellers count"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_seller_sales(db, limit=limit)


@router.get(
    "/order-status",
    response_model=List[OrderStatusCountResponse],
    summary="Get Order Status Distribution",
    description="Retrieve breakdown of order statuses with counts and percentages."
)
def get_order_status_distribution(db: Session = Depends(get_db)):
    return AnalyticsService.get_order_status_distribution(db)
