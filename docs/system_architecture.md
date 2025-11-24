# System Architecture Document

## NEXA Mobile Recharge System

**Version:** 1.0  
**Last Updated:** November 2025  
**Technology Stack:** FastAPI + PostgreSQL + MongoDB

---

## 1. Executive Summary

The NEXA Mobile Recharge System is a RESTful API-based application designed to manage prepaid and postpaid mobile recharge services. Built with FastAPI, PostgreSQL, and MongoDB, it provides secure, scalable endpoints for telecom operators to manage customer accounts, subscriptions, billing, and promotional programs.

---

## 2. System Overview

### 2.1 Purpose

- Centralized management of mobile recharge services (prepaid & postpaid)
- Customer account and subscription management
- Automated billing and payment processing
- Referral and loyalty program management
- Real-time notification system
- Administrative analytics and reporting

### 2.2 Key Features

- Customer registration and authentication with JWT
- Prepaid recharge with offers and discounts
- Postpaid plan activation with billing cycles
- Family account linking (linked accounts)
- Referral program with rewards
- Automated notifications (SMS/Push)
- Subscription queue management
- Data usage tracking and alerts
- Admin dashboard with analytics
- CMS for dynamic content management
- Backup and restore functionality

---

## 3. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│     (Web App, Mobile App, Third-party Integrations)         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                API Gateway / Load Balancer                   │
│                    (nginx/Cloud LB)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Authentication Middleware                    │   │
│  │      (JWT Token Validation & RBAC)                   │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │              API Router Layer                        │   │
│  │  • /auth          • /customer                        │   │
│  │  • /admin         • /customer/postpaid               │   │
│  │  • /customer/referral  • /customer/notifications     │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │            Business Logic Layer                      │   │
│  │  • Subscription Service  • Notification Service      │   │
│  │  • Payment Processing    • Referral Logic            │   │
│  │  • Queue Management      • Billing Service           │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────▼───────────────────────────────┐   │
│  │          CRUD Operations Layer                       │   │
│  │     Database Access & ORM Operations                 │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼────────┐ ┌─────▼──────┐ ┌───────▼────────┐
│   PostgreSQL   │ │  MongoDB   │ │  File Storage  │
│  (Primary DB)  │ │   (CMS)    │ │   (Backups)    │
└────────────────┘ └────────────┘ └────────────────┘
```

---

## 4. Component Architecture

### 4.1 Application Layer Components

#### **Authentication & Authorization Service**

- JWT token generation and validation
- Password hashing with bcrypt
- Role-based access control (Admin, Customer)
- User type verification (admin/customer)
- Token expiration management

#### **Customer Management Service**

- Customer CRUD operations
- Profile management
- Account status tracking (active/inactive/suspended)
- Inactivity monitoring
- Password management

#### **Plan & Offer Management Service**

- Plan catalog management (prepaid/postpaid)
- Category-based filtering
- Offer creation with validity periods
- Discount calculations (percentage/fixed)
- Featured plan management

#### **Prepaid Recharge Service**

- Recharge transaction processing
- Offer application
- Referral discount integration
- Subscription creation
- Queue management for sequential plans
- Top-up activation

#### **Postpaid Management Service**

- Postpaid plan activation
- Billing cycle management
- Secondary number handling (family plans)
- Data addon purchases
- Bill generation and payment
- Usage tracking

#### **Subscription Service**

- Subscription lifecycle management
- Queue-based activation system
- Expiry monitoring and processing
- Data balance tracking
- Daily usage limits
- Top-up integration

#### **Linked Account Service**

- Family member linking
- Linked account recharge
- Relationship management
- Usage tracking per account

#### **Referral Program Service**

- Unique code generation
- Referral tracking (3-step process)
- Discount management (10% referee, 30% referrer)
- Usage log maintenance
- Reward distribution

#### **Notification Service**

- Multi-channel support (SMS/Push)
- Real-time notification delivery
- Automated triggers for events
- Notification history
- Read/unread status tracking

#### **Transaction Management Service**

- Transaction recording
- Payment status tracking
- Transaction history
- Filtering and searching
- Export functionality (CSV/JSON)

#### **Analytics & Reporting Service**

- Revenue analytics
- Customer growth tracking
- Referral trend analysis
- Plan performance metrics
- Dashboard statistics

#### **Backup & Restore Service**

- Automated backup scheduling
- Manual backup creation
- Essential data extraction
- Restore operations
- Backup rotation (max 50)

#### **CMS Service**

- Header content management
- Carousel management
- FAQ management
- MongoDB-based flexible schema

### 4.2 Data Layer Components

#### **PostgreSQL Database**

- Primary transactional data store
- ACID compliance
- Relational integrity
- Full-text search support
- Handles:
  - Customers, Admins
  - Plans, Offers, Categories
  - Transactions, Subscriptions
  - Postpaid activations
  - Referral programs
  - Notifications
  - Linked accounts
  - Backups/Restores

#### **MongoDB**

- CMS content storage
- Flexible schema for dynamic content
- Handles:
  - Headers
  - Carousels
  - FAQs

---

## 5. Database Schema Overview

### 5.1 Core Entities

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Admins    │         │  Customers   │         │  Categories │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ admin_id    │         │ customer_id  │         │ category_id │
│ name        │         │ phone_number │         │ name        │
│ email       │         │ password_hash│         └──────┬──────┘
│ password    │         │ full_name    │                │
└─────────────┘         │ status       │                │
                        │ last_active  │         ┌──────▼──────┐
                        └──────┬───────┘         │    Plans    │
                               │                 ├─────────────┤
                               │                 │ plan_id     │
                               │                 │ category_id │
                               │                 │ plan_name   │
                               │                 │ plan_type   │
                               │                 │ price       │
                               │                 │ validity    │
                               │                 │ is_topup    │
                               │                 └──────┬──────┘
                               │                        │
                        ┌──────▼────────────────────────▼──────┐
                        │         Transactions                 │
                        ├──────────────────────────────────────┤
                        │ transaction_id                       │
                        │ customer_id                          │
                        │ plan_id                              │
                        │ offer_id                             │
                        │ recipient_phone                      │
                        │ original_amount                      │
                        │ discount_amount                      │
                        │ final_amount                         │
                        │ payment_status                       │
                        └──────┬───────────────────────────────┘
                               │
                        ┌──────▼─────────┐
                        │ Subscriptions  │
                        ├────────────────┤
                        │ subscription_id│
                        │ customer_id    │
                        │ plan_id        │
                        │ transaction_id │
                        │ phone_number   │
                        │ is_topup       │
                        │ activation_dt  │
                        │ expiry_dt      │
                        │ data_balance   │
                        └────────────────┘
```

