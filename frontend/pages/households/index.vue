<script setup lang="ts">
import { useHouseholds } from "~/composables/useHouseholds";

definePageMeta({
  layout: "default",
});

useSeoMeta({
  title: "Households - LockIner",
  description: "Manage your households",
});

const { households, loading, error, fetchHouseholds, hasHouseholds } =
  useHouseholds();

// Fetch households on mount
onMounted(async () => {
  await fetchHouseholds();
});

// Format date
const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString("pl-PL", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
</script>

<template>
  <div class="space-y-8">
    <!-- Page header -->
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-pure-white">Households</h1>
        <p class="mt-2 text-pure-white/60">
          Manage your households and shared expenses
        </p>
      </div>
      <NuxtLink to="/households/create">
        <BaseButton variant="primary" icon="i-heroicons-plus">
          Create Household
        </BaseButton>
      </NuxtLink>
    </header>

    <!-- Info box -->
    <div class="p-4 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg">
      <div class="flex">
        <UIcon
          name="i-heroicons-information-circle"
          class="w-5 h-5 text-cyber-blue mr-3 flex-shrink-0 mt-0.5"
        />
        <div class="text-sm text-pure-white/80">
          <p class="font-medium text-pure-white mb-1">About Households</p>
          <p>
            Households allow you to share expenses with family members or
            roommates. Each household has its own transactions, categories, and
            analytics. You can be a member of multiple households.
          </p>
        </div>
      </div>
    </div>

    <!-- Loading state with skeleton -->
    <div
      v-if="loading && !hasHouseholds"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      <CommonSkeletonCard
        v-for="i in 3"
        :key="i"
        :lines="1"
        :show-icon="true"
        :show-badge="false"
      />
    </div>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="p-6 bg-danger-red/10 border border-danger-red/30 rounded-lg"
    >
      <div class="flex items-center gap-3 text-danger-red">
        <UIcon
          name="i-heroicons-exclamation-circle"
          class="w-6 h-6 flex-shrink-0"
        />
        <span>{{ error }}</span>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="!hasHouseholds" class="text-center py-16">
      <div
        class="w-20 h-20 mx-auto mb-6 rounded-full bg-card-black border border-border-gray flex items-center justify-center"
      >
        <UIcon name="i-heroicons-home" class="w-10 h-10 text-pure-white/40" />
      </div>
      <h2 class="text-xl font-semibold text-pure-white mb-2">
        No households yet
      </h2>
      <p class="text-pure-white/60 mb-6 max-w-md mx-auto">
        Create a household to start tracking shared expenses with family or
        roommates.
      </p>
      <NuxtLink to="/households/create">
        <BaseButton variant="primary" icon="i-heroicons-plus">
          Create Your First Household
        </BaseButton>
      </NuxtLink>
    </div>

    <!-- Households grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <NuxtLink
        v-for="household in households"
        :key="household.uid"
        :to="`/households/${household.uid}`"
        class="group"
      >
        <div
          class="bg-card-black border border-border-gray rounded-lg overflow-hidden hover:border-cyber-blue/50 transition-all duration-200"
        >
          <!-- Card header with gradient -->
          <div class="h-2 bg-gradient-to-r from-cyber-blue to-electric-green" />

          <div class="p-6">
            <!-- Icon and name -->
            <div class="flex items-start gap-4 mb-4">
              <div
                class="w-12 h-12 rounded-lg bg-cyber-blue/10 border border-cyber-blue/30 flex items-center justify-center flex-shrink-0"
              >
                <span v-if="household.icon" class="text-2xl">{{
                  household.icon
                }}</span>
                <UIcon
                  v-else
                  name="i-heroicons-home"
                  class="w-6 h-6 text-cyber-blue"
                />
              </div>
              <div class="flex-1 min-w-0">
                <h3
                  class="text-lg font-semibold text-pure-white group-hover:text-cyber-blue transition-colors truncate"
                >
                  {{ household.name }}
                </h3>
                <p
                  v-if="household.description"
                  class="text-sm text-pure-white/60 line-clamp-2 mt-1"
                >
                  {{ household.description }}
                </p>
              </div>
            </div>

            <!-- Footer -->
            <div
              class="flex items-center justify-between text-sm text-pure-white/40"
            >
              <span>Created {{ formatDate(household.created_at) }}</span>
              <UIcon
                name="i-heroicons-chevron-right"
                class="w-5 h-5 group-hover:text-cyber-blue transition-colors"
              />
            </div>
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
