<script setup lang="ts">
interface Props {
  icon?: string;
  title?: string;
  description?: string;
  variant?: "default" | "muted";
}

withDefaults(defineProps<Props>(), {
  icon: "i-heroicons-inbox",
  title: "No records yet",
  description: "Start adding data to see it here",
  variant: "default",
});
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <!-- Custom SVG Illustration -->
    <div class="relative mb-6">
      <!-- Icon container -->
      <div
        class="relative w-20 h-20 rounded-full flex items-center justify-center border-2 border-dashed"
        :class="
          variant === 'muted'
            ? 'border-border-gray bg-card-black/50'
            : 'border-cyber-blue/40 bg-gradient-to-br from-cyber-blue/10 to-electric-green/5'
        "
      >
        <UIcon
          :name="icon"
          class="w-10 h-10"
          :class="
            variant === 'muted' ? 'text-pure-white/30' : 'text-cyber-blue/60'
          "
        />
      </div>
    </div>

    <!-- Text content -->
    <h3
      class="text-lg font-medium mb-2"
      :class="variant === 'muted' ? 'text-pure-white/50' : 'text-pure-white/80'"
    >
      {{ title }}
    </h3>
    <p
      class="text-sm text-center max-w-xs"
      :class="variant === 'muted' ? 'text-pure-white/30' : 'text-pure-white/50'"
    >
      {{ description }}
    </p>

    <!-- Action slot -->
    <div v-if="$slots.action" class="mt-6">
      <slot name="action" />
    </div>
  </div>
</template>
