# Authentication & Role Documentation

**Project:** NEXA Mobile Recharge System  
**Version:** v1.0  
**Last Updated:** November 24, 2025

---

## Overview

This document outlines the authentication system and role-based access control (RBAC) for the NEXA Mobile Recharge System. The system handles user login, token management, and permissions with two primary user roles: **Admin** and **Customer**.

---

## Authentication Flow

| Step                    | Description                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| **1. Registration**     | Customers register with phone number, password, and full name. Optionally provide referral code. |
| **2. Login**            | Users authenticate with credentials and receive a JWT access token.                              |
| **3. Access Token**     | Short-lived JWT (default: 30 minutes) used for authenticating API requests.                      |
| **4. Token Validation** | Middleware verifies token and user type (admin/customer) before route access.                    |
| **5. Logout**           | User logs out (client-side token removal).                                                       |
| **6. Protected Routes** | Middleware checks JWT validity and user role permissions.                                        |

---

## JWT Token Payload Example

```json
{
  "sub": "123",
  "user_type": "customer",
  "iat": 1730000000,
  "exp": 1730001800
}
```

**Fields:**

- `sub`: User ID (admin_id or customer_id)
- `user_type`: Either "admin" or "customer"
- `iat`: Token issued at timestamp
- `exp`: Token expiration timestamp

---

## Authentication Endpoints

| Method | Endpoint                    | Description                            | Auth Required |
| ------ | --------------------------- | -------------------------------------- | ------------- |
| `POST` | `/admin/login`              | Admin login with email and password    | ❌ No         |
| `POST` | `/customer/login`           | Customer login with phone and password | ❌ No         |
| `POST` | `/customer/register`        | Register new customer account          | ❌ No         |
| `POST` | `/customer/change-password` | Change customer password               | ✅ Yes        |

---

## Role-Based Access Control (RBAC)

### Roles

| Role         | Description                           | Key Permissions                                                      |
| ------------ | ------------------------------------- | -------------------------------------------------------------------- |
| **Admin**    | Full system control and management    | Manage all users, plans, offers, transactions, analytics, backups    |
| **Customer** | Access personal services and recharge | View plans, make recharges, manage profile, subscriptions, referrals |

---

## Permissions Matrix

**Legend:** C = Create, R = Read, U = Update, D = Delete

| Resource                  | Admin          | Customer       |
| ------------------------- | -------------- | -------------- |
| **User Management**       |
| Admins                    | CRUD           | ❌             |
| Customers                 | CRUD           | RU (self only) |
| Customer Search           | ✅             | ❌             |
| **Plans & Offers**        |
| Categories                | CRUD           | R              |
| Plans                     | CRUD           | R              |
| Offers                    | CRUD           | R              |
| **Transactions**          |
| View All Transactions     | ✅             | R (own only)   |
| Transaction Filtering     | ✅             | ❌             |
| Export Transactions       | ✅             | ❌             |
| Create Recharge           | ❌             | ✅             |
| **Subscriptions**         |
| View All Subscriptions    | ✅             | R (own only)   |
| View Queue                | ✅             | R (own only)   |
| Activation Processing     | ✅ (automated) | ❌             |
| **Prepaid Services**      |
| Browse Plans              | ✅             | ✅             |
| View Offers               | ✅             | ✅             |
| Make Recharge             | ❌             | ✅             |
| View Transaction History  | ✅ (all)       | ✅ (own)       |
| **Postpaid Services**     |
| View All Activations      | ✅             | R (own only)   |
| Activate Postpaid Plan    | ❌             | ✅             |
| Add Secondary Numbers     | ❌             | ✅ (own plans) |
| Purchase Data Addons      | ❌             | ✅ (own plans) |
| View Bills                | ✅ (all)       | ✅ (own)       |
| Pay Bills                 | ❌             | ✅             |
| Billing Management        | ✅             | ❌             |
| **Linked Accounts**       |
| View All Links            | ✅             | R (own only)   |
| Add Linked Account        | ❌             | ✅             |
| Remove Linked Account     | ✅             | ✅ (own only)  |
| Recharge Linked Account   | ❌             | ✅             |
| **Referral Program**      |
| View All Referrals        | ✅             | ❌             |
| System Referral Stats     | ✅             | ❌             |
| Generate Referral Code    | ❌             | ✅             |
| View Own Referrals        | ❌             | ✅             |
| View Referral Discounts   | ❌             | ✅             |
| **Notifications**         |
| View All Notifications    | ✅             | R (own only)   |
| Send Notifications        | ✅             | ❌             |
| Broadcast Notifications   | ✅             | ❌             |
| System Notification Stats | ✅             | ❌             |
| Mark as Read              | ❌             | ✅             |
| **Analytics & Reports**   |
| Dashboard Analytics       | ✅             | ❌             |
| Revenue Analytics         | ✅             | ❌             |
| Customer Growth           | ✅             | ❌             |
| Referral Trends           | ✅             | ❌             |
| Plan Performance          | ✅             | ❌             |
| **Backup & Restore**      |
| Create Backup             | ✅             | ❌             |
| Restore Data              | ✅             | ❌             |
| Schedule Backups          | ✅             | ❌             |
| View Backup History       | ✅             | ❌             |
| **CMS Management**        |
| Manage Headers            | ✅             | ❌             |
| Manage Carousels          | ✅             | ❌             |
| Manage FAQs               | ✅             | ❌             |
| View CMS Content          | ✅             | ✅             |

