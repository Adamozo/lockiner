# Frontend Changelog

All notable frontend changes for LockIner will be documented in this file.

## [Unreleased]

### Summary

This release integrates the frontend with the new backend authentication and household management system. Key features:

- **Authentication**: JWT-based login/register with automatic token refresh
- **Households**: Create and manage shared expense groups
- **Member Management**: Invite users, manage roles (manager/member), block/remove members
- **Invitations**: Generate shareable links with expiry and usage limits
- **Analytics**: View spending breakdowns by member and category
- **Role-Based UI**: Conditional rendering based on user roles (manager/member)
- **Permission Handling**: Centralized permission checks and blocked user handling
- **Context Switching**: Quick switch between personal and household views via sidebar
- **Landing Page**: Public landing page with CTAs for login/register
- **Global Route Protection**: Automatic protection of all routes except public pages

### New Files Created

**Stores:**
- `stores/auth.ts` - Authentication state management
- `stores/households.ts` - Households and members state

**Composables:**
- `composables/useAuth.ts` - Auth wrapper with router integration
- `composables/useHouseholds.ts` - Households API wrapper
- `composables/useInvitations.ts` - Invitations API wrapper
- `composables/useHouseholdContext.ts` - Household context switching
- `composables/usePermissions.ts` - Role-based permission checking

**Middleware:**
- `middleware/auth.global.ts` - Global route protection for all non-public routes
- `middleware/guest.ts` - Redirect authenticated users from login/register

**Pages:**
- `pages/index.vue` - Public landing page with login/register CTAs
- `pages/home.vue` - Authenticated dashboard (requires login)
- `pages/login.vue` - Login form
- `pages/register.vue` - Registration form
- `pages/profile.vue` - User profile management
- `pages/households/index.vue` - Households list
- `pages/households/create.vue` - Create household
- `pages/households/[uid].vue` - Household detail
- `pages/households/[uid]/invitations.vue` - Manage invitations
- `pages/households/[uid]/analytics.vue` - Household analytics
- `pages/join/[token].vue` - Accept invitation

**Layouts:**
- `layouts/auth.vue` - Centered auth layout

**Components:**
- `components/common/AccessDenied.vue` - Access denied page
- `components/common/BlockedAccess.vue` - Blocked user page
- `components/common/SkeletonCard.vue` - Loading skeleton card
- `components/common/SkeletonList.vue` - Loading skeleton list
- `components/household/HouseholdSelector.vue` - Context switcher dropdown

---

### Phase 1: Authentication System Integration - 2026-01-20

#### Added
- **TypeScript Types** in `types/api.ts`:
  - Auth types: User, UserCreate, UserUpdate, LoginRequest, TokenResponse, RefreshTokenRequest, PasswordChangeRequest
  - Household types: Household, HouseholdCreate, HouseholdUpdate, HouseholdMember, MemberRole, MemberStatus
  - Invitation types: InvitationCreate, InvitationResponse, InvitationPreview, InvitationJoinResponse
  - Household analytics types: MemberSpending, HouseholdMonthlySummary, HouseholdCategoryMemberBreakdown

- **Auth Store** (`stores/auth.ts`):
  - JWT token management with localStorage persistence
  - User state: user, accessToken, refreshToken, isAuthenticated
  - Actions: login, register, logout, refreshAccessToken, fetchCurrentUser, updateProfile, changePassword
  - Automatic token initialization on app start

- **Auth Composable** (`composables/useAuth.ts`):
  - Wrapper around auth store with router integration
  - Helper methods: requireAuth, requireGuest for route protection
  - Login/logout with automatic redirects

- **API Layer Update** (`composables/useApi.ts`):
  - Automatic Authorization header injection
  - 401 handling with automatic token refresh
  - 403 (forbidden) and 410 (expired/gone) error handling
  - `buildQueryParams` helper for household_id support

- **Route Middleware**:
  - `middleware/auth.global.ts` - Global middleware protecting all non-public routes (replaced auth.ts in Phase 9)
  - `middleware/guest.ts` - Redirects logged-in users from /login, /register

