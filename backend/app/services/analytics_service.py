"""
Shoplytics: Analytics & Business Logic Service Layer
Encapsulates database operations, optimized parameterized queries, and analytics aggregations.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc, asc
from ..models import (
    Customer, Product, Order, CustomerSegment, ClusterProfile,
    Recommendation, AssociationRule, Analytics
)


class AnalyticsService:

    # =====================================================================
    # DASHBOARD SUMMARY
    # =====================================================================

    @staticmethod
    def get_dashboard_summary(db: Session) -> Dict[str, Any]:
        """Aggregate top-level dashboard metrics directly from the database."""
        # Query aggregate sales and freight from analytics
        sales_sql = text("""
            SELECT 
                COUNT(DISTINCT order_id) AS total_orders,
                ROUND(COALESCE(SUM(total_item_value), 0), 2) AS total_sales,
                ROUND(COALESCE(SUM(freight_value), 0), 2) AS total_freight,
                COUNT(DISTINCT product_category_name_english) AS active_categories
            FROM analytics;
        """)
        sales_res = db.execute(sales_sql).fetchone()

        total_orders = sales_res[0] or 0
        total_sales = float(sales_res[1] or 0.0)
        total_freight = float(sales_res[2] or 0.0)
        active_categories = sales_res[3] or 0

        # Total unique customers
        total_customers = db.query(func.count(Customer.customer_unique_id)).scalar() or 0

        # Total products catalog
        total_products = db.query(func.count(Product.product_id)).scalar() or 0

        # Delivered and cancelled orders counts from orders
        status_sql = text("""
            SELECT 
                COALESCE(SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END), 0) AS delivered,
                COALESCE(SUM(CASE WHEN order_status = 'canceled' THEN 1 ELSE 0 END), 0) AS cancelled
            FROM orders;
        """)
        status_res = db.execute(status_sql).fetchone()
        delivered_orders = int(status_res[0]) if status_res else 0
        cancelled_orders = int(status_res[1]) if status_res else 0

        # Average Order Value
        avg_order_value = round(total_sales / total_orders, 2) if total_orders > 0 else 0.0

        # Total K-Means clusters
        total_clusters = db.query(func.count(ClusterProfile.cluster)).scalar() or 0

        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_products": total_products,
            "total_sales": total_sales,
            "total_freight": total_freight,
            "average_order_value": avg_order_value,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
            "active_categories": active_categories,
            "total_clusters": total_clusters
        }

    # =====================================================================
    # CUSTOMERS
    # =====================================================================

    @staticmethod
    def get_customers(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        cluster: Optional[int] = None,
        min_spending: Optional[float] = None,
        max_spending: Optional[float] = None
    ) -> Tuple[List[Customer], int]:
        """Fetch paginated customer records with optional cluster and spending filters."""
        query = db.query(Customer)
        if cluster is not None:
            query = query.filter(Customer.cluster == cluster)
        if min_spending is not None:
            query = query.filter(Customer.total_spending >= min_spending)
        if max_spending is not None:
            query = query.filter(Customer.total_spending <= max_spending)

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(Customer.total_spending)).offset(offset).limit(page_size).all()
        return records, total

    @staticmethod
    def get_customer_by_id(db: Session, customer_unique_id: str) -> Optional[Customer]:
        """Retrieve single customer by unique ID."""
        return db.query(Customer).filter(Customer.customer_unique_id == customer_unique_id).first()

    @staticmethod
    def get_top_spenders(db: Session, limit: int = 10) -> List[Customer]:
        """Retrieve top spending customers."""
        return db.query(Customer).order_by(desc(Customer.total_spending)).limit(limit).all()

    @staticmethod
    def search_customers(
        db: Session,
        query_str: Optional[str] = None,
        cluster: Optional[int] = None,
        limit: int = 20
    ) -> List[Customer]:
        """Search customers by ID prefix or cluster."""
        q = db.query(Customer)
        if query_str:
            q = q.filter(Customer.customer_unique_id.ilike(f"{query_str}%"))
        if cluster is not None:
            q = q.filter(Customer.cluster == cluster)
        return q.order_by(desc(Customer.total_spending)).limit(limit).all()

    @staticmethod
    def get_customer_full_profile(db: Session, customer_unique_id: str) -> Optional[Dict[str, Any]]:
        """Fetch unified customer profile including cluster profile, orders, and recommendations."""
        cust = db.query(Customer).filter(Customer.customer_unique_id == customer_unique_id).first()
        if not cust:
            return None

        # Fetch cluster details
        cluster_info = None
        if cust.cluster is not None:
            prof = db.query(ClusterProfile).filter(ClusterProfile.cluster == cust.cluster).first()
            if prof:
                cluster_info = {
                    "cluster": prof.cluster,
                    "cluster_size": prof.customers,
                    "avg_spending": float(prof.avg_spending or 0),
                    "avg_orders": float(prof.avg_orders or 0),
                    "avg_order_value": float(prof.avg_order_value or 0),
                    "min_spending": float(prof.min_spending or 0),
                    "max_spending": float(prof.max_spending or 0)
                }

        # Fetch customer orders from analytics table
        order_sql = text("""
            SELECT DISTINCT 
                order_id, order_purchase_timestamp, order_status, 
                product_category_name_english, total_item_value
            FROM analytics
            WHERE customer_unique_id = :cid
            ORDER BY order_purchase_timestamp DESC
            LIMIT 10;
        """)
        order_rows = db.execute(order_sql, {"cid": customer_unique_id}).fetchall()
        order_history = [
            {
                "order_id": r[0],
                "purchase_timestamp": str(r[1]) if r[1] else None,
                "status": r[2],
                "category": r[3],
                "value": float(r[4] or 0.0)
            }
            for r in order_rows
        ]

        # Fetch recommendations
        rec_sql = text("""
            SELECT r.rank, r.product_id, r.product_category, r.recommendation_score, r.recommendation_source,
                   p.product_weight_g, p.product_photos_qty
            FROM recommendations r
            LEFT JOIN products p ON r.product_id = p.product_id
            WHERE r.customer_id = :cid
            ORDER BY r.rank
            LIMIT 5;
        """)
        rec_rows = db.execute(rec_sql, {"cid": customer_unique_id}).fetchall()
        recommendations = [
            {
                "rank": r[0],
                "product_id": r[1],
                "category": r[2],
                "score": float(r[3] or 0.0),
                "source": r[4],
                "weight_g": float(r[5]) if r[5] is not None else None,
                "photos_qty": r[6]
            }
            for r in rec_rows
        ]

        return {
            "customer": cust,
            "cluster_profile": cluster_info,
            "order_history": order_history,
            "recommendations": recommendations
        }

    # =====================================================================
    # PRODUCTS
    # =====================================================================

    @staticmethod
    def get_products(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None
    ) -> Tuple[List[Product], int]:
        """Fetch paginated products with optional category filter."""
        query = db.query(Product)
        if category:
            query = query.filter(Product.product_category_name_english.ilike(category))

        total = query.count()
        offset = (page - 1) * page_size
        records = query.offset(offset).limit(page_size).all()
        return records, total

    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        """Fetch single product by ID."""
        return db.query(Product).filter(Product.product_id == product_id).first()

    @staticmethod
    def get_top_products(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top products by sales volume & revenue from analytics table."""
        sql = text("""
            SELECT 
                product_id,
                COALESCE(product_category_name_english, 'Unknown') AS category,
                COUNT(*) AS units_sold,
                ROUND(SUM(total_item_value), 2) AS revenue
            FROM analytics
            GROUP BY product_id, product_category_name_english
            ORDER BY revenue DESC
            LIMIT :lim;
        """)
        rows = db.execute(sql, {"lim": limit}).fetchall()
        return [
            {
                "product_id": r[0],
                "product_category_name_english": r[1],
                "units_sold": int(r[2]),
                "revenue": float(r[3] or 0.0)
            }
            for r in rows
        ]

    # =====================================================================
    # ORDERS
    # =====================================================================

    @staticmethod
    def get_orders(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Order], int]:
        """Fetch paginated orders with optional status filter."""
        query = db.query(Order)
        if status:
            query = query.filter(Order.order_status.ilike(status))

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(Order.order_purchase_timestamp)).offset(offset).limit(page_size).all()
        return records, total

    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        """Fetch single order by ID."""
        return db.query(Order).filter(Order.order_id == order_id).first()

    @staticmethod
    def get_recent_orders(db: Session, limit: int = 10) -> List[Order]:
        """Fetch most recent orders by purchase timestamp."""
        return db.query(Order).order_by(desc(Order.order_purchase_timestamp)).limit(limit).all()

    # =====================================================================
    # CUSTOMER SEGMENTS & CLUSTERS
    # =====================================================================

    @staticmethod
    def get_segment_summary(db: Session) -> List[Dict[str, Any]]:
        """Retrieve K-Means segment summary with aggregate metrics."""
        sql = text("""
            SELECT 
                cs.cluster,
                COUNT(cs.customer_unique_id) AS total_customers,
                ROUND(AVG(cs.total_spending), 2) AS avg_spending,
                ROUND(AVG(cs.total_orders), 2) AS avg_orders,
                ROUND(AVG(cs.average_order_value), 2) AS avg_order_value
            FROM customer_segments cs
            GROUP BY cs.cluster
            ORDER BY cs.cluster;
        """)
        rows = db.execute(sql).fetchall()
        return [
            {
                "cluster": int(r[0]),
                "total_customers": int(r[1]),
                "avg_spending": float(r[2] or 0.0),
                "avg_orders": float(r[3] or 0.0),
                "avg_order_value": float(r[4] or 0.0)
            }
            for r in rows
        ]

    @staticmethod
    def get_cluster_profiles(db: Session) -> List[ClusterProfile]:
        """Retrieve all precomputed cluster profiles."""
        return db.query(ClusterProfile).order_by(ClusterProfile.cluster).all()

    @staticmethod
    def get_cluster_customers(
        db: Session,
        cluster_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CustomerSegment], int]:
        """Fetch paginated customers in a specific cluster."""
        query = db.query(CustomerSegment).filter(CustomerSegment.cluster == cluster_id)
        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(CustomerSegment.total_spending)).offset(offset).limit(page_size).all()
        return records, total

    # =====================================================================
    # RECOMMENDATIONS
    # =====================================================================

    @staticmethod
    def get_customer_recommendations(db: Session, customer_id: str, limit: int = 10) -> List[Recommendation]:
        """Retrieve recommendations for a specific customer sorted by rank."""
        return db.query(Recommendation).filter(
            Recommendation.customer_id == customer_id
        ).order_by(Recommendation.rank).limit(limit).all()

    @staticmethod
    def get_recommendations(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        customer_id: Optional[str] = None,
        product_id: Optional[str] = None,
        source: Optional[str] = None
    ) -> Tuple[List[Recommendation], int]:
        """Fetch paginated recommendations with optional filters."""
        query = db.query(Recommendation)
        if customer_id:
            query = query.filter(Recommendation.customer_id == customer_id)
        if product_id:
            query = query.filter(Recommendation.product_id == product_id)
        if source:
            query = query.filter(Recommendation.recommendation_source.ilike(f"%{source}%"))

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(Recommendation.id).offset(offset).limit(page_size).all()
        return records, total

    # =====================================================================
    # ASSOCIATION RULES (APRIORI)
    # =====================================================================

    @staticmethod
    def get_association_rules(
        db: Session,
        limit: int = 20,
        min_support: Optional[float] = None,
        min_confidence: Optional[float] = None,
        min_lift: Optional[float] = None
    ) -> List[AssociationRule]:
        """Fetch Apriori association rules with threshold filters."""
        query = db.query(AssociationRule)
        if min_support is not None:
            query = query.filter(AssociationRule.support >= min_support)
        if min_confidence is not None:
            query = query.filter(AssociationRule.confidence >= min_confidence)
        if min_lift is not None:
            query = query.filter(AssociationRule.lift >= min_lift)

        return query.order_by(desc(AssociationRule.lift)).limit(limit).all()

    @staticmethod
    def get_top_association_rules(db: Session, limit: int = 10) -> List[AssociationRule]:
        """Retrieve top association rules sorted by lift."""
        return db.query(AssociationRule).order_by(desc(AssociationRule.lift)).limit(limit).all()

    # =====================================================================
    # SALES & ANALYTICS
    # =====================================================================

    @staticmethod
    def get_monthly_sales(db: Session) -> List[Dict[str, Any]]:
        """Retrieve monthly sales trends."""
        sql = text("""
            SELECT 
                order_year,
                order_month,
                order_month_name,
                COUNT(DISTINCT order_id) AS orders_count,
                ROUND(SUM(total_item_value), 2) AS revenue,
                ROUND(SUM(price), 2) AS net_sales,
                ROUND(SUM(freight_value), 2) AS freight_value
            FROM analytics
            WHERE order_year IS NOT NULL
            GROUP BY order_year, order_month, order_month_name
            ORDER BY order_year, order_month;
        """)
        rows = db.execute(sql).fetchall()
        return [
            {
                "order_year": int(r[0]),
                "order_month": int(r[1]),
                "order_month_name": str(r[2]),
                "orders_count": int(r[3]),
                "revenue": float(r[4] or 0.0),
                "net_sales": float(r[5] or 0.0),
                "freight_value": float(r[6] or 0.0)
            }
            for r in rows
        ]

    @staticmethod
    def get_category_sales(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve category sales ranking."""
        sql = text("""
            SELECT 
                product_category_name_english AS category,
                COUNT(*) AS items_sold,
                COUNT(DISTINCT order_id) AS orders_count,
                ROUND(SUM(total_item_value), 2) AS revenue,
                ROUND(AVG(price), 2) AS average_price
            FROM analytics
            WHERE product_category_name_english IS NOT NULL
            GROUP BY product_category_name_english
            ORDER BY revenue DESC
            LIMIT :lim;
        """)
        rows = db.execute(sql, {"lim": limit}).fetchall()
        return [
            {
                "category": str(r[0]),
                "items_sold": int(r[1]),
                "orders_count": int(r[2]),
                "revenue": float(r[3] or 0.0),
                "average_price": float(r[4] or 0.0)
            }
            for r in rows
        ]

    @staticmethod
    def get_seller_sales(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve top performing sellers."""
        sql = text("""
            SELECT 
                seller_id,
                COUNT(DISTINCT order_id) AS orders_count,
                COUNT(*) AS items_sold,
                ROUND(SUM(total_item_value), 2) AS revenue
            FROM analytics
            WHERE seller_id IS NOT NULL
            GROUP BY seller_id
            ORDER BY revenue DESC
            LIMIT :lim;
        """)
        rows = db.execute(sql, {"lim": limit}).fetchall()
        return [
            {
                "seller_id": str(r[0]),
                "orders_count": int(r[1]),
                "items_sold": int(r[2]),
                "revenue": float(r[3] or 0.0)
            }
            for r in rows
        ]

    @staticmethod
    def get_order_status_distribution(db: Session) -> List[Dict[str, Any]]:
        """Retrieve order fulfillment status counts and percentage."""
        sql = text("""
            SELECT 
                order_status,
                COUNT(*) AS count,
                ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
            FROM orders
            GROUP BY order_status
            ORDER BY count DESC;
        """)
        rows = db.execute(sql).fetchall()
        return [
            {
                "order_status": str(r[0]),
                "count": int(r[1]),
                "percentage": float(r[2] or 0.0)
            }
            for r in rows
        ]
