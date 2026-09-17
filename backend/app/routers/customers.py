"""
Shoplytics: Customers API Router
Handles customer listings, pagination, top spenders, customer profile lookups, and searches.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import CustomerResponse, CustomerProfileResponse, PaginatedResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get(
    "",
    response_model=PaginatedResponse[CustomerResponse],
    summary="List Customers",
    description="Retrieve paginated customer records with optional cluster and spending filters."
)
def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    cluster: Optional[int] = Query(None, description="Filter by K-Means cluster ID (0-3)"),
    min_spending: Optional[float] = Query(None, ge=0, description="Minimum total spending filter"),
    max_spending: Optional[float] = Query(None, ge=0, description="Maximum total spending filter"),
    db: Session = Depends(get_db)
):
    records, total = AnalyticsService.get_customers(
        db=db,
        page=page,
        page_size=page_size,
        cluster=cluster,
        min_spending=min_spending,
        max_spending=max_spending
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
    "/top-spenders",
    response_model=List[CustomerResponse],
    summary="Get Top Spenders",
    description="Retrieve highest spending customers ordered by total spending."
)
def get_top_spenders(
    limit: int = Query(10, ge=1, le=100, description="Number of customers to return"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.get_top_spenders(db, limit=limit)


@router.get(
    "/search",
    response_model=List[CustomerResponse],
    summary="Search Customers",
    description="Search customers by unique ID prefix or cluster assignment."
)
def search_customers(
    query: Optional[str] = Query(None, description="Customer ID prefix to search for"),
    cluster: Optional[int] = Query(None, description="Cluster filter"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    db: Session = Depends(get_db)
):
    return AnalyticsService.search_customers(db, query_str=query, cluster=cluster, limit=limit)


@router.get(
    "/{customer_unique_id}/profile",
    response_model=CustomerProfileResponse,
    summary="Get Customer Full Profile",
    description="Retrieve comprehensive customer profile including assigned cluster details, order history, and product recommendations."
)
def get_customer_profile(
    customer_unique_id: str,
    db: Session = Depends(get_db)
):
    profile = AnalyticsService.get_customer_full_profile(db, customer_unique_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_unique_id}' not found.")
    return profile


@router.get(
    "/{customer_unique_id}",
    response_model=CustomerResponse,
    summary="Get Customer by ID",
    description="Retrieve customer summary metrics by customer_unique_id."
)
def get_customer_by_id(
    customer_unique_id: str,
    db: Session = Depends(get_db)
):
    cust = AnalyticsService.get_customer_by_id(db, customer_unique_id)
    if not cust:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_unique_id}' not found.")
    return cust
