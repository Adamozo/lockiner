<script setup lang="ts">
interface Props {
  icon: string
  size?: number
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 32,
  color: 'currentColor',
})

// Map icon names to their SVG paths
const iconPaths: Record<string, { path: string; viewBox?: string }> = {
  // House - family home
  house: {
    path: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z',
  },
  // Home with garden
  garden: {
    path: 'M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3zm0 2.84l6 5.38V18h-2v-6H8v6H6v-6.78l6-5.38zM17 4h2v2.25l-2-1.8V4z',
  },
  // Apartment building
  apartment: {
    path: 'M17 11V3H7v4H3v14h8v-4h2v4h8V11h-4zM7 19H5v-2h2v2zm0-4H5v-2h2v2zm0-4H5V9h2v2zm4 4H9v-2h2v2zm0-4H9V9h2v2zm0-4H9V5h2v2zm4 8h-2v-2h2v2zm0-4h-2V9h2v2zm0-4h-2V5h2v2zm4 12h-2v-2h2v2zm0-4h-2v-2h2v2z',
  },
  // Neighborhood / community
  neighborhood: {
    path: 'M1 11v10h6v-5h2v5h6V11L8 6l-7 5zm12 8h-2v-5H5v5H3v-6.97l5-3.57 5 3.57V19zm4-12h2v2h-2v-2zm0 4h2v2h-2v-2zm0 4h2v2h-2v-2zm0 4h2v2h-2v-2zm-2-8h-2v-2h4V3H7v2h2v2h2v2h4v2z',
  },
  // Castle / estate
  castle: {
    path: 'M21 9V7h-2V5h-2V3h-2v2h-2V3H11v2H9V3H7v2H5v2H3v2H1v12h22V9h-2zm0 10h-6v-4c0-1.1-.9-2-2-2s-2 .9-2 2v4H5V9h2v2h2V9h2v2h2V9h2v2h2V9h2v10z',
  },
  // Family group
  family: {
    path: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z',
  },
  // People group
  group: {
    path: 'M12 12.75c1.63 0 3.07.39 4.24.9 1.08.48 1.76 1.56 1.76 2.73V18H6v-1.61c0-1.18.68-2.26 1.76-2.73 1.17-.52 2.61-.91 4.24-.91zM4 13c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm1.13 1.1c-.37-.06-.74-.1-1.13-.1-.99 0-1.93.21-2.78.58A2.01 2.01 0 000 16.43V18h4.5v-1.61c0-.83.23-1.61.63-2.29zM20 13c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm4 3.43c0-.81-.48-1.53-1.22-1.85A6.95 6.95 0 0020 14c-.39 0-.76.04-1.13.1.4.68.63 1.46.63 2.29V18H24v-1.57zM12 6c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3z',
  },
  // Building / office
  building: {
    path: 'M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2v-2zm0 4h-2v2h2v-2z',
  },
}

// Get icon path, fallback to house
const iconData = computed(() => {
  const key = props.icon?.toLowerCase() || 'house'
  return iconPaths[key] || iconPaths.house
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="household-icon"
  >
    <path
      :d="iconData.path"
      :fill="color"
    />
  </svg>
</template>

<style scoped>
.household-icon {
  flex-shrink: 0;
}
</style>
