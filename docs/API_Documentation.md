# NEXA Mobile Recharge System
**Version:** 1.0.0
**Generated on:** 2025-11-24 16:13:18

---

API Documentation

---

## Admin - Backup & Restore

### `POST` /admin/backup-restore/backup/manual
**Create Manual Backup**

Create a manual backup of essential system data.

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/backup-restore/backup
**Get Backup History**

Get backup history with filtering options.

**Parameters:**
- `skip` (query) — 
- `limit` (query) — 
- `backup_type` (query) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/backup-restore/backup/schedule
**Set Backup Schedule**

Set automated backup schedule (daily, weekly, monthly).

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/backup-restore/backup/schedule/status
**Get Schedule Status**

Get current backup schedule status.

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/backup-restore/backup/schedule/options
**Get Schedule Options**

Get available backup schedule options.

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/backup-restore/restore/{backup_id}
**Restore From Backup**

Restore system data from a specific backup.
WARNING: This will overwrite existing data.

**Parameters:**
- `backup_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/backup-restore/restore
**Get Restore History**

Get restore operation history.

**Parameters:**
- `skip` (query) — 
- `limit` (query) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/backup-restore/stats
**Get Backup Stats**

Get backup and restore statistics.

**Responses:**
- `200` — Successful Response

---

### `DELETE` /admin/backup-restore/backup/{backup_id}
**Delete Backup**

Delete a specific backup (both record and file).

**Parameters:**
- `backup_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Admin - CMS Management

### `GET` /admin/cms/headers
**Get Headers**

Get all headers

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/cms/headers
**Create Header**

Create a new header banner

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/cms/headers/{header_id}
**Get Header**

Get a specific header by ID

**Parameters:**
- `header_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/cms/headers/{header_id}
**Update Header**

Update a header

**Parameters:**
- `header_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/cms/headers/{header_id}
**Delete Header**

Delete a header

**Parameters:**
- `header_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/cms/carousels
**Get Carousels**

Get all carousel items ordered by 'order' field

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/cms/carousels
**Create Carousel**

Create a new carousel item

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/cms/carousels/{carousel_id}
**Update Carousel**

Update a carousel item

**Parameters:**
- `carousel_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/cms/carousels/{carousel_id}
**Delete Carousel**

Delete a carousel item

**Parameters:**
- `carousel_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/cms/faqs
**Get Faqs**

Get all FAQ items ordered by 'order' field

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/cms/faqs
**Create Faq**

Create a new FAQ item

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/cms/faqs/{faq_id}
**Update Faq**

Update a FAQ item

**Parameters:**
- `faq_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/cms/faqs/{faq_id}
**Delete Faq**

Delete a FAQ item

**Parameters:**
- `faq_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/cms/overview
**Get Cms Overview**

Get complete CMS data overview

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/cms/reorder
**Reorder Items**

Reorder items in carousel or FAQ collections

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Admin - Linked Accounts

### `GET` /admin/linked-accounts/
**Get All Linked Accounts**

Get all linked account relationships in the system.

**Parameters:**
- `primary_customer_id` (query) — Filter by primary customer
- `linked_phone` (query) — Filter by linked phone number

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/linked-accounts/customer/{customer_id}
**Get Customer Linked Relationships**

Get all linked account relationships for a specific customer
(both as primary and as linked customer).

**Parameters:**
- `customer_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/linked-accounts/{linked_account_id}
**Admin Remove Linked Account**

Admin: Remove any linked account relationship.

**Parameters:**
- `linked_account_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Admin - Referral Management

### `GET` /admin/admin/referrals/
**Get All Referral Programs**

Admin: View all referral programs with filtering.

**Parameters:**
- `status` (query) — Filter by status
- `is_active` (query) — Filter by active status
- `skip` (query) — Skip records
- `limit` (query) — Limit records

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/admin/referrals/{referral_id}/usage-logs
**Get Referral Usage Logs**

Admin: View usage logs for a specific referral program.

**Parameters:**
- `referral_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/admin/referrals/stats/overview
**Get Referral Overview Stats**

Admin: Get overview statistics for referral programs.

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/admin/referrals/customer/{customer_id}/referrals
**Get Customer Referral Details**

Admin: Get detailed referral information for a specific customer.

