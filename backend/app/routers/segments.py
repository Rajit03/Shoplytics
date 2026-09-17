"""
Shoplytics: Customer Segments API Router
Handles K-Means customer segment profiles, cluster summaries, and cluster customer lookups.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import (
    ClusterSummaryResponse, ClusterProfileResponse,
    CustomerSegmentResponse, PaginatedResponse
)
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/segments", tags=["Customer Segments"])


@router.get(
    "",
    response_model=List[ClusterSummaryResponse],
    summary="Get Cluster Summary",
    description="Retrieve high-level population and spending summaries for all 4 customer clusters."
)
def get_segment_summary(db: Session = Depends(get_db)):
    return AnalyticsService.get_segment_summary(db)


@router.get(
    "/profiles",
    response_model=List[ClusterProfileResponse],
    summary="Get Cluster Profiles",
    description="Retrieve precomputed cluster profile boundaries, spending metrics, and averages from Spark ML."
)
def get_cluster_profiles(db: Session = Depends(get_db)):
    return AnalyticsService.get_cluster_profiles(db)


@router.get(
    "/{cluster_id}/customers",
    response_model=PaginatedResponse[CustomerSegmentResponse],
    summary="Get Customers in Cluster",
    description="Retrieve paginated customers belonging to a specific cluster ID (0, 1, 2, 3)."
)
def get_cluster_customers(
    cluster_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    if cluster_id not in (0, 1, 2, 3):
        raise HTTPException(status_code=400, detail=f"Invalid cluster ID '{cluster_id}'. Valid clusters are 0, 1, 2, 3.")

    records, total = AnalyticsService.get_cluster_customers(
        db=db,
        cluster_id=cluster_id,
        page=page,
        page_size=page_size
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
    "/{cluster_id}",
    response_model=ClusterProfileResponse,
    summary="Get Cluster Details",
    description="Retrieve statistical profile boundaries and metrics for a specific cluster ID."
)
def get_cluster_details(
    cluster_id: int,
    db: Session = Depends(get_db)
):
    profiles = AnalyticsService.get_cluster_profiles(db)
    for p in profiles:
        if p.cluster == cluster_id:
            return p
    raise HTTPException(status_code=404, detail=f"Cluster '{cluster_id}' not found.")
