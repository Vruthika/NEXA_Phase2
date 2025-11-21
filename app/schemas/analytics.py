# app/schemas/analytics.py
from pydantic import BaseModel
from datetime import datetime
from typing import Any, List, Optional, Dict

class RevenueAnalyticsResponse(BaseModel):
    period: str
    date: str
    revenue: float
    transactions_count: int
    average_order_value: float

    class Config:
        from_attributes = True

class CustomerGrowthResponse(BaseModel):
    period: str
    date: str
    new_customers: int
    total_customers: int
    growth_rate: float

    class Config:
        from_attributes = True

class PlanPerformanceResponse(BaseModel):
    plan_id: int
    plan_name: str
    total_revenue: float
    transaction_count: int
    popularity_rank: int

    class Config:
        from_attributes = True

class DashboardStatsResponse(BaseModel):
    total_revenue_today: float
    new_customers_today: int
    transactions_today: int
    active_subscriptions: int
    revenue_trend: List[RevenueAnalyticsResponse]
    customer_growth_trend: List[CustomerGrowthResponse]
    top_performing_plans: List[PlanPerformanceResponse]

    class Config:
        from_attributes = True
    
class SimplifiedRevenueTrend(BaseModel):
    date: str
    revenue: float
    transactions: int

class SimplifiedCustomerGrowth(BaseModel):
    date: str
    new_customers: int
    total_customers: int
    growth: str  # Formatted as percentage

class SimplifiedReferralTrend(BaseModel):
    date: str
    new_referrals: int
    successful_referrals: int
    success_rate: str  # Formatted as percentage

class SimplifiedPlanPerformance(BaseModel):
    plan_name: str
    transactions: int
    revenue: str  # Formatted as currency string
    rank: int

class DashboardSummaryResponse(BaseModel):
    # Today's Overview
    today_stats: Dict[str, Any]
    
    # Trends (Last 7 days)
    revenue_trend: List[SimplifiedRevenueTrend]
    customer_growth: List[SimplifiedCustomerGrowth]
    referral_trend: List[SimplifiedReferralTrend]
    
    # Top Performers
    top_plans: List[SimplifiedPlanPerformance]
    
    # Quick Stats
    quick_stats: Dict[str, Any]

    class Config:
        from_attributes = True

class TransactionSummaryResponse(BaseModel):
    total: int
    successful: int
    failed: int
    success_rate: str
    payment_methods: Dict[str, int]

class SubscriptionOverviewResponse(BaseModel):
    active: int
    expiring_soon: int
    recently_activated: int
    in_queue: int

# Additional schemas for detailed analytics
class RevenueTrendRequest(BaseModel):
    period: str = "daily"  # daily, weekly, monthly
    days: int = 30

class CustomerGrowthRequest(BaseModel):
    days: int = 90

class ReferralTrendRequest(BaseModel):
    days: int = 90

class PlanPerformanceRequest(BaseModel):
    limit: int = 10

# Response schemas for individual analytics endpoints
class RevenueAnalyticsDetailResponse(BaseModel):
    period: str
    data: List[Dict[str, Any]]

class CustomerGrowthDetailResponse(BaseModel):
    period: str
    data: List[Dict[str, Any]]

class ReferralAnalyticsDetailResponse(BaseModel):
    period: str
    data: List[Dict[str, Any]]

class PlanPerformanceDetailResponse(BaseModel):
    data: List[Dict[str, Any]]

# Enhanced analytics for comprehensive reports
class ComprehensiveAnalyticsResponse(BaseModel):
    revenue_analytics: RevenueAnalyticsDetailResponse
    customer_analytics: CustomerGrowthDetailResponse
    referral_analytics: ReferralAnalyticsDetailResponse
    plan_analytics: PlanPerformanceDetailResponse
    summary: Dict[str, Any]

    class Config:
        from_attributes = True

# Real-time metrics for dashboard
class RealTimeMetrics(BaseModel):
    current_revenue: float
    current_customers: int
    current_transactions: int
    system_health: str  # good, warning, critical

# Trend comparison schemas
class TrendComparison(BaseModel):
    current_period: Dict[str, Any]
    previous_period: Dict[str, Any]
    growth_percentage: float
    trend_direction: str  # up, down, stable

class RevenueComparison(TrendComparison):
    pass

class CustomerComparison(TrendComparison):
    pass

class ReferralComparison(TrendComparison):
    pass

# Performance metrics
class PerformanceMetrics(BaseModel):
    metric_name: str
    current_value: Any
    target_value: Any
    achievement_percentage: float
    status: str  # exceeded, met, below

# KPI schemas
class KPIResponse(BaseModel):
    kpi_name: str
    current_value: Any
    previous_value: Any
    change_percentage: float
    target_value: Any
    status: str  # positive, negative, neutral

# Chart data schemas
class ChartDataPoint(BaseModel):
    label: str
    value: Any
    color: Optional[str] = None

class ChartDataset(BaseModel):
    label: str
    data: List[ChartDataPoint]
    backgroundColor: Optional[List[str]] = None
    borderColor: Optional[str] = None

class ChartResponse(BaseModel):
    type: str  # line, bar, pie, doughnut
    labels: List[str]
    datasets: List[ChartDataset]
    options: Optional[Dict[str, Any]] = None

# Export schemas
class AnalyticsExportRequest(BaseModel):
    analytics_type: str  # revenue, customers, referrals, comprehensive
    format: str = "json"  # json, csv
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Optional[Dict[str, Any]] = None

class AnalyticsExportResponse(BaseModel):
    export_id: str
    download_url: str
    file_size: str
    generated_at: datetime