<script setup lang="ts">
definePageMeta({
  layout: "food",
});

const { currentHouseholdId } = useHouseholdContext();

const pageTitle = computed(() => {
  return currentHouseholdId.value ? "Shared Recipes" : "My Recipes";
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-pure-white">{{ pageTitle }}</h1>
        <p class="text-pure-white/60 mt-1">
          Recipe suggestions based on your products
        </p>
      </div>
    </div>

    <!-- Work in Progress Banner -->
    <div
      class="bg-warning-orange/10 border border-warning-orange/30 rounded-xl p-6"
    >
      <div class="flex items-center gap-4">
        <div
          class="w-12 h-12 rounded-full bg-warning-orange/20 flex items-center justify-center flex-shrink-0"
        >
          <UIcon
            name="i-heroicons-wrench-screwdriver"
            class="w-6 h-6 text-warning-orange"
          />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-warning-orange">
            Work in Progress
          </h3>
          <p class="text-pure-white/70 mt-1">
            The recipe system is under development. Coming soon:
          </p>
          <ul class="text-pure-white/60 mt-2 space-y-1 text-sm">
            <li class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-check"
                class="w-4 h-4 text-electric-green"
              />
              Send product list to AI and get recipe suggestions
            </li>

            <li class="flex items-center gap-2">
              <UIcon
                name="i-heroicons-check"
                class="w-4 h-4 text-electric-green"
              />
              Save favorite recipes to your collection
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Placeholder Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg bg-cyber-blue/10 flex items-center justify-center"
          >
            <UIcon
              name="i-heroicons-sparkles"
              class="w-5 h-5 text-cyber-blue"
            />
          </div>
          <div>
            <p class="text-pure-white/60 text-sm">Suggested Recipes</p>
            <p class="text-2xl font-bold text-pure-white">--</p>
          </div>
        </div>
      </div>

      <div class="bg-card-black border border-border-gray rounded-xl p-6">
        <div class="flex items-center gap-3 mb-4">
          <div
            class="w-10 h-10 rounded-lg bg-electric-green/10 flex items-center justify-center"
          >
            <UIcon
              name="i-heroicons-star"
              class="w-5 h-5 text-electric-green"
            />
          </div>
          <div>
            <p class="text-pure-white/60 text-sm">Rated Recipes</p>
            <p class="text-2xl font-bold text-pure-white">--</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Generate Recipes Button (disabled) -->
    <div class="bg-card-black border border-border-gray rounded-xl p-6">
      <div class="flex flex-col md:flex-row items-center gap-6">
        <div
          class="w-16 h-16 rounded-full bg-cyber-blue/10 flex items-center justify-center flex-shrink-0"
        >
          <UIcon name="i-heroicons-cpu-chip" class="w-8 h-8 text-cyber-blue" />
        </div>
        <div class="flex-1 text-center md:text-left">
          <h3 class="text-lg font-medium text-pure-white mb-2">
            Generate Recipes with AI
          </h3>
          <p class="text-pure-white/60">
            Select products from your pantry and AI will suggest recipes
            tailored to your ingredients and taste preferences.
          </p>
        </div>
        <button
          disabled
          class="px-6 py-3 bg-cyber-blue/20 text-cyber-blue/50 rounded-lg font-medium cursor-not-allowed"
        >
          Coming Soon
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div
      class="bg-card-black border border-border-gray rounded-xl p-12 text-center"
    >
      <div
        class="w-16 h-16 rounded-full bg-pure-white/5 flex items-center justify-center mx-auto mb-4"
      >
        <UIcon
          name="i-heroicons-book-open"
          class="w-8 h-8 text-pure-white/40"
        />
      </div>
      <h3 class="text-lg font-medium text-pure-white mb-2">No Recipes</h3>
      <p class="text-pure-white/60 max-w-md mx-auto">
        This section will display AI-suggested recipes and your ratings.
      </p>
    </div>
  </div>
</template>
