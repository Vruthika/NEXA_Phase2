# Mobile Recharge System — API Documentation

**Version:** 1.0

**Base URL (dev):** `http://127.0.0.1:8000/docs`

**Framework:** FastAPI

**Content Type:** `application/json`

**Authentication:** JWT Bearer Token (`Authorization: Bearer <access_token>`)

**Last Updated:** 18-Nov-2025

---

## Table of contents

1. Overview
2. Authentication (auth)
3. Admin Management
4. Category Management
5. Plan Management
6. Offer Management
7. Transaction Monitoring
8. Subscription Management
9. Customer Management
10. Analytics & Reports
11. Admin - Backup & Restore
12. Admin - CMS Management
13. Admin - Linked Accounts
14. Admin Notifications
15. Postpaid Management
16. Referral Management
17. Customer Operations
18. Customer CMS
19. Customer Linked Accounts
20. Customer Notifications
21. Customer Postpaid
22. Customer Referral
23. Common errors & standard response format
24. Examples & Auth flow
25. Pagination & filtering conventions

---

## 1. Overview

This API powers a comprehensive Mobile Recharge and Postpaid Management System. Responsibilities:

- Admin panel for complete system management
- Customer registration and authentication
- Prepaid and postpaid plan management
- Recharge transactions and subscription handling
- Referral programs and discount management
- CMS for marketing content management
- Analytics and reporting
- Backup and restore operations
- Notification system

---

## 2. Authentication (auth)

### POST `/auth/admin/login` — Admin Login

**Auth:** No
**Content-Type:** `application/json`
**Body:**

```json
{
  "email": "admin@nexa.com",
  "password": "admin123"
}
```

**Success (200):**

```json
{
  "access_token": "<jwt_access>",
  "refresh_token": "<jwt_refresh>",
  "token_type": "bearer"
}
```

**Errors:** `401` invalid credentials

---

### POST `/auth/customer/login` — Customer Login

**Auth:** No
**Body:**

```json
{
  "phone_number": "9876543210",
  "password": "customer123"
}
```

**Success (200):**

```json
{
  "access_token": "<jwt_access>",
  "refresh_token": "<jwt_refresh>",
  "token_type": "bearer"
}
```

**Errors:** `401` invalid credentials

---

### POST `/auth/customer/register` — Customer Registration

**Auth:** No
**Body:**

```json
{
  "phone_number": "9876543210",
  "password": "customer123",
  "full_name": "John Doe",
  "profile_picture_url": "https://example.com/avatar.jpg",
  "referral_code": "REF123"
}
```

**Success (200):**

```json
{
  "customer_id": 1,
  "phone_number": "9876543210",
  "full_name": "John Doe",
  "account_status": "active",
  "profile_picture_url": "https://example.com/avatar.jpg",
  "last_active_plan_date": null,
  "days_inactive": 0,
  "created_at": "2025-11-18T12:00:00Z",
  "updated_at": "2025-11-18T12:00:00Z"
}
```

**Errors:** `400` phone number already registered

---

### POST `/auth/refresh` — Refresh Token

**Auth:** Bearer (refresh token)
**Body:**

```json
{
  "refresh_token": "<jwt_refresh>"
}
```

**Success (200):**

```json
{
  "access_token": "<new_jwt_access>",
  "token_type": "bearer"
}
```

**Errors:** `401` invalid/revoked refresh token

---

### POST `/auth/logout` — Logout

**Auth:** Bearer (access token)
**Success (200):**

```json
{
  "message": "Successfully logged out"
}
```

---

## 3. Admin Management

> **Permissions:** Admin only (Bearer token with admin role)

### POST `/admins/` — Create Admin

**Auth:** Bearer (admin)
**Body:**

```json
{
  "name": "New Admin",
  "phone_number": "9876543211",
  "email": "newadmin@nexa.com",
  "password": "admin123"
}
```

**Success (200):**

```json
{
  "admin_id": 2,
  "name": "New Admin",
  "phone_number": "9876543211",
  "email": "newadmin@nexa.com",
  "created_at": "2025-11-18T12:00:00Z",
  "updated_at": "2025-11-18T12:00:00Z"
}
```

---

### GET `/admins/` — Get All Admins or Specific Admin

**Auth:** Bearer (admin)
**Query Params:** `admin_id` (optional)

**Success (200):** List of admin objects or single admin

