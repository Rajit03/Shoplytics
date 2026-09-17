"""
Shoplytics: Dashboard API Router
Provides high-level dashboard summaries and health metrics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import DashboardSummaryResponse
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get Dashboard Summary",
    description="Retrieve high-level business, order fulfillment, customer, and product metrics."
)
def get_dashboard_summary(db: Session = Depends(get_db)):
    try:
        return AnalyticsService.get_dashboard_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard summary.")
