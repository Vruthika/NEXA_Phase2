# NEXA Mobile Recharge System

A scalable **FastAPI-based backend system** designed to manage end-to-end mobile recharge services including prepaid subscriptions, postpaid billing, top-ups, referral rewards, customer management, notifications, payments, analytics, and CMS content control.

The platform supports secure authentication using JWT, real-time notification handling, dynamic CMS content via MongoDB, automated background tasks, and disaster-recovery backup/restore.

This backend powers both customer applications and admin dashboards, following a modular service-driven architecture built for production-grade performance.

---

## 🚀 Core Features

### 👥 Customer Management

- Secure registration and authentication with JWT
- Profile management with password change
- Account status tracking (active/inactive/suspended)
- Inactivity monitoring and notifications
- Multi-address support through linked accounts

### 📱 Prepaid Services

- Browse and filter prepaid plans by category and type
- View active offers with discount calculations
- Recharge with offer and referral discount support
- Subscription activation and queue management
- Top-up data plans with instant activation
- Data usage tracking with daily limits

### 💳 Postpaid Services

- Postpaid plan activation with billing cycles
- Secondary number management (family plans)
- Data addon purchases
- Bill generation and payment processing
- Usage monitoring and alerts

### 🔗 Linked Accounts

- Add family members/friends to account
- Recharge for linked numbers
- Track spending per linked account
- Subscription management for linked accounts

### 🎁 Referral Program

- Generate unique referral codes
- 10% discount for referee on first recharge
- 30% discount for referrer after referee's first recharge
- Track referral usage and earnings

### 🔔 Notifications

- Real-time SMS and push notifications
- Automated alerts for:
  - Plan expiry reminders
  - Low balance warnings (< 200MB)
  - Payment confirmations
  - Referral bonuses
  - Plan activation/queuing
  - Postpaid bill due dates

### 📊 Admin Dashboard

- Customer management and monitoring
- Transaction tracking and filtering
- Plan and offer management
- Subscription queue monitoring
- Analytics and reporting
- Backup and restore functionality

### 🎨 CMS Management

- Dynamic header content
- Carousel management for featured plans
- FAQ management with ordering
- MongoDB-based flexible content

---

## 🛠 Technology Stack

| Component        | Technology   | Version  |
| ---------------- | ------------ | -------- |
| Framework        | FastAPI      | 0.104.1+ |
| Language         | Python       | 3.11+    |
| Database (SQL)   | PostgreSQL   | 15+      |
| Database (NoSQL) | MongoDB      | 4.5+     |
| ORM              | SQLAlchemy   | 2.0.23+  |
| Validation       | Pydantic     | 2.5.0+   |
| Authentication   | JWT + bcrypt | -        |
| Server           | Uvicorn      | 0.24.0+  |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **MongoDB 4.5+** - [Download MongoDB](https://www.mongodb.com/try/download/community)
- **pip** - Python package installer (comes with Python)
- **Virtual Environment Tool** - venv or virtualenv

---

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Vruthika/NEXA_Phase2
cd nexa-mobile-recharge
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Setup

```bash
# Create database
psql -U postgres
CREATE DATABASE nexa_recharge;
\q
```

#### MongoDB Setup

```bash
# Start MongoDB service
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### 5. Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/nexa_recharge
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=nexa_cms

# JWT Configuration
SECRET_KEY=your-secret-key-here-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
ENVIRONMENT=development
APP_NAME=NEXA Mobile Recharge System
APP_VERSION=1.0.0

# Admin Default Credentials
ADMIN_DEFAULT_NAME=Super Admin
ADMIN_DEFAULT_EMAIL=admin@nexa.com
ADMIN_DEFAULT_PASSWORD=admin123

# API Settings
API_V1_PREFIX=/api/v1
DOCS_URL=/docs
REDOC_URL=/admin/redoc

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Backup Settings
MAX_BACKUPS=50
BACKUP_DIR=backups
DEFAULT_BACKUP_TIME=02:00
```

## 🚀 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points

- **Main Application**: http://localhost:8000
- **Swagger UI (API Docs)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/admin/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs

  - Interactive API explorer
  - Test endpoints directly
  - View request/response schemas

- **ReDoc**: http://localhost:8000/admin/redoc
  - Clean, readable documentation
  - Better for reference

### Base URL

```
Development: http://localhost:8000
Production: https://api.nexa.com
```

### Authentication

All protected endpoints require JWT token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

---

## 📁 Project Structure

```
nexa-mobile-recharge/
├── app/
│   ├── core/                  # Core functionality (auth, security, config)
│   │   ├── auth.py            # Authentication dependencies
│   │   └── security.py        # JWT and password hashing
│   ├── crud
│   │   ├── __init__.py
│   │   ├── crud_admin.py
│   │   ├── crud_backup_restore.py
│   │   ├── crud_category.py
│   │   ├── crud_customer.py
│   │   ├── crud_linked_account.py
│   │   ├── crud_notification.py
│   │   ├── crud_offer.py
│   │   ├── crud_plan.py
│   │   ├── crud_postpaid.py
│   │   ├── crud_referral.py
│   │   ├── crud_subscription.py
│   │   ├── crud_token.py
│   │   └── crud_transaction.py
│   ├── middleware
│   │   ├── __init__.py
│   │   ├── error_handling.py
│   │   ├── logging_middleware.py
│   │   ├── rate_limiting.py
│   │   └── security_headers.py
│   ├── models/                # SQLAlchemy models
│   │   └── models.py
│   ├── routes                 # API Endpoints
│   │   ├── admin.py
│   │   ├── admin_analytics.py
│   │   ├── admin_backup_restore.py
│   │   ├── admin_cms.py
│   │   ├── admin_linked_accounts.py
│   │   ├── admin_notifications.py
│   │   ├── admin_postpaid.py
│   │   ├── admin_referral.py
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── customer_cms.py
│   │   ├── customer_linked_accounts.py
│   │   ├── customer_notifications.py
│   │   ├── customer_postpaid.py
│   │   └── customer_referral.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── analytics.py
│   │   ├── backup_restore.py
│   │   ├── category.py
│   │   ├── cms.py
│   │   ├── customer.py
│   │   ├── customer_operations.py
│   │   ├── linked_account.py
│   │   ├── notification.py
│   │   ├── offer.py
│   │   ├── plan.py
│   │   ├── postpaid.py
│   │   ├── referral.py
│   │   ├── token.py
│   │   └── transaction.py
│   ├── services/              # Business logic
│   │   ├── automated_notifications.py
│   │   ├── background_tasks.py
│   │   ├── backup_scheduler.py
│   │   ├── backup_service.py
│   │   ├── notification_service.py
│   │   └── subscription_service.py
│   ├── utils/                 # Helper utilities
│   │   └── mongo_utils.py
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection
│   ├── mongo.py               # MongoDB connection
│   └── main.py                # FastAPI application
├── backups/                   # Backup files
├── docs/                      # Documentation
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🔐 Authentication Flow

1. **Register/Login** → User authenticates with phone number and password
2. **Token Issuance** → System returns JWT access token
3. **Token Usage** → Include token in Authorization header for protected routes
4. **Token Expiry** → Tokens expire after 30 minutes (configurable)
5. **Logout** → User logs out, token is invalidated

### Quick Authentication Example

```bash
# Login (Customer)
curl -X POST "http://localhost:8000/customer/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "1234567890", "password": "password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}

