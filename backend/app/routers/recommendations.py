"""
Shoplytics: Recommendations API Router
Serves collaborative and association-based product recommendations.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import RecommendationResponse, PaginatedResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get(
    "",
    response_model=PaginatedResponse[RecommendationResponse],
    summary="List Recommendations",
    description="Retrieve paginated recommendation records with optional filters for customer, product, or recommendation source."
)
def list_recommendations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    source: Optional[str] = Query(None, description="Filter by recommendation source (e.g. Apriori, Cosine, Popularity)"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_recommendations(
        db=db,
        page=page,
        page_size=page_size,
        customer_id=customer_id,
        product_id=product_id,
        source=source
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
    "/{customer_id}",
    response_model=List[RecommendationResponse],
    summary="Get Customer Recommendations",
    description="Retrieve top personalized product recommendations for a specific customer ID sorted by rank."
)
def get_customer_recommendations(
    customer_id: str,
    limit: int = Query(10, ge=1, le=50, description="Max recommendations to return"),
    db: Session = Depends(get_db)
):
    recs = AnalyticsService.get_customer_recommendations(db, customer_id=customer_id, limit=limit)
    if not recs:
        # Check if customer exists in general
        cust = AnalyticsService.get_customer_by_id(db, customer_id)
        if not cust:
            raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
        return []
    return recs
