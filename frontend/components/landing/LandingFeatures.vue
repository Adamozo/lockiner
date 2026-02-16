<script setup lang="ts">
// Landing page features section

interface Feature {
  name: string;
  description: string;
  icon: string;
  color: "electric-green" | "warning-orange" | "cyber-blue" | "alert-red";
}

const features: Feature[] = [
  {
    name: "Finance",
    description:
      "Track expenses, manage budgets, and analyze spending patterns",
    icon: "i-heroicons-banknotes",
    color: "electric-green",
  },
  {
    name: "Fitness",
    description: "Log workouts, track weight, and monitor your gym progress",
    icon: "i-heroicons-fire",
    color: "warning-orange",
  },

  {
    name: "Food",
    description: "Plan meals, track nutrition, and manage your diet goals",
    icon: "i-heroicons-cake",
    color: "cyber-blue",
  },
];

const colorClasses = {
  "electric-green": {
    bg: "bg-electric-green/10",
    text: "text-electric-green",
  },
  "warning-orange": {
    bg: "bg-warning-orange/10",
    text: "text-warning-orange",
  },
  "cyber-blue": {
    bg: "bg-cyber-blue/10",
    text: "text-cyber-blue",
  },
  "alert-red": {
    bg: "bg-alert-red/10",
    text: "text-alert-red",
  },
};
</script>

<template>
  <div class="border-t border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <h2
        class="text-3xl md:text-4xl font-bold text-pure-white text-center mb-12"
      >
        Everything you need in one place
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="feature in features"
          :key="feature.name"
          class="bg-card-black border border-border-gray rounded-xl p-6 hover:border-pure-white/20 transition-colors"
        >
          <div
            :class="[
              'inline-flex items-center justify-center w-12 h-12 rounded-xl mb-4',
              colorClasses[feature.color].bg,
            ]"
          >
            <UIcon
              :name="feature.icon"
              :class="['w-6 h-6', colorClasses[feature.color].text]"
            />
          </div>
          <h3 class="text-xl font-semibold text-pure-white mb-2">
            {{ feature.name }}
          </h3>
          <p class="text-pure-white/60">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
