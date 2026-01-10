# LockIner Frontend

Nuxt 4 + Vue 3 + TypeScript frontend for personal finance management.

## Tech Stack

- **Framework**: Nuxt 4
- **UI Library**: Vue 3 Composition API
- **Language**: TypeScript (strict mode)
- **Styling**: UnoCSS (utility-first)
- **Components**: @nuxt/ui (Nuxt UI)
- **State Management**: Pinia + Composables
- **Validation**: Zod schemas
- **HTTP Client**: $fetch (auto-configured)

## Project Structure

```
frontend/
├── app.vue                 # Root component with layout
├── nuxt.config.ts         # Nuxt configuration
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── pages/                 # File-based routing
│   ├── index.vue         # Dashboard
│   ├── transactions.vue  # Transaction CRUD
│   ├── receipts.vue      # Receipt management
│   └── import.vue        # CSV import
├── components/           # Vue components
│   ├── AppLayout.vue     # Main layout with navigation
│   ├── TransactionList.vue
│   ├── TransactionForm.vue
│   └── CategoryBadge.vue
├── composables/          # Reusable composition functions
│   ├── useApi.ts         # API client
│   ├── useTransactions.ts
│   ├── useCategories.ts
│   └── useReceipts.ts
├── stores/               # Pinia stores
│   └── categories.ts     # Category state management
├── types/                # TypeScript definitions
│   └── api.ts           # API interfaces
└── utils/                # Utility functions
    └── formatters.ts    # Date/currency formatters
```

## Development

### Local Development (Docker)

The frontend runs in a Docker container with hot reload enabled:

```bash
# Start containers
just up

# View frontend logs
just logs-frontend

# Access shell
just shell-frontend

# Open in browser
just open  # http://localhost:3000
```

### Manual Development (without Docker)

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The frontend communicates with the FastAPI backend at `http://backend:8000` (in Docker) or `http://localhost:8000` (local).

API proxy is configured in `nuxt.config.ts`:

```typescript
nitro: {
  devProxy: {
    '/api': {
      target: 'http://backend:8000',
      changeOrigin: true,
    },
  },
}
```

All API calls use the `/api/v1/*` prefix and are automatically proxied to the backend.

## Key Features

### 1. Transaction Management
- View all transactions with filtering
- Add new transactions (income/expense)
- Edit existing transactions
- Delete transactions
- Import from CSV

### 2. Category System
- Global category state (Pinia store)
- Cached category data (5-minute TTL)
- Color-coded category badges
- Icon support for categories

### 3. Receipt Processing (Coming Soon)
- Image upload with drag & drop
- AI-powered OCR with Claude
- Automatic transaction creation
- Manual verification workflow

### 4. Dashboard Analytics (Coming Soon)
- Income/expense overview
- Category breakdown charts
- Spending trends
- Budget tracking

## Composable Pattern

All API logic is abstracted into composables for reusability:

```typescript
// In any component
const { transactions, loading, fetchTransactions, createTransaction } = useTransactions()

onMounted(async () => {
  await fetchTransactions({ limit: 10 })
})

const addTransaction = async (data) => {
  await createTransaction(data)
}
```

## Form Validation

Forms use Zod schemas for validation:

```typescript
import { z } from 'zod'

const schema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  amount: z.number().min(0.01),
  category: z.string().min(1),
})
```

## Styling with UnoCSS

UnoCSS provides Tailwind-like utilities with better performance:

```vue
<template>
  <div class="container mx-auto p-4 md:p-8">
    <h1 class="text-2xl md:text-4xl font-bold text-gray-800 dark:text-gray-100">
      Dashboard
    </h1>
  </div>
</template>
```

## TypeScript Types

All API types are defined in `types/api.ts`:

```typescript
import type { Transaction, TransactionCreate } from '~/types/api'

const createTransaction = async (data: TransactionCreate): Promise<Transaction> => {
  // ...
}
```

## Environment Variables

Configure the backend API URL via environment variables:

```env
API_BASE_URL=http://backend:8000
```

## Hot Reload

Hot module replacement (HMR) is enabled in Docker via volume mounts:

```yaml
volumes:
  - ./frontend:/app:rw
  - /app/node_modules  # Exclude node_modules
```

Changes to `.vue`, `.ts`, or `.css` files trigger automatic browser refresh.

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Output in .output/ directory
npm run preview
```

## Troubleshooting

### Container won't start

```bash
# Rebuild container
just rebuild frontend

# Check logs
just logs-frontend
```

### Hot reload not working

- Ensure volume mounts are correct in `docker-compose.yml`
- Check file permissions (should be readable by container user)
- Try restarting the container: `just restart`

### API calls failing

- Verify backend is running: `just health`
- Check API proxy configuration in `nuxt.config.ts`
- Inspect network tab in browser DevTools

## Contributing

1. Follow Vue 3 Composition API patterns (`<script setup>`)
2. Use TypeScript with strict mode (no `any` types)
3. Create reusable composables for shared logic
4. Use UnoCSS utility classes for styling
5. Add proper error handling and loading states
6. Test on mobile (responsive design required)

## License

Private project - not for public distribution.