- **Auth Layout** (`layouts/auth.vue`):
  - Centered layout for authentication pages
  - Logo and branding display

- **Auth Pages**:
  - `pages/login.vue` - Login form with validation and error handling
  - `pages/register.vue` - Registration form with password strength indicator
  - `pages/profile.vue` - User profile management and password change

- **Sidebar Auth UI**:
  - GlobalSidebar: User avatar, name display, profile link, logout button
  - MobileSidebar: Profile/login button in bottom navigation

#### Changed
- `components/global/GlobalSidebar.vue` - Added auth state display and actions
- `components/global/MobileSidebar.vue` - Added profile/login navigation

---

### Phase 2: Existing Endpoints Update - 2026-01-20

#### Changed
- **`composables/useTransactions.ts`** - Added optional `householdId` parameter to all methods
- **`composables/useReceipts.ts`** - Added optional `householdId` parameter to all methods
- **`composables/useCategories.ts`** - Added optional `householdId` parameter to all methods
- **`composables/useAnalytics.ts`** - Added optional `householdId` and household analytics endpoints

#### Added
- **`composables/useHouseholdContext.ts`** - Manages current household context (personal vs household)
  - `currentHouseholdId` reactive ref with localStorage persistence
  - `setHouseholdContext()` to switch between personal and household mode
  - `clearHouseholdContext()` to return to personal mode

---

### Phase 3: Households System - 2026-01-20

#### Added
- **Households Store** (`stores/households.ts`):
  - Full CRUD for households
  - Member management: fetchMembers, updateMember, removeMember, leaveHousehold
  - State: households[], currentHousehold, members[], loading, error

- **Households Composable** (`composables/useHouseholds.ts`):
  - Wrapper with auth integration
  - Computed properties: isCurrentUserManager, isCurrentUserMember

- **Household Pages**:
  - `pages/households/index.vue` - List view with household cards, empty state
  - `pages/households/create.vue` - Create form with icon selection
  - `pages/households/[uid].vue` - Detail view with member management
    - Edit household form (manager only)
    - Delete household confirmation (manager only)
    - Member role/status management (manager only)
    - Leave household functionality

---

### Phase 4: Invitation System - 2026-01-20

#### Added
- **Invitations Composable** (`composables/useInvitations.ts`):
  - `createInvitation(householdUid, options)` - Create new invitation
  - `listInvitations(householdUid)` - List active invitations
  - `revokeInvitation(householdUid, invitationId)` - Revoke invitation
  - `getInvitationPreview(token)` - Public preview (no auth required)
  - `joinHousehold(token)` - Join household via invitation
  - `getInvitationLink(token)` - Generate shareable link
  - `copyInvitationLink(token)` - Copy link to clipboard

- **Invitation Pages**:
  - `pages/households/[uid]/invitations.vue` - Invitation management (manager only)
    - List active invitations with status badges
    - Create invitation dialog with expiry and max uses options
    - Copy invitation link to clipboard
    - Revoke invitation with confirmation
  - `pages/join/[token].vue` - Public invitation join page
    - Shows invitation preview (household name, icon, creator)
    - Login redirect with return URL for unauthenticated users
    - Join button for authenticated users
    - Error handling for expired/revoked/invalid invitations

---

### Phase 5: Household Analytics - 2026-01-20

#### Added
- **Household Analytics Page** (`pages/households/[uid]/analytics.vue`):
  - Monthly summary cards (income, expenses, net, transaction count)
  - Spending by member section with progress bars and percentages
  - Spending by category with nested member breakdown
  - Member overview table with detailed statistics
  - Month selector (last 12 months)
  - Polish locale formatting for dates and currency (PLN)

#### Changed
- **`pages/households/[uid].vue`** - Added Analytics button in header to navigate to analytics page

---

### Phase 6: Role-Based UI - 2026-01-20

