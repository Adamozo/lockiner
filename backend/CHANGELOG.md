# Changelog

All notable changes to the LockIner backend will be documented in this file.

## [Unreleased]

### Phase 8: Authorization & Permissions - 2026-01-20

#### Added
- **Permission Dependencies** in `dependencies.py`:
  - `require_household_member` - Checks user is an active (non-blocked) household member
  - `require_household_manager` - Checks user is a manager of the household
  - `HouseholdContext` - Dataclass returned by permission checks containing household_id, member info, and user

- **Permission Errors** in `dependencies.py`:
  - `NotHouseholdMemberError` - User is not a member
  - `HouseholdAccessBlockedError` - User's access is blocked
  - `NotHouseholdManagerError` - User is not a manager
  - `HouseholdNotFoundError` - Household does not exist

#### Changed
- Household analytics endpoints now use `require_household_member` dependency
- Simplified endpoint code by moving permission checks to reusable dependencies

#### Frontend Impact
- **No API changes** - Permission errors remain HTTP 403/404 as before
- Role-based access is now enforced:
  - **Manager**: Full access to all household operations
  - **Member**: Can view/add transactions/receipts, view analytics
  - **Blocked**: Cannot access household resources (HTTP 403)

---

### Phase 7: Household Analytics - 2026-01-20

#### Added
- **Household Analytics Endpoints** in `/api/v1/households/{uid}/analytics`:
  - `GET /{uid}/analytics/summary?month=YYYY-MM` - Monthly summary with category and member breakdown
  - `GET /{uid}/analytics/by-member?month=YYYY-MM` - Spending breakdown by household member
  - `GET /{uid}/analytics/by-category?month=YYYY-MM` - Spending by category with member contributions

- **New Schemas** in `schemas.py`:
  - `MemberSpending` - Individual member spending summary (user_id, user_name, total, count, average, percentage)
  - `HouseholdMonthlySummary` - Monthly summary with income, expenses, by_category, and by_member lists
  - `HouseholdCategorySummary` - Category spending with nested member contributions

- **Repository Methods** in `AnalyticsRepository`:
  - `get_household_transactions()` - Fetch household transactions with user who added them
  - `get_household_expenses()` - Fetch household expenses with user attribution

- **Service Methods** in `AnalyticsService`:
  - `get_household_monthly_summary()` - Calculate monthly summary for household
  - `get_household_spending_by_member()` - Aggregate spending by member
  - `get_household_spending_by_category()` - Category spending with member breakdown

#### Frontend Impact
- **New household analytics endpoints available**
- All endpoints require authentication and household membership
- Blocked members cannot access analytics (HTTP 403)
- `month` parameter is optional for by-member and by-category (omit for all-time data)
- Response includes who spent how much, enabling household expense sharing features

---

### Phase 6: Update Existing Services - 2026-01-19

#### Changed
- **Transaction endpoints now require authentication**
  - All `/api/v1/transactions` endpoints require `Authorization: Bearer <token>`
  - New optional `household_id` query parameter for household context
  - Transactions are filtered by ownership (personal + optional household)
  - Creating a transaction automatically creates ownership record
  - `TransactionAccessDeniedError` returned for unauthorized access (HTTP 403)

- **Receipt endpoints now require authentication**
  - All `/api/v1/receipts` endpoints require `Authorization: Bearer <token>`
  - New optional `household_id` parameter for household context
  - Receipts are filtered by ownership (personal + optional household)
  - Auto-created transactions from verified receipts inherit receipt ownership
  - `ReceiptAccessDeniedError` returned for unauthorized access (HTTP 403)

- **Category endpoints now require authentication**
  - All `/api/v1/categories` endpoints require `Authorization: Bearer <token>`
  - New optional `household_id` query parameter for household context
  - Default categories (without ownership) are visible to all users
  - User-created categories are private unless assigned to household
  - `CategoryAccessDeniedError` returned for unauthorized access (HTTP 403)

- **Budget settings endpoints now require authentication**
  - `GET/PUT /api/v1/analytics/budget-settings` require authentication
  - `GET /api/v1/analytics/budget-status-complete` requires authentication
  - `GET /api/v1/analytics/budget-alerts` requires authentication
  - New optional `household_id` parameter for household budget settings
  - User/household-specific budget settings via ownership system