### 5.2 Key Entity Relationships

**Customer** → has many → **Transactions**  
**Customer** → has many → **Subscriptions**  
**Customer** → has many → **Linked Accounts** (as primary)  
**Customer** → has many → **Referral Programs**  
**Customer** → has many → **Notifications**  
**Customer** → has many → **Postpaid Activations**

**Plan** → belongs to → **Category**  
**Plan** → has many → **Offers**  
**Plan** → has many → **Transactions**  
**Plan** → has many → **Subscriptions**

**Transaction** → belongs to → **Customer**  
**Transaction** → belongs to → **Plan**  
**Transaction** → may have → **Offer**  
**Transaction** → creates → **Subscription**

**Subscription** → may be in → **Activation Queue**  
**Subscription** → may have → **Active Topups**

---

## 6. Data Flow Diagrams

### 6.1 Customer Registration & First Recharge Flow

```
Customer → Register → FastAPI
                        │
                        ▼
                   Validate Input
                   (Phone, Password)
                        │
                        ▼
                   Check Referral Code
                   (Optional)
                        │
                        ▼
                   Create Customer
                   (Hash Password)
                        │
                        ▼
                   Apply Referral Code
                   (If provided)
                        │
                        ▼
                   Return JWT Token
                        │
Customer ← ─────────────┘
   │
   ├─→ Browse Plans
   │
   ├─→ Select Plan + Offer
   │
   └─→ Recharge → Validate Plan
                        │
                        ▼
                   Check Referral Discount
                   (10% for first recharge)
                        │
                        ▼
                   Calculate Final Amount
                   (Offer or Referral)
                        │
                        ▼
                   Create Transaction
                        │
                        ▼
                   Create Subscription
                   (Immediate activation)
                        │
                        ▼
                   Complete Referral
                   (If applicable)
                        │
                        ▼
                   Create 30% Discount
                   (For referrer)
                        │
                        ▼
                   Send Notifications
                   (Payment Success)
                        │
                        ▼
                   Return Success
```

### 6.2 Subscription Queue Processing Flow