---

### PUT `/admins/{admin_id}` — Update Admin

**Auth:** Bearer (admin)
**Body:** (Partial fields)

```json
{
  "name": "Updated Admin Name",
  "phone_number": "9876543222"
}
```

**Success (200):** Updated admin object

---

### POST `/admins/change-password` — Change Admin Password

**Auth:** Bearer (admin)
**Query Params:** `current_password`, `new_password`

**Success (200):**

```json
{
  "message": "Password changed successfully"
}
```

---

## 4. Category Management

### POST `/categories/` — Create Category

**Auth:** Bearer (admin)
**Body:**

```json
{
  "category_name": "Data Plans"
}
```

**Success (200):**

```json
{
  "category_id": 1,
  "category_name": "Data Plans",
  "created_at": "2025-11-18T12:00:00Z"
}
```

---

### GET `/categories/` — Get All Categories

**Auth:** Bearer (admin)
**Success (200):** List of category objects

---

### PUT `/categories/{category_id}` — Update Category

**Auth:** Bearer (admin)
**Body:**

```json
{
  "category_name": "Updated Category Name"
}
```

**Success (200):** Updated category object

---

### DELETE `/categories/{category_id}` — Delete Category

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Category deleted successfully"
}
```

---

## 5. Plan Management

### POST `/plans/` — Create Plan

**Auth:** Bearer (admin)
**Body:**

```json
{
  "category_id": 1,
  "plan_name": "1.5GB/day 84 Days Pack",
  "plan_type": "prepaid",
  "is_topup": false,
  "price": 755.0,
  "validity_days": 84,
  "description": "1.5GB data per day for 84 days",
  "data_allowance_gb": 126.0,
  "daily_data_limit_gb": 1.5,
  "talktime_allowance_minutes": 0,
  "sms_allowance": 100,
  "benefits": ["Unlimited calls", "100 SMS/day"],
  "max_secondary_numbers": 0,
  "is_featured": true
}
```

**Success (200):** Created plan object

---

### GET `/plans/` — Get All Plans or Specific Plan

**Auth:** Bearer (admin)
**Query Params:** `plan_id`, `plan_type`, `category_id`, `status`

**Success (200):** List of plan objects or single plan

---

### PUT `/plans/{plan_id}` — Update Plan

**Auth:** Bearer (admin)
**Body:** (Partial fields)

```json
{
  "price": 699.0,
  "is_featured": false
}
```

**Success (200):** Updated plan object

---

### POST `/plans/{plan_id}/activate` — Activate Plan

**Auth:** Bearer (admin)
**Success (200):** Activated plan object

---

### POST `/plans/{plan_id}/deactivate` — Deactivate Plan

**Auth:** Bearer (admin)
**Success (200):** Deactivated plan object

---

### DELETE `/plans/{plan_id}` — Delete Plan

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Plan deleted successfully"
}
```

---

## 6. Offer Management

### POST `/offers/` — Create Offer (Direct Price)

**Auth:** Bearer (admin)
**Body:**

```json
{
  "plan_id": 1,
  "offer_name": "Summer Special",
  "description": "Limited time summer discount",
  "discounted_price": 699.0,
  "valid_from": "18.11.2025 00:00",
  "valid_until": "25.11.2025 23:59"
}
```

**Success (200):** Created offer object

---

### POST `/offers/create-with-discount` — Create Offer (Percentage Discount)

**Auth:** Bearer (admin)
**Body:**

```json
{
  "plan_id": 1,
  "offer_name": "Diwali Discount",
  "description": "Festival special discount",
  "discount_percentage": 15.0,
  "valid_from": "18.11.2025 00:00",
  "valid_until": "20.11.2025 23:59"
}
```

**Success (200):** Created offer object

---

### GET `/offers/calculate-discount` — Calculate Discount Preview

**Auth:** Bearer (admin)
**Query Params:** `plan_id`, `discount_percentage`

**Success (200):**

```json
{
  "original_price": 755.0,
  "discount_percentage": 15.0,
  "discounted_price": 641.75,
  "amount_saved": 113.25
}
```

---

### GET `/offers/` — Get All Offers or Specific Offer

**Auth:** Bearer (admin)
**Query Params:** `offer_id`, `plan_id`, `status`

**Success (200):** List of offer objects or single offer

---

### GET `/offers/active` — Get Active Offers

