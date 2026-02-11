<script setup lang="ts">
import { formatCurrency } from "~/utils/formatters";
import type { BudgetStatus } from "~/types/api";

const props = defineProps<{
  budgets: BudgetStatus[];
}>();

// Get status color
const getStatusColor = (status: "ok" | "warning" | "over") => {
  switch (status) {
    case "ok":
      return "bg-electric-green";
    case "warning":
      return "bg-warning-orange";
    case "over":
      return "bg-danger-red";
    default:
      return "bg-pure-white/20";
  }
};

// Get status text color
const getStatusTextColor = (status: "ok" | "warning" | "over") => {
  switch (status) {
    case "ok":
      return "text-electric-green";
    case "warning":
      return "text-warning-orange";
    case "over":
      return "text-danger-red";
    default:
      return "text-pure-white/60";
  }
};

// Get status icon
const getStatusIcon = (status: "ok" | "warning" | "over") => {
  switch (status) {
    case "ok":
      return "i-heroicons-check-circle";
    case "warning":
      return "i-heroicons-exclamation-triangle";
    case "over":
      return "i-heroicons-x-circle";
    default:
      return "i-heroicons-minus-circle";
  }
};

// Get status label
const getStatusLabel = (status: "ok" | "warning" | "over") => {
  switch (status) {
    case "ok":
      return "On Track";
    case "warning":
      return "Warning";
    case "over":
      return "Over Budget";
    default:
      return "Unknown";
  }
};
</script>

<template>
  <div>
    <div class="space-y-4 max-h-[480px] overflow-y-auto pr-1 scrollbar-thin">
    <div
      v-for="budget in budgets"
      :key="budget.category"
      class="bg-background-black rounded-lg p-4 border border-border-gray"
    >
      <!-- Category Header -->
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center"
            :style="{ backgroundColor: (budget.color || '#00d4ff') + '20' }"
          >
            <CategoryIcon
              :icon="budget.icon"
              :size="24"
              :color="budget.color || '#00d4ff'"
            />
          </div>
          <div>
            <h4 class="font-semibold text-pure-white">{{ budget.category }}</h4>
            <p class="text-sm text-pure-white/60">
              {{ formatCurrency(budget.spent) }} /
              {{ formatCurrency(budget.budget_limit) }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <UIcon
            :name="getStatusIcon(budget.status)"
            class="w-5 h-5"
            :class="getStatusTextColor(budget.status)"
          />
          <span
            class="text-sm font-semibold"
            :class="getStatusTextColor(budget.status)"
          >
            {{ getStatusLabel(budget.status) }}
          </span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div
        class="relative w-full h-3 bg-card-black rounded-full overflow-hidden"
      >
        <div
          class="absolute top-0 left-0 h-full transition-all duration-500"
          :class="getStatusColor(budget.status)"
          :style="{ width: `${Math.min(budget.percentage, 100)}%` }"
        ></div>
      </div>

      <!-- Percentage & Remaining -->
      <div class="flex items-center justify-between mt-2">
        <span
          class="text-sm font-semibold"
          :class="getStatusTextColor(budget.status)"
        >
          {{ budget.percentage.toFixed(1) }}% used
        </span>
        <span class="text-sm text-pure-white/60">
          {{
            budget.remaining >= 0
              ? formatCurrency(budget.remaining) + " left"
              : formatCurrency(Math.abs(budget.remaining)) + " over"
          }}
        </span>
      </div>
    </div>
    </div>

    <!-- Manage Budget Limits Link -->
    <div v-if="budgets.length > 0" class="mt-6 text-center">
      <NuxtLink
        to="/finance/limits"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyber-blue/10 border border-cyber-blue text-cyber-blue hover:bg-cyber-blue hover:text-background-black transition-all duration-300"
      >
        <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" />
        <span class="font-medium">Manage Budget Limits</span>
        <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
      </NuxtLink>
    </div>

    <!-- No budgets message -->
    <div v-if="budgets.length === 0" class="text-center py-8">
      <p class="text-pure-white/40 mb-4">No budget limits configured.</p>
      <NuxtLink
        to="/finance/limits"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyber-blue text-background-black hover:bg-cyber-blue/90 transition-all duration-300 font-medium"
      >
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Set Up Budget Limits
      </NuxtLink>
    </div>
  </div>
</template>