```
Customer → Recharge (with active plan) → FastAPI
                                           │
                                           ▼
                                    Check Active Plans
                                    (For phone number)
                                           │
                                           ▼
                                    Create Subscription
                                    (Future activation)
                                           │
                                           ▼
                                    Add to Queue
                                    (Position based on expiry)
                                           │
                                           ▼
                                    Send Queue Notification

Background Task (Hourly) ─────────────────┘
                │
                ▼
        Check Expired Plans
                │
                ▼
        Delete Expired Base Plans
                │
                ▼
        Process Queue
                │
                ▼
        Activate Next in Queue
                │
                ▼
        Update Queue Positions
                │
                ▼
        Send Activation Notification
```

### 6.3 Postpaid Bill Payment Flow

```
Customer → View Bill → FastAPI
                         │
                         ▼
                    Get Activation
                    (Billing cycle data)
                         │
                         ▼
                    Calculate Total
                    (Base + Addons)
                         │
                         ▼
                    Return Bill Details
                         │
Customer ← ──────────────┘
   │
   └─→ Pay Bill → Validate Cycle End
                         │
                         ▼
                    Check Outstanding
                         │
                         ▼
                    Create Transaction
                         │
                         ▼
                    Update Activation
                    (Status = Completed)
                         │
                         ▼
                    Expire Addons
                         │
                         ▼
                    Send Notification
                         │
                         ▼
                    Return Success
```

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
1. User Login → POST /customer/login or /admin/login
   ├─ Validate credentials
   ├─ Generate JWT access token (30 min)
   ├─ Add user_type claim (admin/customer)
   └─ Return token

2. Protected Request → Header: Authorization: Bearer {token}
   ├─ Middleware validates JWT
   ├─ Extract user_id and user_type
   ├─ Verify user exists in database
   ├─ Check role permissions
   └─ Process request or return 401/403
```

### 7.2 Authorization Matrix

| Resource      | Admin       | Customer  |
| ------------- | ----------- | --------- |
| Customer Data | Full Access | Self Only |
| Plans         | Manage      | View      |
| Transactions  | View All    | Own Only  |
| Subscriptions | View All    | Own Only  |
| Postpaid      | Manage All  | Own Only  |
| Referrals     | View All    | Own Only  |
| Notifications | Send All    | View Own  |
| Analytics     | Full Access | None      |
| Backups       | Manage      | None      |
| CMS           | Manage      | View      |

### 7.3 Security Measures

- **Password Storage**: bcrypt hashing with salt
- **API Security**: JWT with 30-minute expiration
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries
- **CORS Configuration**: Whitelist allowed origins
- **Audit Logging**: Transaction and subscription logs
- **Role Validation**: Every protected route checks user_type

---

## 8. Deployment Architecture

### 8.1 Production Environment

```
                    ┌──────────────┐
                    │  Cloud CDN   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Load Balancer│
                    │  (nginx/ALB) │
                    └──────┬───────┘
                           │
        ┌──────────────────┼────────────────┐
        │                  │                │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │FastAPI  │       │FastAPI  │       │FastAPI  │
   │Instance1│       │Instance2│       │Instance3│
   │(Docker) │       │(Docker) │       │(Docker) │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                  │                │
        └──────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │  (Primary)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │  (Replica)   │
                    └──────────────┘

                    ┌──────────────┐
                    │   MongoDB    │
                    │   (CMS)      │
                    └──────────────┘