#### Added
- **Permissions Composable** (`composables/usePermissions.ts`):
  - Centralized permission checking for role-based access control
  - Permission checkers: `canManageHousehold`, `canInviteMembers`, `canEditMember`, `canRemoveMember`, `canDeleteHousehold`, `canViewContent`, `canAddContent`, `canViewAnalytics`
  - Computed shortcuts: `isMember`, `isManager`, `isBlocked`, `isActive`
  - Permission error parsing with `parsePermissionError()`
  - Support for checking permissions on specific household or current household

- **Access Control Components** (`components/common/`):
  - `AccessDenied.vue` - Generic access denied page with different error types
    - Supports: not_authenticated, not_household_member, household_access_blocked, not_household_manager, household_not_found
    - Shows appropriate icons, titles, and action buttons
    - Login redirect for unauthenticated users
  - `BlockedAccess.vue` - Specific component for blocked users
    - Shows detailed explanation of blocked status
    - Lists what blocked users can and cannot do
    - Allows leaving the household

#### Changed
- **`pages/households/[uid].vue`** - Added blocked access detection with BlockedAccess component
- **`pages/households/[uid]/invitations.vue`** - Added manager-only access check with AccessDenied component
- **`pages/households/[uid]/analytics.vue`** - Added blocked access detection with BlockedAccess component

---

### Phase 7: UI Finalization - 2026-01-20

#### Added
- **Household Selector Component** (`components/household/HouseholdSelector.vue`):
  - Dropdown to switch between personal and household contexts
  - Shows current context (Personal or household name with icon)
  - Lists all user's households for quick switching
  - Link to manage households page
  - Works in both expanded and collapsed sidebar modes
  - Toast notifications on context switch

- **Skeleton Loader Components** (`components/common/`):
  - `SkeletonCard.vue` - Single skeleton card with configurable lines, icon, and badge
  - `SkeletonList.vue` - Multiple skeleton cards for list loading states

- **Sidebar Updates**:
  - Added Households link to main module navigation
  - Added HouseholdSelector to sidebar bottom section
  - Updated MobileSidebar with Households navigation

#### Changed
- **`components/global/GlobalSidebar.vue`**:
  - Added Households module to navigation
  - Added HouseholdSelector component
- **`components/global/MobileSidebar.vue`**:
  - Added Households to mobile navigation
- **`pages/households/index.vue`** - Replaced spinner with skeleton loader during loading

---

### Phase 8: Permission Error Handling - 2026-01-20

#### Changed
- **`composables/useApi.ts`** - Enhanced error handling:
  - 403 errors now show toast notifications with specific messages
    - Blocked user access
    - Manager-only access
    - Non-member access
  - 410 (Gone) errors show toast notification
  - 500+ (Server) errors show toast notification
  - Error messages parsed from backend detail field

---

### Phase 9: Landing Page & Global Route Protection - 2026-01-20

#### Added
- **Public Landing Page** (`pages/index.vue`):
  - Hero section with app branding and tagline
  - Feature cards showcasing Finance, Fitness, and Skills modules
  - CTA buttons for "Get Started Free" and "Sign In"
  - Navigation bar with login/register links
  - Footer with branding
  - Auto-redirect to `/home` if already authenticated

- **Global Auth Middleware** (`middleware/auth.global.ts`):
  - Automatically protects all routes except public ones
  - Public routes: `/`, `/login`, `/register`, `/join/*`
  - Redirects unauthenticated users to `/login` with return URL
  - Eliminates need for explicit `middleware: 'auth'` on each page

#### Changed
- **`pages/home.vue`** (renamed from `pages/index.vue`):
  - Now the authenticated user dashboard at `/home`
  - Updated SEO title to "Dashboard - Life Manager"

- **`middleware/guest.ts`** - Updated redirect target from `/` to `/home`

- **`pages/login.vue`** - Updated post-login redirect from `/` to `/home`

- **Removed explicit `middleware: 'auth'`** from pages (now handled globally):
  - `pages/profile.vue`
  - `pages/households/index.vue`
  - `pages/households/create.vue`
  - `pages/households/[uid].vue`
  - `pages/households/[uid]/invitations.vue`
  - `pages/households/[uid]/analytics.vue`

#### Removed
- **`middleware/auth.ts`** - Replaced by global middleware `auth.global.ts`
