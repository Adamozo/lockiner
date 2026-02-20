<script setup lang="ts">
definePageMeta({
  layout: false,
});

useSeoMeta({
  title: "Changelog - LockIner",
  description: "What's new in LockIner — release history and updates",
});

type BadgeVariant = "new" | "improved" | "fixed" | "infra";

interface ChangelogEntry {
  date: string;
  label: string;
  badge: BadgeVariant;
  items: string[];
}

interface ChangelogRelease {
  version: string;
  date: string;
  tag: string;
  highlight: string;
  changes: ChangelogEntry[];
}

const badgeConfig: Record<BadgeVariant, { label: string; classes: string }> = {
  new: {
    label: "New",
    classes: "bg-electric-green/10 text-electric-green border border-electric-green/20",
  },
  improved: {
    label: "Improved",
    classes: "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/20",
  },
  fixed: {
    label: "Fixed",
    classes: "bg-warning-orange/10 text-warning-orange border border-warning-orange/20",
  },
  infra: {
    label: "Infra",
    classes: "bg-pure-white/5 text-pure-white/50 border border-border-gray",
  },
};

const releases: ChangelogRelease[] = [
  {
    version: "Alpha 0.11",
    date: "20 February 2026",
    tag: "Current",
    highlight: "Shopping Lists — collaborative shopping with household sharing",
    changes: [
      {
        date: "20 Feb 2026",
        label: "Shopping Lists",
        badge: "new",
        items: [
          "Standalone Shopping module — lists can be for any store type (grocery, hardware, etc.)",
          "Create lists with optional store name and planned date",
          "Private lists (owner only) or household-shared lists (all active household members have equal access)",
          "3-state item status cycle: Pending → In Cart → Purchased — tap the icon to advance",
          "Items grouped by category with purchased items collapsed into a separate section",
          "Progress bar showing purchased / total items, with in-cart count displayed separately",
          "Quick-add form with optional details: quantity, unit, category and note",
          "Inline editing of list name and store name directly on the detail page",
          "Mark list as Completed to archive it; Completed lists have a dedicated view",
        ],
      },
    ],
  },
  {
    version: "Alpha 0.10",
    date: "20 February 2026",
    tag: "",
    highlight: "Backup & Data Export with Google Drive integration",
    changes: [
      {
        date: "20 Feb 2026",
        label: "Backup & Data Export",
        badge: "new",
        items: [
          "Full data export: all personal data (workouts, journal, medicines, finance, food) packed into an AES-256 encrypted ZIP",
          "Household backup: household admins can export the entire household dataset separately",
          "Password-protected archives — set your own encryption password, viewable any time in settings",
          "Manual download from the Settings → Backup tab",
        ],
      },
      {
        date: "20 Feb 2026",
        label: "Google Drive integration",
        badge: "new",
        items: [
          "Connect your Google account via OAuth to enable automatic Drive uploads",
          "Scheduled auto-backup: daily, weekly or monthly at a chosen time",
          "Backups uploaded to your own Google Drive — app stores only a refresh token, never the file contents",
          "Household managers can connect a separate Drive account for household backups",
          "Error notifications: app alerts you if Drive access is revoked, quota is exceeded or a folder is missing",
        ],
      },
      {
        date: "20 Feb 2026",
        label: "Settings",
        badge: "improved",
        items: [
          "Settings page reorganised into tabs: General, Notifications, Backup, Integrations",
          "Mobile view uses a custom styled dropdown instead of a raw tab bar",
        ],
      },
    ],
  },
  {
    version: "Alpha 0.9",
    date: "17 February 2026",
    tag: "",
    highlight: "Medicines, per-set workout tracking & journal encryption",
    changes: [
      {
        date: "17 Feb 2026",
        label: "Fitness — Medicines",
        badge: "new",
        items: [
          "Medicine cabinet: add medications with name, dosage and frequency",
          "Individual medicine detail pages with schedule and edit support",
          "Medicine log entries encrypted client-side before leaving the device",
        ],
      },
      {
        date: "17 Feb 2026",
        label: "Fitness — Workouts",
        badge: "new",
        items: [
          "Per-set weight & rep tracking — each set logged independently",
          "Full-page workout form replaces modal (routes: /fitness/workouts/new, /fitness/workouts/[id])",
          "Draft workout support: workouts auto-saved every 3 seconds while in progress",
          "Set completion toggling with visual feedback",
        ],
      },
      {
        date: "17 Feb 2026",
        label: "Journal",
        badge: "new",
        items: [
          "Daily journal entries with mood tracking (1–5 scale)",
          "Client-side AES-GCM encryption — server stores only ciphertext",
          "History view with calendar navigation",
          "Monthly report summaries with mood trend charts",
        ],
      },
      {
        date: "17 Feb 2026",
        label: "Landing page",
        badge: "improved",
        items: [
          "Module sections for Finance, Fitness, Food, Journal — each with screenshots and feature highlights",
          "PWA install prompt dialog",
          "Privacy Policy and Terms of Service subpages",
        ],
      },
    ],
  },
  {
    version: "Alpha 0.8",
    date: "January 2026",
    tag: "",
    highlight: "Finance analytics, receipt scanning & household budgets",
    changes: [
      {
        date: "Jan 2026",
        label: "Finance",
        badge: "new",
        items: [
          "Transaction list with category tagging and search",
          "Spending limits per category with over-budget alerts",
          "CSV/bank import for bulk transaction upload",
          "Receipt scanning — upload photo, extract merchant and total automatically",
          "Finance analytics dashboard: monthly breakdown, top categories, trend charts",
        ],
      },
      {
        date: "Jan 2026",
        label: "Households",
        badge: "new",
        items: [
          "Create and join households via invite token",
          "Shared household finance view with per-member contribution breakdown",
          "Household-level analytics separate from personal finance",
          "Invitation management page for household admins",
        ],
      },
      {
        date: "Jan 2026",
        label: "Notifications",
        badge: "new",
        items: [
          "In-app notification centre",
          "Admin broadcast notifications to all users",
          "Unread badge on nav icon",
        ],
      },
    ],
  },
];
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">

      <!-- Page header -->
      <div class="mb-14">
        <p class="text-xs font-bold tracking-widest uppercase text-pure-white/35 mb-3">
          Release history
        </p>
        <h1 class="text-3xl md:text-4xl font-bold text-pure-white mb-4 leading-tight">
          Changelog
        </h1>
        <p class="text-pure-white/50 text-base leading-relaxed max-w-xl">
          LockIner is in active alpha development. This page tracks what's been
          shipped — features, improvements and fixes — in rough chronological order.
        </p>
      </div>

      <!-- Alpha badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-warning-orange/10 border border-warning-orange/25 rounded-full mb-14">
        <span class="w-2 h-2 rounded-full bg-warning-orange animate-pulse" />
        <span class="text-xs font-semibold text-warning-orange tracking-wide uppercase">
          Alpha — invite-only access
        </span>
      </div>

      <!-- Timeline -->
      <div class="relative">
        <!-- Vertical line -->
        <div class="absolute left-0 top-0 bottom-0 w-px bg-border-gray ml-[7px] hidden sm:block" />

        <div class="space-y-16">
          <div
            v-for="release in releases"
            :key="release.version"
            class="sm:pl-10 relative"
          >
            <!-- Timeline dot -->
            <div class="absolute left-0 top-1 w-4 h-4 rounded-full bg-background-black border-2 border-electric-green hidden sm:flex items-center justify-center">
              <div class="w-1.5 h-1.5 rounded-full bg-electric-green" />
            </div>

            <!-- Release header -->
            <div class="flex flex-wrap items-center gap-3 mb-2">
              <span class="text-xl font-bold text-pure-white">{{ release.version }}</span>
              <span
                v-if="release.tag"
                class="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-electric-green/10 text-electric-green border border-electric-green/25"
              >
                {{ release.tag }}
              </span>
            </div>
            <p class="text-xs text-pure-white/35 font-medium mb-1">{{ release.date }}</p>
            <p class="text-pure-white/60 text-sm mb-8">{{ release.highlight }}</p>

            <!-- Change groups -->
            <div class="space-y-6">
              <div
                v-for="group in release.changes"
                :key="group.label"
                class="bg-card-black border border-border-gray rounded-2xl p-6 hover:border-white/10 transition-colors"
              >
                <div class="flex flex-wrap items-center gap-3 mb-4">
                  <span
                    class="text-xs font-semibold px-2.5 py-1 rounded-full"
                    :class="badgeConfig[group.badge].classes"
                  >
                    {{ badgeConfig[group.badge].label }}
                  </span>
                  <span class="text-sm font-semibold text-pure-white">{{ group.label }}</span>
                  <span class="text-xs text-pure-white/30 ml-auto">{{ group.date }}</span>
                </div>
                <ul class="space-y-2">
                  <li
                    v-for="item in group.items"
                    :key="item"
                    class="flex gap-2.5 text-sm text-pure-white/60 leading-relaxed"
                  >
                    <span class="mt-2 w-1 h-1 rounded-full bg-pure-white/25 shrink-0" />
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <LandingFooter />
  </div>
</template>