```

### 8.2 Infrastructure Components

- **Application Servers**: Docker containers on Kubernetes/ECS
- **Database**: PostgreSQL with read replicas
- **NoSQL**: MongoDB for CMS content
- **File Storage**: Local/S3 for backups
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging to files

---

## 9. API Architecture Patterns

### 9.1 RESTful Design Principles

- Resource-based URLs (`/customer/profile`, `/admin/plans`)
- HTTP methods for CRUD (GET, POST, PUT, DELETE, PATCH)
- Stateless communication
- JSON request/response format
- No API versioning in URLs (future: `/api/v1/`)

### 9.2 Response Format Standard

```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully"
}
```

**Error Response:**

```json
{
  "detail": "Error message here"
}
```

---

## 10. Performance Considerations

### 10.1 Optimization Strategies

- **Database Indexing**: Primary keys, foreign keys, phone numbers, transaction dates
- **Query Optimization**: Eager loading with `joinedload()`, avoid N+1 queries
- **Pagination**: Default 100 records per page
- **Background Tasks**: Hourly subscription processing, notification delivery
- **Connection Pooling**: SQLAlchemy connection reuse

### 10.2 Scalability

- **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
- **Database Scaling**: Read replicas for reporting queries
- **Caching**: Consider Redis for frequently accessed plans/offers
- **Async Operations**: Background tasks for heavy operations

---

## 11. Monitoring & Observability

### 11.1 Key Metrics

- API response times per endpoint
- Request success/failure rates
- Database query performance
- Active subscriptions count
- Transaction volume and revenue
- Notification delivery rates

### 11.2 Logging Strategy

- **Application Logs**: INFO, WARNING, ERROR levels
- **Access Logs**: All API requests with timestamps
- **Transaction Logs**: All financial transactions
- **Notification Logs**: SMS simulation in console format

---

## 12. Background Services

### 12.1 Automated Tasks

1. **Subscription Expiry Processing** (Hourly)

   - Delete expired base plans
   - Activate queued subscriptions
   - Update queue positions
   - Send activation notifications

2. **Notification Triggers** (Hourly)

   - Plan expiry warnings (24h before)
   - Low balance alerts (< 200MB)
   - Postpaid bill reminders (3 days before)

3. **Data Usage Tracking**

   - Daily data limit resets
   - Usage monitoring
   - Balance calculations

4. **Backup Service**
   - Scheduled automated backups
   - Backup rotation (max 50)
   - Essential data extraction

---

## 13. Integration Points

### 13.1 External Systems

**Future Integrations:**

- Payment Gateway (Razorpay, Stripe)
- SMS Provider (Twilio, AWS SNS)
- Push Notification Service (FCM, APNs)
- Analytics Platform (Google Analytics)

### 13.2 Internal Services

- **Notification Service**: Handles SMS/Push delivery
- **Subscription Service**: Queue and lifecycle management
- **Referral Service**: Code generation and tracking
- **Backup Service**: Automated backup/restore

---

## 14. Future Enhancements

- Real-time WebSocket notifications
- Mobile app API optimizations
- Advanced analytics dashboard
- ML-based plan recommendations
- Automated customer support chatbot
- International roaming plans
- Bill payment reminders via email
- Customer loyalty rewards system
- Multi-language support
- Integration with telecom provider APIs

---

## 15. Technology Stack Summary

| Layer            | Technology         | Purpose                 |
| ---------------- | ------------------ | ----------------------- |
| API Framework    | FastAPI 0.104.1+   | RESTful API server      |
| Language         | Python 3.11+       | Backend logic           |
| ORM              | SQLAlchemy 2.0.23+ | Database abstraction    |
| SQL Database     | PostgreSQL 15+     | Primary data store      |
| NoSQL Database   | MongoDB 4.5+       | CMS content             |
| Authentication   | JWT + bcrypt       | Security                |
| Validation       | Pydantic 2.5.0+    | Input validation        |
| Migration        | Alembic 1.12.1+    | Database versioning     |
| Server           | Uvicorn 0.24.0+    | ASGI server             |
| Documentation    | OpenAPI/Swagger    | Auto-generated API docs |
| Containerization | Docker             | Deployment packaging    |

---

## 16. Development Guidelines

### 16.1 Code Structure

```
app/
├── core/                  # Core functionality
│   ├── auth.py            # Authentication dependencies
│   ├── security.py        # JWT & password hashing
│   └── config.py          # Configuration
├── crud/                  # Database operations
│   ├── crud_customer.py
│   ├── crud_plan.py
│   └── ...
├── models/                # SQLAlchemy models
│   └── models.py
├── routes/                # API endpoints
│   ├── auth.py
│   ├── customer.py
│   └── admin.py
├── schemas/               # Pydantic models
│   ├── customer.py
│   └── ...
├── services/              # Business logic
│   ├── subscription_service.py
│   └── notification_service.py
├── utils/                 # Helpers
│   └── mongo_utils.py
├── database.py            # DB connection
├── mongo.py               # MongoDB connection
└── main.py                # FastAPI app
```

### 16.2 Best Practices

- Use type hints throughout codebase
- Comprehensive error handling with try-except
- Database transactions for data consistency
- Dependency injection for services
- Background tasks for heavy operations
- Structured logging for debugging
- Pydantic validation for all inputs

---

**Document Version**: 1.0  
**Last Updated**: November 24, 2025  
**Author**: Vruthika L S  
**Contact**: vruthikasan@gmail.com
