# Multi-User & Household Feature Implementation

## Phase 1: Infrastructure Setup

### 1. PostgreSQL Container Setup
- [x] Create/update `docker-compose.yml` with PostgreSQL service
- [x] Configure environment variables for DB connection
- [x] Add volume for data persistence
- [x] Update `.env.example` with required variables

### 2. Switch to Async SQLAlchemy
- [x] Install `asyncpg` and update `sqlalchemy` for async support
- [x] Refactor `database.py` to use `AsyncSession` and `create_async_engine`
- [x] Update all repositories to use async methods
- [x] Update all services to be async-compatible

---

## Phase 2: User Management

### 3. User Model & Authentication
- [x] Create `User` model:
  - `id`, `name`, `email` (hashed), `password_hash`, `created_at`, `updated_at`
- [x] Create `UserRepository`
- [x] Create `UserService`
- [x] Create `AuthService` for JWT handling
- [x] Create `/api/v1/auth` router:
  - `POST /register`
  - `POST /login`
  - `POST /logout`
  - `POST /refresh-token`
  - `GET /me`
- [x] Add authentication middleware/dependency

---

## Phase 3: Household Core

### 4. Household Model
- [x] Create `Household` model:
  - `uid` (UUID), `name`, `description`, `icon`, `created_at`, `updated_at`
- [x] Create `HouseholdRepository`
- [x] Create `HouseholdService`
- [x] Create `/api/v1/households` router:
  - `POST /` - create household
  - `GET /` - list user's households
  - `GET /{uid}` - get household details
  - `PUT /{uid}` - update household
  - `DELETE /{uid}` - delete household (manager only)

### 5. Household Members (Many-to-Many)
- [x] Create `HouseholdMember` model:
  - `id`, `household_id` (FK), `user_id` (FK), `role`, `status`, `joined_at`
- [x] Create `HouseholdMemberRepository`
- [x] Create `HouseholdMemberService`
- [x] Add member management endpoints:
  - `GET /households/{uid}/members`
  - `PUT /households/{uid}/members/{user_id}` - update role/status
  - `DELETE /households/{uid}/members/{user_id}` - remove member

---

## Phase 4: Invitation System

### 6. Invitation Link System
- [x] Create `HouseholdInvitation` model:
  - `id`, `household_id` (FK), `token` (UUID), `created_by` (FK), `expires_at`, `max_uses`, `uses_count`
- [x] Create `HouseholdInvitationRepository`
- [x] Create `HouseholdInvitationService`:
  - Generate invitation token/link
  - Validate and redeem invitation
- [x] Add endpoints:
  - `POST /households/{uid}/invitations` - create invitation (returns token/link)
  - `GET /households/{uid}/invitations` - list active invitations
  - `DELETE /households/{uid}/invitations/{id}` - revoke invitation
  - `POST /invitations/{token}/join` - join household
  - `GET /invitations/{token}` - get invitation info (preview)

> **Note:** Frontend will generate QR code from the returned invitation link

---

## Phase 5: Ownership Junction Tables

### 7. Create Ownership Link Tables

```
UserTransaction
  - id
  - user_id (FK to User)
  - transaction_id (FK to Transaction)
  - created_at

HouseholdTransaction
  - id
  - household_id (FK to Household)
  - transaction_id (FK to Transaction)
  - added_by_user_id (FK to User)
  - created_at

UserReceipt
  - id
  - user_id (FK to User)
  - receipt_id (FK to Receipt)
  - created_at

HouseholdReceipt
  - id
  - household_id (FK to Household)
  - receipt_id (FK to Receipt)
  - added_by_user_id (FK to User)
  - created_at

UserCategory
  - id
  - user_id (FK to User)
  - category_id (FK to Category)
  - created_at

HouseholdCategory
  - id
  - household_id (FK to Household)
  - category_id (FK to Category)
  - created_at

UserBudgetSettings
  - id
  - user_id (FK to User)
  - budget_settings_id (FK to BudgetSettings)
  - created_at

HouseholdBudgetSettings
  - id
  - household_id (FK to Household)
  - budget_settings_id (FK to BudgetSettings)
  - created_at
```

- [x] Create all ownership models
- [x] Run migrations (auto-created on startup via init_db)

### 8. Create Ownership Repositories
- [x] `UserOwnershipRepository` - handles all user junction tables
- [x] `HouseholdOwnershipRepository` - handles all household junction tables

### 9. Create Ownership Service
- [x] `OwnershipService` with methods:
  - `assign_to_user(entity_type, entity_id, user_id)`
  - `assign_to_household(entity_type, entity_id, household_id, added_by)`
  - `get_user_entities(entity_type, user_id)`
  - `get_household_entities(entity_type, household_id)`
  - `remove_from_user(entity_type, entity_id, user_id)`
  - `remove_from_household(entity_type, entity_id, household_id)`
  - `user_owns_entity(entity_type, entity_id, user_id)`
  - `household_owns_entity(entity_type, entity_id, household_id)`

---

## Phase 6: Update Existing Services

### 10. Update Transaction Flow
- [x] Modify `TransactionService.create()` to also create ownership record
- [x] Add filtering by user/household context
- [x] Update endpoints to require authentication and scope

### 11. Update Receipt Flow
- [x] Modify `ReceiptService` for ownership
- [x] Add filtering by user/household context
- [x] Update endpoints

### 12. Update Category Flow
- [x] Support user-specific and household-specific categories
- [x] Default categories can be shared (no ownership record)
- [x] Update endpoints

### 13. Update Budget/Limits Flow
- [x] Support user and household budget settings
- [x] Update endpoints

---

## Phase 7: Household Analytics

### 14. Extended Analytics
- [x] Update `AnalyticsRepository` to join with ownership tables
- [x] Add spending breakdown by household member
- [x] New endpoints:
  - `GET /households/{uid}/analytics/summary`
  - `GET /households/{uid}/analytics/by-member`
  - `GET /households/{uid}/analytics/by-category`

---

## Phase 8: Authorization & Permissions

### 15. Permission System
- [x] Create permission decorator/dependency
- [x] Implement role-based access:
  - **Manager**: full access, can block/unblock, manage invitations
  - **Member**: CRUD on transactions/receipts, view analytics
  - **Blocked**: no access

---

## Summary

| Phase | Description | Tasks |
|-------|-------------|-------|
| 1 | Infrastructure Setup | 2 |
| 2 | User Management | 1 |
| 3 | Household Core | 2 |
| 4 | Invitation System | 1 |
| 5 | Ownership Junction Tables | 3 |
| 6 | Update Existing Services | 4 |
| 7 | Household Analytics | 1 |
| 8 | Authorization & Permissions | 1 |
| **Total** | | **15** |