**Auth:** Bearer (admin)
**Success (200):** List of active offer objects

---

### PUT `/offers/{offer_id}` — Update Offer

**Auth:** Bearer (admin)
**Body:** (Partial fields)

```json
{
  "discounted_price": 649.0,
  "valid_until": "30.11.2025 23:59"
}
```

**Success (200):** Updated offer object

---

### DELETE `/offers/{offer_id}` — Delete Offer

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Offer deleted successfully"
}
```

---

## 7. Transaction Monitoring

### GET `/transactions/` — Get All Transactions or Specific Transaction

**Auth:** Bearer (admin)
**Query Params:** `transaction_id`, `customer_id`, `customer_phone`, `plan_id`, `transaction_type`, `payment_status`, `payment_method`, `date_from`, `date_to`

**Success (200):** List of transaction objects with customer and plan details

---

### POST `/transactions/export` — Export Transactions to CSV

**Auth:** Bearer (admin)
**Success (200):** CSV file download

---

## 8. Subscription Management

### GET `/subscriptions/active` — Get Active Subscriptions

**Auth:** Bearer (admin)
**Query Params:** `customer_id` (optional)

**Success (200):** List of active subscription objects with customer and plan details

---

### GET `/subscriptions/queue` — Get Activation Queue

**Auth:** Bearer (admin)
**Query Params:** `customer_id` (optional)

**Success (200):** List of queued subscription objects

---

## 9. Customer Management

### GET `/customers/` — Get All Customers or Specific Customer

**Auth:** Bearer (admin)
**Query Params:** `customer_id`, `phone_number`, `full_name`, `account_status`, `days_inactive_min`, `days_inactive_max`, `search_term`

**Success (200):** List of customer objects or detailed customer object

---

### GET `/customers/stats` — Get Customer Statistics

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "total_customers": 150,
  "active_customers": 120,
  "inactive_customers": 25,
  "suspended_customers": 5,
  "new_customers_today": 3,
  "new_customers_this_week": 15
}
```

---

### POST `/customers/{customer_id}/deactivate` — Deactivate Customer

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Customer account deactivated successfully",
  "customer_id": 1
}
```

---

## 10. Analytics & Reports

### GET `/analytics/dashboard` — Get Dashboard Analytics

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "today": {
    "revenue": "₹2,500.00",
    "new_customers": 5
  },
  "overview": {
    "total_customers": 150,
    "total_transactions": 1200,
    "total_revenue": "₹1,50,000.00"
  },
  "top_plans": [
    {
      "name": "1.5GB/day 84 Days Pack",
      "transactions": 45,
      "revenue": "₹33,975.00"
    }
  ]
}
```

---

### GET `/analytics/revenue` — Get Revenue Analytics

**Auth:** Bearer (admin)
**Query Params:** `period` (daily, weekly, monthly), `days` (default: 30)

**Success (200):** List of revenue trend data

---

### GET `/analytics/customers/growth` — Get Customer Growth Analytics

**Auth:** Bearer (admin)
**Query Params:** `days` (default: 90)

**Success (200):** List of customer growth data

---

### GET `/analytics/referrals/trend` — Get Referral Trend Analytics

**Auth:** Bearer (admin)
**Query Params:** `days` (default: 90)

**Success (200):** List of referral trend data

---

### GET `/analytics/plans/performance` — Get Plan Performance

**Auth:** Bearer (admin)
**Query Params:** `limit` (default: 10)

**Success (200):** List of top performing plans

---

## 11. Admin - Backup & Restore

### POST `/backup-restore/backup/manual` — Create Manual Backup

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "backup_id": 1,
  "admin_id": 1,
  "file_name": "backup_20251118_120000.json",
  "path": "/backups/backup_20251118_120000.json",
  "type": "manual",
  "data_list": { "tables": ["customers", "plans", "transactions"] },
  "date": "2025-11-18",
  "message": "Backup created successfully with 2048 bytes of data"
}
```

---

### GET `/backup-restore/backup` — Get Backup History

**Auth:** Bearer (admin)
**Query Params:** `skip`, `limit`, `backup_type`

**Success (200):** List of backup objects

---

### POST `/backup-restore/backup/schedule` — Set Backup Schedule

**Auth:** Bearer (admin)
**Body:**

```json
{
  "frequency": "daily",
  "time_of_day": "02:00"
}
```

**Success (200):**

```json
{
  "success": true,
  "message": "Backup schedule set to daily at 02:00",
  "next_run": "2025-11-19T02:00:00Z"
}
```

---

### POST `/backup-restore/restore/{backup_id}` — Restore From Backup

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "restore_id": 1,
  "admin_id": 1,
  "file_name": "backup_20251118_120000.json",
  "path": "/backups/backup_20251118_120000.json",
  "type": "manual",
  "data_list": { "tables_restored": ["customers", "plans"] },
  "date": "2025-11-18",
  "message": "Restore process initiated successfully"
}
```