**Parameters:**
- `customer_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Admin Management

### `POST` /admin/admins/
**Create Admin**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/admins/
**Get Admins**

Get all admins or a specific admin by ID.

**Parameters:**
- `admin_id` (query) — Get specific admin by ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/admins/{admin_id}
**Update Admin**

**Parameters:**
- `admin_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/admins/change-password
**Change Password**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Admin Notifications

### `GET` /admin/notifications/
**Get All Notifications**

Admin: Get all notifications with filtering options

**Parameters:**
- `customer_id` (query) — Filter by customer
- `notification_type` (query) — Filter by type
- `channel` (query) — Filter by channel
- `status` (query) — Filter by status

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/notifications/send
**Send Admin Notification**

Admin: Send notification to one or multiple customers

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/notifications/stats
**Get Admin Notification Stats**

Admin: Get system-wide notification statistics - shows sent_today

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/notifications/automated-stats
**Get Automated Notification Stats**

Get statistics about automated notifications

**Responses:**
- `200` — Successful Response

---

## Analytics & Reports

### `GET` /admin/analytics/dashboard
**Get Dashboard Analytics**

Get minimal dashboard analytics - ESSENTIAL DATA ONLY

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/analytics/revenue
**Get Revenue Analytics**

Get revenue analytics - FIXED TO RETURN DATA

**Parameters:**
- `period` (query) — daily, weekly, monthly
- `days` (query) — Number of days to analyze

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/analytics/customers/growth
**Get Customer Growth Analytics**

Get customer growth analytics

**Parameters:**
- `days` (query) — Number of days to analyze

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/analytics/referrals/trend
**Get Referral Trend Analytics**

Get referral trend analytics - FIXED TO RETURN DATA

**Parameters:**
- `days` (query) — Number of days to analyze

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/analytics/plans/performance
**Get Plan Performance**

Get top performing plans by transaction count

**Parameters:**
- `limit` (query) — Number of top plans to return

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Authentication

### `POST` /admin/login
**Admin Login**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /customer/login
**Customer Login**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /refresh
**Refresh Token**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /logout
**Logout**

Simple logout - just blacklists the access token

**Responses:**
- `200` — Successful Response

---

### `POST` /customer/register
**Customer Register**

Register a new customer account with optional referral code.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Category Management

### `GET` /admin/categories/
**Get Categories**

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/categories/
**Create Category**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/categories/{category_id}
**Update Category**

**Parameters:**
- `category_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/categories/{category_id}
**Delete Category**

**Parameters:**
- `category_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Customer - CMS Content

### `GET` /customer/cms/content
**Get Cms Content**

Get all CMS content for customer frontend

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/cms/headers
**Get Headers**

Get headers for customer (public endpoint)

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/cms/carousels
**Get Carousels**

Get carousel items for customer (public endpoint)

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/cms/faqs
**Get Faqs**

Get FAQ items for customer (public endpoint)

**Responses:**
- `200` — Successful Response

---

## Customer Management

### `GET` /admin/customers/
**Get Customers**

Get all customers, a specific customer by ID, or search customers with filtering options.

**Parameters:**
- `customer_id` (query) — Get specific customer by ID
- `phone_number` (query) — Filter by phone number
- `full_name` (query) — Filter by full name
- `account_status` (query) — Filter by account status
- `days_inactive_min` (query) — Minimum days inactive
- `days_inactive_max` (query) — Maximum days inactive
- `search_term` (query) — Search by phone number or name

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/customers/stats
**Get Customer Stats**

Get customer statistics.

**Responses:**
- `200` — Successful Response

---

### `POST` /admin/customers/{customer_id}/deactivate
**Deactivate Customer**

Deactivate a customer account.