#### Frontend Impact
- **All data endpoints now require authentication** - Frontend must include `Authorization: Bearer <token>` header
- Use `household_id` query parameter to work with household data:
  - `GET /api/v1/transactions?household_id=1` - Include household transactions
  - `POST /api/v1/transactions?household_id=1` - Create transaction for household
  - Same pattern for receipts, categories, and budget settings
- HTTP 403 (Forbidden) is returned when accessing entities without ownership
- HTTP 401 (Unauthorized) is returned when no/invalid token is provided

---

### Phase 5: Ownership Junction Tables - 2026-01-19

#### Added
- Ownership junction models in `models.py`:
  - `UserTransaction` - links users to their transactions
  - `HouseholdTransaction` - links households to transactions (with `added_by_user_id`)
  - `UserReceipt` - links users to their receipts
  - `HouseholdReceipt` - links households to receipts (with `added_by_user_id`)
  - `UserCategory` - links users to custom categories
  - `HouseholdCategory` - links households to shared categories
  - `UserBudgetSettings` - links users to their budget settings
  - `HouseholdBudgetSettings` - links households to shared budget settings
- `UserOwnershipRepository` for managing user ownership records
- `HouseholdOwnershipRepository` for managing household ownership records
- `OwnershipService` with unified API:
  - `assign_to_user(entity_type, entity_id, user_id)`
  - `assign_to_household(entity_type, entity_id, household_id, added_by)`
  - `get_user_entities(entity_type, user_id)`
  - `get_household_entities(entity_type, household_id)`
  - `remove_from_user/household()`
  - `user_owns_entity()` / `household_owns_entity()`
- Database indexes for all ownership junction tables

#### Frontend Impact
- **No new endpoints yet** - ownership is infrastructure for Phase 6
- Entity types supported: `transaction`, `receipt`, `category`, `budget_settings`
- Household ownership tracks `added_by_user_id` for audit trail
- Existing endpoints continue to work (not yet filtered by ownership)

---

### Phase 4: Invitation System - 2026-01-19

#### Added
- `HouseholdInvitation` model in `models.py`:
  - `id`, `household_id` (FK), `token` (UUID), `created_by` (FK), `expires_at`, `max_uses`, `uses_count`, `is_active`, `created_at`
- `InvitationRepository` for invitation database operations
- `InvitationService` with business logic:
  - Generate invitation tokens
  - Validate expiration and usage limits
  - Redeem invitations (join household)
- Invitation endpoints in `/api/v1/households`:
  - `POST /{uid}/invitations` - Create invitation (manager only, returns token)
  - `GET /{uid}/invitations` - List active invitations (manager only)
  - `DELETE /{uid}/invitations/{id}` - Revoke invitation (manager only)
- `/api/v1/invitations` router:
  - `GET /{token}` - Get invitation info (preview, no auth required)
  - `POST /{token}/join` - Join household using invitation token
- Schemas: `InvitationCreate`, `InvitationResponse`, `InvitationJoinResponse`

#### Frontend Impact
- **New invitation endpoints available** - Frontend can implement invitation flow
- Invitation creation returns a `token` that can be used to generate QR codes or shareable links
- Preview endpoint (`GET /invitations/{token}`) does not require authentication - allows showing household name before login
- Join endpoint (`POST /invitations/{token}/join`) requires authentication
- Invitations can have optional expiration (`expires_in_days`) and usage limits (`max_uses`)
- HTTP 410 (Gone) is returned for expired/exhausted/revoked invitations
- HTTP 409 (Conflict) is returned if user is already a member

---

### Phase 3: Household Core - 2026-01-19

#### Added
- `Household` model in `models.py`:
  - `id`, `uid` (UUID), `name`, `description`, `icon`, `created_at`, `updated_at`
- `HouseholdMember` model for many-to-many relationship:
  - `id`, `household_id` (FK), `user_id` (FK), `role` (manager/member), `status` (active/blocked), `joined_at`