---

## Token Validation Middleware

### Admin Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.core.security import verify_token

security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("user_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin access required"
        )

    admin_id = int(payload.get("sub"))
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found"
        )

    return admin
```

### Customer Authentication

```python
def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("user_type") != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer access required"
        )

    customer_id = int(payload.get("sub"))
    customer = db.query(Customer).filter(
        Customer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found"
        )

    return customer
```

### Usage in Routes

```python
from app.core.auth import get_current_admin, get_current_customer

# Admin-only endpoint
@router.get("/admin/dashboard")
async def get_dashboard(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return {"message": "Admin dashboard"}

# Customer-only endpoint
@router.get("/customer/profile")
async def get_profile(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return current_customer
```

---

## Frontend Integration Guidelines

### Storing Tokens

Store JWT tokens securely:

```javascript
// After successful login
const response = await fetch("/customer/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ phone_number, password }),
});

const data = await response.json();

// Store token securely (localStorage or sessionStorage)
localStorage.setItem("access_token", data.access_token);
```

### Using Tokens in Requests

```javascript
// Include token in Authorization header
const token = localStorage.getItem("access_token");

const response = await fetch("/customer/profile", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});
```

### Handling Token Expiry

```javascript
// Check for 401 Unauthorized
if (response.status === 401) {
  // Token expired, redirect to login
  localStorage.removeItem("access_token");
  window.location.href = "/login";
}
```

---

## Token Expiry Policy

| Token Type      | Lifetime             | Storage                    | Usage              |
| --------------- | -------------------- | -------------------------- | ------------------ |
| Access Token    | 30 minutes (default) | Client-side (localStorage) | API authentication |
| User Type Claim | Same as token        | In JWT payload             | Role verification  |

**Configuration**: Token lifetime can be adjusted in `.env`:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Security Best Practices

### Password Security

- Passwords hashed using **bcrypt** with salt
- Minimum 6 characters required for customer passwords
- Admin passwords should follow strong password policies

### Token Security

- Tokens include `user_type` claim for role verification
- Tokens validated on every protected route
- Invalid tokens return 401 Unauthorized
- Token tampering detected via signature verification

### API Security

- All sensitive endpoints require authentication
- Role-based authorization enforced
- Input validation using Pydantic models
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration with allowed origins

### Rate Limiting

- Consider implementing rate limiting for:
  - Login endpoints (prevent brute force)
  - Registration endpoints (prevent spam)
  - SMS notification triggers

---

## Example Token Flow Sequence

1. **Customer Registration**

   ```
   POST /customer/register
   → New customer account created
   → Optionally apply referral code
   ```

2. **Customer Login**

   ```
   POST /customer/login
   → Credentials verified
   → JWT token generated with user_type="customer"
   → Token returned to client
   ```

3. **Access Protected Resource**

   ```
   GET /customer/profile
   → Authorization: Bearer <token>
   → Middleware verifies token
   → Checks user_type = "customer"
   → Fetches customer data
   → Returns profile
   ```

4. **Admin Login & Access**

   ```
   POST /admin/login
   → Credentials verified
   → JWT token with user_type="admin"
   → Admin can access all admin routes
   ```

5. **Logout**
   ```
   → Client removes token from storage
   → Token becomes invalid on next request
   ```

---

## Password Change Flow

1. Customer provides current password
2. System verifies current password
3. New password is validated (min 6 chars)
4. Password hashed with bcrypt
5. Database updated
6. Success response returned
7. Customer should login again with new password

---

## Automated Notifications

The system automatically triggers notifications for:

- **Plan Expiry**: 24 hours before expiration
- **Low Balance**: When data < 200MB
- **Payment Success**: After successful recharge
- **Referral Bonus**: When earning referral discount
- **Plan Activated**: When plan starts
- **Plan Queued**: When plan added to queue
- **Postpaid Due**: 3 days before bill due date

All notifications respect user preferences for SMS/Push channels.

---

## Contact

For authentication and security queries, contact:

**Developer**: Vruthika L S
**Email**: vruthikasan@gmail.com
**GitHub**: [https://github.com/Vruthika](https://github.com/Vruthika)

---

**Last Updated**: November 24, 2025  
**Version**: 1.0