**Parameters:**
- `customer_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Customer Notifications

### `GET` /customer/notifications/
**Get My Notifications**

Get current customer's notifications

**Parameters:**
- `unread_only` (query) — Show only unread notifications

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/notifications/stats
**Get Notification Stats**

Get notification statistics for customer

**Responses:**
- `200` — Successful Response

---

### `POST` /customer/notifications/mark-read
**Mark Notifications As Read**

Mark specific notifications as read

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /customer/notifications/mark-all-read
**Mark All Notifications As Read**

Mark all notifications as read for current customer

**Responses:**
- `200` — Successful Response

---

## Customer Profile

### `GET` /customer/profile
**Get Customer Profile**

Get current customer's profile information.

**Responses:**
- `200` — Successful Response

---

### `PUT` /customer/profile
**Update Customer Profile**

Update customer profile information.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /customer/change-password
**Change Customer Password**

Change customer password.

**Parameters:**
- `current_password` (query) (required) — Current password
- `new_password` (query) (required) — New password

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Customer Referral

### `POST` /customer/referral/generate
**Generate Referral Code**

Generate a new referral code for the current customer.

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/referral/my-referrals
**Get Referral Details**

Get referral program details and statistics for the current customer.

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/referral/discounts
**Get My Referral Discounts**

Get all active referral discounts for the current customer.

**Responses:**
- `200` — Successful Response

---

## Linked Accounts

### `POST` /customer/linked-accounts
**Add Linked Account**

Add a linked account (family member/friend) to your account.
The linked phone number will receive OTP for verification (simulated).

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/linked-accounts
**Get Linked Accounts**

Get all linked accounts for the current customer or a specific linked account by ID.

**Parameters:**
- `linked_account_id` (query) — Get specific linked account by ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /customer/linked-accounts/{linked_account_id}
**Remove Linked Account**

Remove a linked account from your account.

**Parameters:**
- `linked_account_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /customer/linked-accounts/{linked_account_id}/recharge
**Recharge Linked Account**

Recharge a plan for a linked account.

**Parameters:**
- `linked_account_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Offer Management

### `POST` /admin/offers/
**Create Offer**

Create a new offer by specifying discounted price directly.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/offers/
**Get Offers**

Get all offers or a specific offer by ID with optional filtering.

**Parameters:**
- `offer_id` (query) — Get specific offer by ID
- `plan_id` (query) — Filter by plan
- `status` (query) — Filter by status (active/inactive/expired)

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/offers/create-with-discount
**Create Offer With Discount**

Create an offer by specifying discount percentage.
The system automatically calculates the discounted price.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/offers/calculate-discount
**Calculate Discount**

Calculate discount details without creating an offer.
Useful for previewing the discount before creating the offer.

**Parameters:**
- `plan_id` (query) (required) — Plan ID
- `discount_percentage` (query) (required) — Discount percentage (0-100)

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/offers/active
**Get Active Offers**

Get all currently active offers (valid_from <= current_time <= valid_until).

**Responses:**
- `200` — Successful Response

---

### `PUT` /admin/offers/{offer_id}
**Update Offer**

Update an existing offer.

**Parameters:**
- `offer_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/offers/{offer_id}
**Delete Offer**

Delete an offer.

**Parameters:**
- `offer_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Plan Management

### `POST` /admin/plans/
**Create Plan**

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/plans/
**Get Plans**

Get all plans or a specific plan by ID with optional filtering.

**Parameters:**
- `plan_id` (query) — Get specific plan by ID
- `plan_type` (query) — Filter by plan type
- `category_id` (query) — Filter by category
- `status` (query) — Filter by status

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `PUT` /admin/plans/{plan_id}
**Update Plan**

**Parameters:**
- `plan_id` (path) (required) — 

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /admin/plans/{plan_id}
**Delete Plan**

**Parameters:**
- `plan_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/plans/{plan_id}/activate
**Activate Plan**

**Parameters:**
- `plan_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/plans/{plan_id}/deactivate
**Deactivate Plan**

**Parameters:**
- `plan_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Postpaid - Secondary Numbers

### `GET` /customer/postpaid/secondary-numbers
**Get Secondary Numbers**

Get all secondary numbers for current postpaid plan.

**Responses:**
- `200` — Successful Response

---

### `POST` /customer/postpaid/secondary-numbers
**Add Secondary Number**

Add a secondary number to postpaid plan.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `DELETE` /customer/postpaid/secondary-numbers/{secondary_id}
**Remove Secondary Number**

Remove a secondary number from postpaid plan.

**Parameters:**
- `secondary_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Postpaid Activations

### `POST` /customer/postpaid/activate
**Activate Postpaid Plan**

Activate a postpaid plan for a primary phone number.
Note: Each phone number can have only one active postpaid plan at a time.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/postpaid/activation
**Get Customer Postpaid Activations**

Get all active postpaid activations for the current customer.
Includes activations where customer is primary owner OR secondary number.

**Responses:**
- `200` — Successful Response

---

## Postpaid Activations Management

### `GET` /admin/postpaid/activations
**Get Postpaid Activations**

Get all postpaid activations or a specific activation by ID with filtering options.
Shows only active activations by default.

**Parameters:**
- `activation_id` (query) — Get specific activation by ID
- `plan_id` (query) — Filter by plan
- `status` (query) — Filter by status
- `customer_phone` (query) — Filter by customer phone
- `date_from` (query) — Filter from date
- `date_to` (query) — Filter to date

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/postpaid/activations/{activation_id}/secondary-validation
**Validate Secondary Number Addition**

Check if a secondary number can be added to this activation

**Parameters:**
- `activation_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Postpaid Billing

