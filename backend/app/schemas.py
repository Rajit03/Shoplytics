"""
Shoplytics: Pydantic v2 Request & Response Schemas
Provides data validation, serialization, and typing for all API endpoints.
"""

from typing import Generic, TypeVar, List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# =====================================================================
# PAGINATION SCHEMA
# =====================================================================

class PaginatedResponse(BaseModel, Generic[T]):
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total matching records count")
    total_pages: int = Field(..., ge=0, description="Total pages available")
    data: List[T] = Field(..., description="List of items for the current page")


# =====================================================================
# BASE & SYSTEM SCHEMAS
# =====================================================================

class MessageResponse(BaseModel):
    message: str
    version: str = "1.0.0"


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


# =====================================================================
# DASHBOARD SCHEMAS
# =====================================================================

class DashboardSummaryResponse(BaseModel):
    total_customers: int
    total_orders: int
    total_products: int
    total_sales: float
    total_freight: float
    average_order_value: float
    delivered_orders: int
    cancelled_orders: int
    active_categories: int
    total_clusters: int


# =====================================================================
# CUSTOMER SCHEMAS
# =====================================================================

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_unique_id: str
    total_orders: Optional[int] = 0
    total_spending: Optional[float] = 0.0
    total_freight: Optional[float] = 0.0
    total_products: Optional[int] = 0
    average_order_value: Optional[float] = 0.0
    cluster: Optional[int] = None


class CustomerProfileResponse(BaseModel):
    customer: CustomerResponse
    cluster_profile: Optional[dict] = None
    order_history: List[dict] = []
    recommendations: List[dict] = []


# =====================================================================
# PRODUCT SCHEMAS
# =====================================================================

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    product_category_name: Optional[str] = None
    product_name_lenght: Optional[int] = None
    product_description_lenght: Optional[int] = None
    product_photos_qty: Optional[int] = None
    product_weight_g: Optional[float] = None
    product_length_cm: Optional[float] = None
    product_height_cm: Optional[float] = None
    product_width_cm: Optional[float] = None
    product_category_name_english: Optional[str] = None


class TopProductResponse(BaseModel):
    product_id: str
    product_category_name_english: Optional[str] = "Unknown"
    units_sold: int
    revenue: float


# =====================================================================
# ORDER SCHEMAS
# =====================================================================

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    customer_id: Optional[str] = None
    order_status: Optional[str] = None
    order_purchase_timestamp: Optional[datetime] = None
    order_approved_at: Optional[datetime] = None
    order_delivered_carrier_date: Optional[datetime] = None
    order_delivered_customer_date: Optional[datetime] = None
    order_estimated_delivery_date: Optional[datetime] = None
    order_year: Optional[int] = None
    order_month: Optional[int] = None
    order_month_name: Optional[str] = None
    order_date: Optional[date] = None
    order_day: Optional[int] = None
    order_day_of_week: Optional[str] = None
    delivery_days: Optional[float] = None
    estimated_delivery_days: Optional[float] = None


class OrderStatusCountResponse(BaseModel):
    order_status: str
    count: int
    percentage: float


# =====================================================================
# SEGMENT & CLUSTER SCHEMAS
# =====================================================================

class CustomerSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_unique_id: str
    total_orders: Optional[int] = 0
    total_spending: Optional[float] = 0.0
    total_freight: Optional[float] = 0.0
    total_products: Optional[int] = 0
    average_order_value: Optional[float] = 0.0
    cluster: Optional[int] = None


class ClusterProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cluster: int
    customers: int
    avg_orders: float
    avg_spending: float
    avg_freight: float
    avg_products: float
    avg_order_value: float
    min_spending: float
    max_spending: float


class ClusterSummaryResponse(BaseModel):
    cluster: int
    total_customers: int
    avg_spending: float
    avg_orders: float
    avg_order_value: float


# =====================================================================
# RECOMMENDATION SCHEMAS
# =====================================================================

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: str
    rank: int
    product_id: str
    product_category: Optional[str] = None
    recommendation_score: float
    apriori_score: Optional[float] = 0.0
    similarity_score: Optional[float] = 0.0
    popularity_score: Optional[float] = 0.0
    recommendation_source: Optional[str] = None


# =====================================================================
# ASSOCIATION RULES SCHEMAS
# =====================================================================

class AssociationRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    antecedent: str
    antecedent_categories: Optional[str] = None
    consequent: str
    consequent_categories: Optional[str] = None
    antecedent_support: Optional[float] = 0.0
    consequent_support: Optional[float] = 0.0
    support: float
    support_count: Optional[int] = 0
    confidence: float
    lift: float


# =====================================================================
# SALES & ANALYTICS SCHEMAS
# =====================================================================

class MonthlySalesResponse(BaseModel):
    order_year: int
    order_month: int
    order_month_name: str
    orders_count: int
    revenue: float
    net_sales: float
    freight_value: float


class CategorySalesResponse(BaseModel):
    category: str
    items_sold: int
    orders_count: int
    revenue: float
    average_price: float


class SellerSalesResponse(BaseModel):
    seller_id: str
    orders_count: int
    items_sold: int
    revenue: float
