<script setup lang="ts">
const valueProps = [
  {
    icon: "i-heroicons-chart-bar-square",
    color: "electric-green" as const,
    title: "Track every aspect of your life",
    description:
      "Finance, fitness, food, mood — all quantified and connected in one dashboard. Metrics you didn't know you needed, habits you didn't know you had.",
  },
  {
    icon: "i-heroicons-bell-alert",
    color: "warning-orange" as const,
    title: "The app remembers. You don't have to",
    description:
      "Set up notifications for anything — medicine reminders, overspend alerts, journal nudges. Configure it once and give your attention back to things that actually matter.",
  },
  {
    icon: "i-heroicons-device-phone-mobile",
    color: "cyber-blue" as const,
    title: "Browser, phone or installed. Your call",
    description:
      "Works as a website and installs as a PWA. Your data lives on the server — so wherever you log in, everything is exactly as you left it.",
  },
  {
    icon: "i-heroicons-lock-closed",
    color: "electric-green" as const,
    title: "Sensitive data? We can't read it either",
    description:
      "Journal entries and medicine logs are encrypted on your device before they ever leave it. The server stores ciphertext. Nobody — including us — can see what you wrote.",
  },
  {
    icon: "i-heroicons-squares-2x2",
    color: "cyber-blue" as const,
    title: "One app. Not seven",
    description:
      "Finance tracker, workout logger, pantry manager, journal, household finances — all in one platform, all talking to each other. No more switching context between half-baked single-purpose tools.",
  },
  {
    icon: "i-heroicons-users",
    color: "warning-orange" as const,
    title: "Your household, not just your phone",
    description:
      "Share a household context with flatmates or family. Split finances, manage shared pantry and see household-level analytics — without the group chat spreadsheet nightmare.",
  },
];

const colorClasses = {
  "electric-green": {
    bg: "bg-electric-green/10",
    text: "text-electric-green",
    border: "border-electric-green/15",
  },
  "warning-orange": {
    bg: "bg-warning-orange/10",
    text: "text-warning-orange",
    border: "border-warning-orange/15",
  },
  "cyber-blue": {
    bg: "bg-cyber-blue/10",
    text: "text-cyber-blue",
    border: "border-cyber-blue/15",
  },
};

const modules = [
  { name: "Finance", icon: "i-heroicons-banknotes", color: "electric-green" as const },
  { name: "Fitness", icon: "i-heroicons-fire", color: "warning-orange" as const },
  { name: "Food", icon: "i-heroicons-cake", color: "electric-green" as const },
  { name: "Journal", icon: "i-heroicons-pencil-square", color: "cyber-blue" as const },
  { name: "Households", icon: "i-heroicons-home-modern", color: "cyber-blue" as const },
];
</script>

<template>
  <div class="border-t border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">

      <!-- Header -->
      <div class="max-w-3xl mb-14 md:mb-16">
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-pure-white leading-tight mb-5">
          Everything you need<br class="hidden sm:block" />
          in one place
        </h2>
        <p class="text-pure-white/55 text-lg leading-relaxed">
          Not five apps. Not ten spreadsheets. One platform that tracks, reminds,
          syncs and protects — so you can focus on living, not managing.
        </p>
      </div>

      <!-- Value props grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="vp in valueProps"
          :key="vp.title"
          class="bg-card-black border rounded-2xl p-7 flex flex-col gap-4 hover:border-white/15 transition-colors"
          :class="colorClasses[vp.color].border"
        >
          <div
            class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
            :class="colorClasses[vp.color].bg"
          >
            <UIcon :name="vp.icon" class="w-5 h-5" :class="colorClasses[vp.color].text" />
          </div>
          <div>
            <h3 class="text-base font-bold text-pure-white mb-2 leading-snug">
              {{ vp.title }}
            </h3>
            <p class="text-pure-white/55 text-sm leading-relaxed">
              {{ vp.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- Module chips -->
      <div class="mt-14 pt-10 border-t border-border-gray">
        <p class="text-xs font-bold tracking-widest uppercase text-pure-white/35 mb-5">
          Modules included
        </p>
        <div class="flex flex-wrap gap-3">
          <div
            v-for="mod in modules"
            :key="mod.name"
            class="flex items-center gap-2 px-4 py-2 bg-card-black border border-border-gray rounded-full text-sm font-medium text-pure-white/70"
          >
            <UIcon
              :name="mod.icon"
              class="w-4 h-4"
              :class="colorClasses[mod.color].text"
            />
            {{ mod.name }}
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