### `GET` /customer/postpaid/bill
**Get Postpaid Bill**

Get current postpaid bill details.

**Responses:**
- `200` — Successful Response

---

### `POST` /customer/postpaid/pay-bill
**Pay Postpaid Bill**

Pay postpaid bill for a specific activation.
Only allowed after billing cycle ends.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Postpaid Billing Management

### `GET` /admin/postpaid/due-payments
**Get Due Payments**

Get all activations with due payments (only unpaid bills).

**Responses:**
- `200` — Successful Response

---

### `GET` /admin/postpaid/customer-history/{customer_id}
**Get Customer Postpaid History**

Get detailed postpaid history for a specific customer.

**Parameters:**
- `customer_id` (path) (required) — 

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Recharge

### `POST` /customer/recharge
**Create Recharge**

Create a new recharge transaction and handle subscription logic.
Applies referral discounts and completes referral process for first recharge.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Subscription Management

### `GET` /admin/subscriptions/active
**Get Active Subscriptions**

Get all active subscriptions (only currently active ones).

**Parameters:**
- `customer_id` (query) — Filter by customer ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /admin/subscriptions/queue
**Get Activation Queue**

Get the subscription activation queue.

**Parameters:**
- `customer_id` (query) — Filter by customer ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## Transaction Monitoring

### `GET` /admin/transactions/
**Get Transactions**

Get all transactions or a specific transaction by ID with filtering options.

**Parameters:**
- `transaction_id` (query) — Get specific transaction by ID
- `customer_id` (query) — Filter by customer ID
- `customer_phone` (query) — Filter by customer phone
- `plan_id` (query) — Filter by plan
- `transaction_type` (query) — Filter by transaction type
- `payment_status` (query) — Filter by payment status
- `payment_method` (query) — Filter by payment method
- `date_from` (query) — Filter from date
- `date_to` (query) — Filter to date

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `POST` /admin/transactions/export
**Export Transactions**

Export all transactions as CSV file.

**Responses:**
- `200` — Successful Response

---

## View Plans & Offers

### `GET` /customer/categories
**Get Categories**

Get all plan categories.

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/plans
**Get Plans For Customer**

Get all available plans for customers or a specific plan by ID.

**Parameters:**
- `plan_id` (query) — Get specific plan by ID
- `plan_type` (query) — Filter by plan type
- `category_id` (query) — Filter by category

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/offers
**Get Offers For Customer**

Get all active offers for customers.

**Parameters:**
- `plan_id` (query) — Filter by plan

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

## View Postpaid Plans & Addons

### `GET` /customer/postpaid/plans
**Get Postpaid Plans**

Get all available postpaid plans or a specific postpaid plan by ID.

**Parameters:**
- `plan_id` (query) — Get specific postpaid plan by ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/postpaid/usage
**Get Data Usage**

Get current data usage statistics.

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/postpaid/addon-plans
**Get Data Addon Plans**

Get all available data addon plans (postpaid plans with is_topup=True).

**Responses:**
- `200` — Successful Response

---

### `POST` /customer/postpaid/purchase-addon
**Purchase Data Addon**

Purchase a data addon for postpaid plan.

**Request Body Example:**
```json
// See schema in full documentation
```

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---

### `GET` /customer/postpaid/addons
**Get Active Data Addons**

Get all active data addons for current postpaid plan.

**Responses:**
- `200` — Successful Response

---

## View Subscriptions

### `GET` /customer/subscriptions/active
**Get Customer Active Subscriptions**

Get customer's active subscription.

**Responses:**
- `200` — Successful Response

---

### `GET` /customer/subscriptions/queue
**Get Customer Queued Subscriptions**

Get customer's queued subscriptions waiting for activation.

**Responses:**
- `200` — Successful Response

---

## View Transactions

### `GET` /customer/transactions
**Get Customer Transactions**

Get customer's transaction history or a specific transaction by ID.

**Parameters:**
- `transaction_id` (query) — Get specific transaction by ID

**Responses:**
- `200` — Successful Response
- `422` — Validation Error

---