# Use token in subsequent requests
curl -X GET "http://localhost:8000/customer/profile" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

## 📍 API Endpoints (Quick Reference)

### Authentication

- `POST /admin/login` - Admin login
- `POST /customer/register` - Customer registration
- `POST /customer/login` - Customer login
- `POST /refresh` - Refresh Token
- `POST /logout` - Logout

### Customer - Profile

- `GET /customer/profile` - Get profile
- `PUT /customer/profile` - Update profile
- `POST /customer/change-password` - Change password

### Customer - Plans & Offers

- `GET /customer/categories` - Category details
- `GET /customer/plans` - Plan details
- `GET /customer/offers` - View offers

### Customer - Recharge

- `POST /customer/recharge` - Create recharge
- `GET /customer/transactions` - Transaction history
- `GET /customer/subscriptions/active` - Active subscriptions
- `GET /customer/subscriptions/queue` - Queued subscriptions

### Customer - Postpaid

- `GET /customer/postpaid/plans` - Browse postpaid plans
- `POST /customer/postpaid/activate` - Activate postpaid
- `GET /customer/postpaid/bill` - View bill
- `POST /customer/postpaid/pay-bill` - Pay bill
- `POST /customer/postpaid/purchase-addon` - Buy data addon
- `POST /customer/postpaid/secondary-numbers` - Add secondary number

### Customer - Referral

- `POST /customer/referral/generate` - Generate referral code
- `GET /customer/referral/my-referrals` - View referral stats
- `GET /customer/referral/discounts` - View available discounts

### Customer - Notifications

- `GET /customer/notifications` - Get notifications
- `GET /customer/notifications/stats` - Notification statistics
- `POST /customer/notifications/mark-read` - Mark as read

### Admin - Management

- `GET /admin/customers` - Manage customers
- `GET /admin/transactions` - View transactions
- `POST /admin/plans` - Create plan
- `POST /admin/offers` - Create offer
- `GET /admin/dashboard` - Dashboard stats

### Admin - Analytics

- `GET /admin/analytics/dashboard` - Dashboard analytics
- `GET /admin/analytics/revenue` - Revenue analytics
- `GET /admin/analytics/customers/growth` - Customer growth
- `GET /admin/analytics/referrals/trend` - Referral trends

### Admin - CMS

- `POST /admin/cms/headers` - Manage headers
- `POST /admin/cms/carousels` - Manage carousels
- `POST /admin/cms/faqs` - Manage FAQs

---

## ⚠️ Common Issues & Troubleshooting

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:

- Ensure PostgreSQL is running
- Check DATABASE_URL in `.env`
- Verify database exists

### MongoDB Connection Error

```
pymongo.errors.ServerSelectionTimeoutError
```

**Solution**:

- Start MongoDB service
- Check MONGODB_URL in `.env`
- Verify MongoDB is accessible

### Port Already in Use

```
ERROR: [Errno 48] Address already in use
```

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

---

## 📖 Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical fixes

### Commit Messages

```
feat: Add referral program functionality
fix: Resolve subscription queue processing
docs: Update API documentation
refactor: Improve notification service
```

---

## 📞 Contact & Support

**Developer**: Vruthika L S

**Email**: vruthikasan@gmail.com

**GitHub**: [https://github.com/Vruthika](https://github.com/Vruthika)

**Project Repository**: [https://github.com/Vruthika/NEXA_Phase2](https://github.com/Vruthika/NEXA_Phase2)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- SQLAlchemy for robust ORM
- Pydantic for data validation
- All contributors and supporters

---

**Made with ❤️ by Vruthika L S**
