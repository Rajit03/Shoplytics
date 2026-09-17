"""
Shoplytics: SQLAlchemy ORM Models
Directly mapped to the 8 existing PostgreSQL tables in the 'shoplytics' database.
"""

from sqlalchemy import Column, String, Integer, BigInteger, Numeric, Date, DateTime, Text
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_unique_id = Column(String(64), primary_key=True, index=True)
    total_orders = Column(Integer)
    total_spending = Column(Numeric(12, 2))
    total_freight = Column(Numeric(12, 2))
    total_products = Column(Integer)
    average_order_value = Column(Numeric(12, 2))
    cluster = Column(Integer, index=True)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(64), primary_key=True, index=True)
    product_category_name = Column(String(100))
    product_name_lenght = Column(Integer)
    product_description_lenght = Column(Integer)
    product_photos_qty = Column(Integer)
    product_weight_g = Column(Numeric(10, 2))
    product_length_cm = Column(Numeric(10, 2))
    product_height_cm = Column(Numeric(10, 2))
    product_width_cm = Column(Numeric(10, 2))
    product_category_name_english = Column(String(100), index=True)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(String(64), index=True)
    order_status = Column(String(50), index=True)
    order_purchase_timestamp = Column(DateTime, index=True)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)
    order_year = Column(Integer)
    order_month = Column(Integer)
    order_month_name = Column(String(20))
    order_date = Column(Date)
    order_day = Column(Integer)
    order_day_of_week = Column(String(20))
    delivery_days = Column(Numeric(10, 4))
    estimated_delivery_days = Column(Numeric(10, 4))


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    customer_unique_id = Column(String(64), primary_key=True, index=True)
    total_orders = Column(Integer)
    total_spending = Column(Numeric(12, 2))
    total_freight = Column(Numeric(12, 2))
    total_products = Column(Integer)
    average_order_value = Column(Numeric(12, 2))
    cluster = Column(Integer, index=True)


class ClusterProfile(Base):
    __tablename__ = "cluster_profiles"

    cluster = Column(Integer, primary_key=True)
    customers = Column(BigInteger)
    avg_orders = Column(Numeric(10, 4))
    avg_spending = Column(Numeric(12, 4))
    avg_freight = Column(Numeric(12, 4))
    avg_products = Column(Numeric(10, 4))
    avg_order_value = Column(Numeric(12, 4))
    min_spending = Column(Numeric(12, 2))
    max_spending = Column(Numeric(12, 2))


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_id = Column(String(64), index=True)
    rank = Column(Integer, index=True)
    product_id = Column(String(64), index=True)
    product_category = Column(String(100))
    recommendation_score = Column(Numeric(8, 4))
    apriori_score = Column(Numeric(8, 4))
    similarity_score = Column(Numeric(8, 4))
    popularity_score = Column(Numeric(8, 4))
    recommendation_source = Column(String(100))


class AssociationRule(Base):
    __tablename__ = "association_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    antecedent = Column(Text)
    antecedent_categories = Column(Text)
    consequent = Column(Text)
    consequent_categories = Column(Text)
    antecedent_support = Column(Numeric(12, 6))
    consequent_support = Column(Numeric(12, 6))
    support = Column(Numeric(12, 6), index=True)
    support_count = Column(Integer)
    confidence = Column(Numeric(10, 6), index=True)
    lift = Column(Numeric(12, 4), index=True)


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(String(64), index=True)
    order_item_id = Column(Integer)
    product_id = Column(String(64), index=True)
    seller_id = Column(String(64))
    shipping_limit_date = Column(DateTime)
    price = Column(Numeric(10, 2))
    freight_value = Column(Numeric(10, 2))
    total_item_value = Column(Numeric(10, 2))
    customer_id = Column(String(64))
    order_status = Column(String(50))
    order_purchase_timestamp = Column(DateTime)
    order_approved_at = Column(DateTime)
    order_delivered_carrier_date = Column(DateTime)
    order_delivered_customer_date = Column(DateTime)
    order_estimated_delivery_date = Column(DateTime)
    order_year = Column(Integer)
    order_month = Column(Integer)
    order_month_name = Column(String(20))
    order_date = Column(Date)
    order_day = Column(Integer)
    order_day_of_week = Column(String(20))
    delivery_days = Column(Numeric(10, 4))
    estimated_delivery_days = Column(Numeric(10, 4))
    product_category_name_english = Column(String(100), index=True)
    customer_unique_id = Column(String(64), index=True)
    customer_city = Column(String(100))
    customer_state = Column(String(10))