---

### DELETE `/backup-restore/backup/{backup_id}` — Delete Backup

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Backup deleted successfully"
}
```

---

## 12. Admin - CMS Management

### POST `/cms/headers` — Create Header Banner

**Auth:** Bearer (admin)
**Body:**

```json
{
  "title": "Special Offer",
  "description": "Get 50% off on all plans",
  "button_text": "Shop Now",
  "image_url": "https://example.com/banner.jpg"
}
```

**Success (200):** Created header object

---

### GET `/cms/headers` — Get All Headers

**Auth:** Bearer (admin)
**Success (200):** List of header objects

---

### PUT `/cms/headers/{header_id}` — Update Header

**Auth:** Bearer (admin)
**Body:** (Partial fields)

```json
{
  "title": "Updated Offer",
  "button_text": "Buy Now"
}
```

**Success (200):** Updated header object

---

### POST `/cms/carousels` — Create Carousel Item

**Auth:** Bearer (admin)
**Body:**

```json
{
  "title": "Data Plans",
  "details": "Best data plans starting at ₹299",
  "price_text": "From ₹299",
  "category_id": "1",
  "image_url": "https://example.com/carousel1.jpg",
  "cta_text": "View Plans",
  "order": 1
}
```

**Success (200):** Created carousel object

---

### GET `/cms/carousels` — Get All Carousels

**Auth:** Bearer (admin)
**Success (200):** List of carousel objects

---

### POST `/cms/faqs` — Create FAQ Item

**Auth:** Bearer (admin)
**Body:**

```json
{
  "question": "How to recharge my number?",
  "answer": "You can recharge through the app or website",
  "image_url": "https://example.com/faq1.jpg",
  "order": 1
}
```

**Success (200):** Created FAQ object

---

### GET `/cms/overview` — Get Complete CMS Overview

**Auth:** Bearer (admin)
**Success (200):** Complete CMS data including headers, carousels, and FAQs

---

## 13. Admin - Linked Accounts

### GET `/linked-accounts/` — Get All Linked Accounts

**Auth:** Bearer (admin)
**Query Params:** `primary_customer_id`, `linked_phone`

**Success (200):** List of linked account objects

---

### GET `/linked-accounts/customer/{customer_id}` — Get Customer Linked Relationships

**Auth:** Bearer (admin)
**Success (200):** Customer's linked account relationships

---

### DELETE `/linked-accounts/{linked_account_id}` — Remove Linked Account

**Auth:** Bearer (admin)
**Success (200):**

```json
{
  "message": "Linked account relationship removed successfully by admin"
}
```

---

## 14. Admin Notifications

### GET `/notifications/` — Get All Notifications

**Auth:** Bearer (admin)
**Query Params:** `customer_id`, `notification_type`, `channel`, `status`

**Success (200):** List of notification objects

---

### POST `/notifications/send` — Send Admin Notification

**Auth:** Bearer (admin)
**Body:**

```json
{
  "title": "Maintenance Notice",
  "message": "System maintenance scheduled for tomorrow",
  "type": "promotional",
  "channel": "push",
  "customer_ids": [1, 2, 3],
  "send_to_all": false
}
```

**Success (200):** Notification send results

---

### GET `/notifications/stats` — Get Notification Statistics

**Auth:** Bearer (admin)
**Success (200):** System-wide notification statistics

---

## 15. Postpaid Management

### GET `/postpaid/activations` — Get Postpaid Activations

**Auth:** Bearer (admin)
**Query Params:** `activation_id`, `plan_id`, `status`, `customer_phone`, `date_from`, `date_to`

**Success (200):** List of postpaid activation objects

---

### GET `/postpaid/due-payments` — Get Due Payments

**Auth:** Bearer (admin)
**Success (200):** List of activations with due payments

---

### GET `/postpaid/customer-history/{customer_id}` — Get Customer Postpaid History

**Auth:** Bearer (admin)
**Success (200):** Detailed postpaid history for specific customer

---

## 16. Referral Management

### GET `/admin/referrals/` — Get All Referral Programs

**Auth:** Bearer (admin)
**Query Params:** `status`, `is_active`, `skip`, `limit`

**Success (200):** List of referral program objects

---

### GET `/admin/referrals/stats/overview` — Get Referral Overview Statistics

**Auth:** Bearer (admin)
**Success (200):** System referral statistics

---

### GET `/admin/referrals/customer/{customer_id}/referrals` — Get Customer Referral Details

**Auth:** Bearer (admin)
**Success (200):** Detailed referral information for specific customer

---

## 17. Customer Operations

### GET `/customer/profile` — Get Customer Profile

**Auth:** Bearer (customer)
**Success (200):** Customer profile object

---

### PUT `/customer/profile` — Update Customer Profile

**Auth:** Bearer (customer)
**Body:** (Partial fields)

```json
{
  "full_name": "Updated Name",
  "profile_picture_url": "https://example.com/new-avatar.jpg"
}
```

**Success (200):** Updated customer profile

---

### POST `/customer/change-password` — Change Customer Password

**Auth:** Bearer (customer)
**Query Params:** `current_password`, `new_password`

**Success (200):**

```json
{
  "message": "Password changed successfully"
}
```

---

### GET `/customer/plans` — Get Available Plans

**Auth:** Bearer (customer)
**Query Params:** `plan_id`, `plan_type`, `category_id`

**Success (200):** List of plan objects with offer information

---

### GET `/customer/offers` — Get Active Offers

**Auth:** Bearer (customer)
**Query Params:** `plan_id` (optional)

**Success (200):** List of active offer objects

---

### POST `/customer/recharge` — Create Recharge

**Auth:** Bearer (customer)
**Body:**

```json
{
  "plan_id": 1,
  "offer_id": 1,
  "recipient_phone_number": "9876543210",
  "payment_method": "upi"
}
```

**Success (200):**

```json
{
  "transaction_id": 1001,
  "plan_name": "1.5GB/day 84 Days Pack",
  "final_amount": 699.0,
  "payment_status": "success",
  "message": "Recharge successful! Your plan is now active."
}
```

---

### GET `/customer/transactions` — Get Customer Transactions

**Auth:** Bearer (customer)
**Query Params:** `transaction_id` (optional)

**Success (200):** List of transaction objects

---

### GET `/customer/subscriptions/active` — Get Active Subscriptions

**Auth:** Bearer (customer)
**Success (200):** List of active subscription objects

---

### GET `/customer/subscriptions/queue` — Get Queued Subscriptions

**Auth:** Bearer (customer)
**Success (200):** List of queued subscription objects

---

## 18. Customer CMS

### GET `/customer/cms/content` — Get CMS Content

**Auth:** Bearer (customer)
**Success (200):** Complete CMS content including headers, carousels, and FAQs

---

### GET `/customer/cms/headers` — Get Headers (Public)

**Auth:** No
**Success (200):** List of header objects

---

### GET `/customer/cms/carousels` — Get Carousels (Public)

**Auth:** No
**Success (200):** List of carousel objects

---

### GET `/customer/cms/faqs` — Get FAQs (Public)

**Auth:** No
**Success (200):** List of FAQ objects

---

## 19. Customer Linked Accounts

### POST `/customer/linked-accounts` — Add Linked Account

**Auth:** Bearer (customer)
**Body:**

```json
{
  "linked_phone_number": "9876543211"
}
```

**Success (200):** Created linked account object

---

### GET `/customer/linked-accounts` — Get Linked Accounts

**Auth:** Bearer (customer)
**Query Params:** `linked_account_id` (optional)

**Success (200):** List of linked account objects

---

### DELETE `/customer/linked-accounts/{linked_account_id}` — Remove Linked Account

**Auth:** Bearer (customer)
**Success (200):**

```json
{
  "message": "Linked account removed successfully"
}
```

---

### POST `/customer/linked-accounts/{linked_account_id}/recharge` — Recharge Linked Account

**Auth:** Bearer (customer)
**Body:**

```json
{
  "plan_id": 1,
  "offer_id": 1,
  "payment_method": "upi"
}
```

**Success (200):** Recharge response for linked account

---

## 20. Customer Notifications

### GET `/customer/notifications/` — Get Customer Notifications

**Auth:** Bearer (customer)
**Query Params:** `unread_only` (default: false)

**Success (200):** List of notification objects

---

### GET `/customer/notifications/stats` — Get Notification Statistics

**Auth:** Bearer (customer)
**Success (200):** Customer notification statistics

---

### POST `/customer/notifications/mark-read` — Mark Notifications as Read

**Auth:** Bearer (customer)
**Body:**

```json
{
  "notification_ids": [1, 2, 3]
}
```

**Success (200):**

```json
{
  "message": "Marked 3 notifications as read"
}
```

---

## 21. Customer Postpaid

### GET `/customer/postpaid/plans` — Get Postpaid Plans

**Auth:** Bearer (customer)
**Query Params:** `plan_id` (optional)

**Success (200):** List of postpaid plan objects

---

### POST `/customer/postpaid/activate` — Activate Postpaid Plan

**Auth:** Bearer (customer)
**Body:**

```json
{
  "plan_id": 5,
  "primary_number": "9876543210"
}
```

**Success (200):** Postpaid activation response

---

### GET `/customer/postpaid/activation` — Get Customer Postpaid Activations

**Auth:** Bearer (customer)
**Success (200):** List of postpaid activation objects

---

### GET `/customer/postpaid/bill` — Get Postpaid Bill

**Auth:** Bearer (customer)
**Success (200):** Postpaid bill details

---

### POST `/customer/postpaid/pay-bill` — Pay Postpaid Bill

**Auth:** Bearer (customer)
**Body:**

```json
{
  "activation_id": 1,
  "payment_method": "upi"
}
```

**Success (200):** Bill payment response

---

### POST `/customer/postpaid/secondary-numbers` — Add Secondary Number

**Auth:** Bearer (customer)
**Body:**

```json
{
  "activation_id": 1,
  "phone_number": "9876543211"
}
```

**Success (200):** Secondary number response

---

## 22. Customer Referral

### POST `/customer/referral/generate` — Generate Referral Code

**Auth:** Bearer (customer)
**Success (200):** Referral program object

---

### GET `/customer/referral/my-referrals` — Get Referral Details

**Auth:** Bearer (customer)
**Success (200):** Referral statistics and details

---

### GET `/customer/referral/discounts` — Get Referral Discounts

**Auth:** Bearer (customer)
**Success (200):** List of active referral discounts

---

## 23. Common errors & standard response format

**Standard wrapper**

```json
{
  "status": "success|error",
  "data": { ... } | null,
  "message": "Human readable message"
}
```

**Common HTTP codes**

- `200` OK
- `201` Created
- `400` Bad Request (validation)
- `401` Unauthorized (token missing/invalid)
- `403` Forbidden (role mismatch)
- `404` Not Found
- `409` Conflict (e.g., duplicate entry)
- `422` Unprocessable Entity (Pydantic validation)
- `500` Server Error

**Example error**

```json
{
  "status": "error",
  "data": null,
  "message": "Could not validate credentials"
}
```

---

## 24. Examples & Auth flow

**Sample Authorization header**

```
Authorization: Bearer <access_token>
```

**Login → Use**

1. `POST auth/admin/login` or `POST auth/customer/login` → receive `access_token` & `refresh_token`
2. Set `Authorization` header for protected requests
3. On `401` caused by expired access token → call `POST /auth/refresh` with refresh token to get a new access token

**Token claims:**

- `sub` — user ID (admin_id or customer_id)
- `user_type` — `admin` | `customer`
- `type` — `access` | `refresh`
- `iat`, `exp`

**Token lifetimes (recommended):**

- Access token — 30 minutes
- Refresh token — 7 days

---

## 25. Pagination & Filtering (conventions)

- Use `?skip=<int>&limit=<int>` for paginated endpoints
- Use specific query parameters for filtering (e.g., `customer_id`, `plan_type`, `status`)
- For date ranges, use `date_from` and `date_to` parameters
- Search functionality available through `search_term` parameter

---

**Notes:**

- All timestamps use UTC format
- Currency amounts are in Indian Rupees (₹)
- Phone numbers follow Indian format (10 digits)
- Input validation follows Pydantic model rules
- File uploads for profile pictures support common image formats (JPEG, PNG, WebP)