- `HouseholdRepository` for household database operations
- `HouseholdService` with business logic for households and members
- `/api/v1/households` router with endpoints:
  - `POST /` - Create household (creator becomes manager)
  - `GET /` - List user's households
  - `GET /{uid}` - Get household details with members
  - `PUT /{uid}` - Update household (manager only)
  - `DELETE /{uid}` - Delete household (manager only)
  - `GET /{uid}/members` - List all members
  - `PUT /{uid}/members/{user_id}` - Update member role/status (manager only)
  - `DELETE /{uid}/members/{user_id}` - Remove member (manager only, or self-removal)
- Schemas: `HouseholdCreate`, `HouseholdUpdate`, `HouseholdResponse`, `HouseholdDetailResponse`, `HouseholdMemberResponse`, `HouseholdMemberUpdate`

#### Frontend Impact
- **New household endpoints available** - Frontend can implement household management
- All household endpoints require authentication (`Authorization: Bearer <token>`)
- Households are identified by UUID (`uid`) in URLs, not integer IDs
- Creator of household is automatically added as manager
- Self-removal from household is always allowed (except last manager)

---

### Phase 2: User Model & Authentication - 2026-01-19

#### Added
- `User` model in `models.py`:
  - `id`, `email_hash` (SHA-256 hashed email), `password_hash` (bcrypt), `name`, `is_active`, `created_at`, `updated_at`
- `UserRepository` for database operations on users
- `AuthService` for authentication logic:
  - JWT access/refresh token generation and validation
  - Password hashing with bcrypt
  - Email hashing with SHA-256
- `dependencies.py` with authentication middleware:
  - `get_current_user` - extracts and validates JWT from Authorization header
  - `get_current_active_user` - ensures user is active
- `/api/v1/auth` router with endpoints:
  - `POST /register` - Register new user
  - `POST /login` - Authenticate and get tokens
  - `POST /logout` - Logout (stateless, client discards tokens)
  - `POST /refresh-token` - Refresh access token
  - `GET /me` - Get current user info
  - `PUT /me` - Update user profile
  - `POST /change-password` - Change password
- New authentication dependencies: `python-jose`, `passlib`, `bcrypt`
- `JWT_SECRET_KEY` environment variable for token signing

#### Frontend Impact
- **New auth endpoints available** - Frontend can now implement user registration/login
- All endpoints still work without authentication (for now)
- New schemas: `UserCreate`, `UserResponse`, `LoginRequest`, `TokenResponse`, `RefreshTokenRequest`, `PasswordChangeRequest`
- Store tokens in localStorage/cookies and include `Authorization: Bearer <token>` header for protected routes

---

### Phase 1.2: Switch to Async SQLAlchemy - 2026-01-19

#### Changed
- `database.py`: Complete rewrite to use async SQLAlchemy
  - Uses `create_async_engine` and `async_sessionmaker`
  - `AsyncSession` for all database operations
  - Added `init_db()` async function for table creation on startup
- All repositories converted to async methods:
  - `CategoryRepository`: All methods now async
  - `TransactionRepository`: All methods now async
  - `ReceiptRepository`: All methods now async
  - `AnalyticsRepository`: All methods now async
  - `ImportRepository`: All methods now async
- All services converted to async:
  - `CategoryService`: All methods now async
  - `TransactionService`: All methods now async
  - `ReceiptService`: All methods now async
  - `AnalyticsService`: All methods now async
  - `ImportService`: All methods now async
- All routers updated to await async service calls
- `main.py`: Added lifespan context manager for database initialization

#### Frontend Impact
- No API changes - all endpoints remain the same
- No frontend changes required
- Database operations are now non-blocking

---

### Phase 1.1: PostgreSQL Container Setup - 2026-01-19

#### Added
- PostgreSQL 16 Alpine container in `docker-compose.yml`
- PostgreSQL data persistence volume (`postgres_data`)
- Health checks for PostgreSQL container
- Backend service now depends on healthy PostgreSQL

#### Changed
- `docker-compose.yml`: Added PostgreSQL service configuration
- `docker-compose.yml`: Backend DATABASE_URL now uses `postgresql+asyncpg://` connection string
- `.env.example`: Added PostgreSQL environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)
- `requirements.txt`: Added `asyncpg==0.29.0` and `greenlet==3.1.1` for async PostgreSQL support
- `Dockerfile`: Removed SQLite dependency (no longer needed)

#### Frontend Impact
- No frontend changes required for this phase
- Backend API remains unchanged
- Database connection string format changed (handled by backend configuration)
