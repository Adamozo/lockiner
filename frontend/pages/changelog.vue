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

const { t } = useI18n()

const badgeConfig: Record<BadgeVariant, { classes: string }> = {
  new:      { classes: "bg-electric-green/10 text-electric-green border border-electric-green/20" },
  improved: { classes: "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/20" },
  fixed:    { classes: "bg-warning-orange/10 text-warning-orange border border-warning-orange/20" },
  infra:    { classes: "bg-pure-white/5 text-pure-white/50 border border-border-gray" },
};

const releases = computed<ChangelogRelease[]>(() => [
  {
    version: "Alpha 0.12",
    date: t('landing.cl_r1_date'),
    tag: "Current",
    highlight: t('landing.cl_r1_highlight'),
    changes: [
      {
        date: t('landing.cl_r1_g1_date'),
        label: t('landing.cl_r1_g1_label'),
        badge: "new",
        items: [
          t('landing.cl_r1_g1_i1'), t('landing.cl_r1_g1_i2'), t('landing.cl_r1_g1_i3'),
          t('landing.cl_r1_g1_i4'), t('landing.cl_r1_g1_i5'), t('landing.cl_r1_g1_i6'),
        ],
      },
      {
        date: t('landing.cl_r1_g2_date'),
        label: t('landing.cl_r1_g2_label'),
        badge: "new",
        items: [
          t('landing.cl_r1_g2_i1'), t('landing.cl_r1_g2_i2'), t('landing.cl_r1_g2_i3'),
          t('landing.cl_r1_g2_i4'), t('landing.cl_r1_g2_i5'), t('landing.cl_r1_g2_i6'), t('landing.cl_r1_g2_i7'),
        ],
      },
      {
        date: t('landing.cl_r1_g3_date'),
        label: t('landing.cl_r1_g3_label'),
        badge: "new",
        items: [
          t('landing.cl_r1_g3_i1'), t('landing.cl_r1_g3_i2'), t('landing.cl_r1_g3_i3'),
          t('landing.cl_r1_g3_i4'), t('landing.cl_r1_g3_i5'), t('landing.cl_r1_g3_i6'),
          t('landing.cl_r1_g3_i7'), t('landing.cl_r1_g3_i8'), t('landing.cl_r1_g3_i9'),
        ],
      },
    ],
  },
  {
    version: "Alpha 0.11",
    date: t('landing.cl_r2_date'),
    tag: "",
    highlight: t('landing.cl_r2_highlight'),
    changes: [
      {
        date: t('landing.cl_r2_g1_date'),
        label: t('landing.cl_r2_g1_label'),
        badge: "new",
        items: [
          t('landing.cl_r2_g1_i1'), t('landing.cl_r2_g1_i2'), t('landing.cl_r2_g1_i3'),
          t('landing.cl_r2_g1_i4'), t('landing.cl_r2_g1_i5'), t('landing.cl_r2_g1_i6'),
          t('landing.cl_r2_g1_i7'), t('landing.cl_r2_g1_i8'), t('landing.cl_r2_g1_i9'),
        ],
      },
    ],
  },
  {
    version: "Alpha 0.10",
    date: t('landing.cl_r3_date'),
    tag: "",
    highlight: t('landing.cl_r3_highlight'),
    changes: [
      {
        date: t('landing.cl_r3_g1_date'),
        label: t('landing.cl_r3_g1_label'),
        badge: "new",
        items: [
          t('landing.cl_r3_g1_i1'), t('landing.cl_r3_g1_i2'), t('landing.cl_r3_g1_i3'), t('landing.cl_r3_g1_i4'),
        ],
      },
      {
        date: t('landing.cl_r3_g2_date'),
        label: t('landing.cl_r3_g2_label'),
        badge: "new",
        items: [
          t('landing.cl_r3_g2_i1'), t('landing.cl_r3_g2_i2'), t('landing.cl_r3_g2_i3'),
          t('landing.cl_r3_g2_i4'), t('landing.cl_r3_g2_i5'),
        ],
      },
      {
        date: t('landing.cl_r3_g3_date'),
        label: t('landing.cl_r3_g3_label'),
        badge: "improved",
        items: [t('landing.cl_r3_g3_i1'), t('landing.cl_r3_g3_i2')],
      },
    ],
  },
  {
    version: "Alpha 0.9",
    date: t('landing.cl_r4_date'),
    tag: "",
    highlight: t('landing.cl_r4_highlight'),
    changes: [
      {
        date: t('landing.cl_r4_g1_date'),
        label: t('landing.cl_r4_g1_label'),
        badge: "new",
        items: [t('landing.cl_r4_g1_i1'), t('landing.cl_r4_g1_i2'), t('landing.cl_r4_g1_i3')],
      },
      {
        date: t('landing.cl_r4_g2_date'),
        label: t('landing.cl_r4_g2_label'),
        badge: "new",
        items: [
          t('landing.cl_r4_g2_i1'), t('landing.cl_r4_g2_i2'), t('landing.cl_r4_g2_i3'), t('landing.cl_r4_g2_i4'),
        ],
      },
      {
        date: t('landing.cl_r4_g3_date'),
        label: t('landing.cl_r4_g3_label'),
        badge: "new",
        items: [
          t('landing.cl_r4_g3_i1'), t('landing.cl_r4_g3_i2'), t('landing.cl_r4_g3_i3'), t('landing.cl_r4_g3_i4'),
        ],
      },
      {
        date: t('landing.cl_r4_g4_date'),
        label: t('landing.cl_r4_g4_label'),
        badge: "improved",
        items: [t('landing.cl_r4_g4_i1'), t('landing.cl_r4_g4_i2'), t('landing.cl_r4_g4_i3')],
      },
    ],
  },
  {
    version: "Alpha 0.8",
    date: t('landing.cl_r5_date'),
    tag: "",
    highlight: t('landing.cl_r5_highlight'),
    changes: [
      {
        date: t('landing.cl_r5_g1_date'),
        label: t('landing.cl_r5_g1_label'),
        badge: "new",
        items: [
          t('landing.cl_r5_g1_i1'), t('landing.cl_r5_g1_i2'), t('landing.cl_r5_g1_i3'),
          t('landing.cl_r5_g1_i4'), t('landing.cl_r5_g1_i5'),
        ],
      },
      {
        date: t('landing.cl_r5_g2_date'),
        label: t('landing.cl_r5_g2_label'),
        badge: "new",
        items: [
          t('landing.cl_r5_g2_i1'), t('landing.cl_r5_g2_i2'), t('landing.cl_r5_g2_i3'), t('landing.cl_r5_g2_i4'),
        ],
      },
      {
        date: t('landing.cl_r5_g3_date'),
        label: t('landing.cl_r5_g3_label'),
        badge: "new",
        items: [t('landing.cl_r5_g3_i1'), t('landing.cl_r5_g3_i2'), t('landing.cl_r5_g3_i3')],
      },
    ],
  },
]);
</script>

<template>
  <div class="min-h-screen bg-background-black">
    <LandingNav />

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">

      <!-- Page header -->
      <div class="mb-14">
        <p class="text-xs font-bold tracking-widest uppercase text-pure-white/35 mb-3">
          {{ $t('landing.changelog_subtitle') }}
        </p>
        <h1 class="text-3xl md:text-4xl font-bold text-pure-white mb-4 leading-tight">
          {{ $t('landing.changelog_title') }}
        </h1>
        <p class="text-pure-white/50 text-base leading-relaxed max-w-xl">
          {{ $t('landing.changelog_desc') }}
        </p>
      </div>

      <!-- Alpha badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-warning-orange/10 border border-warning-orange/25 rounded-full mb-14">
        <span class="w-2 h-2 rounded-full bg-warning-orange animate-pulse" />
        <span class="text-xs font-semibold text-warning-orange tracking-wide uppercase">
          {{ $t('landing.changelog_alpha_badge') }}
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
                {{ release.tag === 'Current' ? $t('landing.changelog_current') : release.tag }}
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
                    {{ $t('landing.badge_' + group.badge) }}
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
