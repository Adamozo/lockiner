<script setup lang="ts">
interface Props {
  icon: string | null
  size?: number
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 32,
  color: 'currentColor',
})

// Map icon names to their SVG paths
const iconPaths: Record<string, { path: string; viewBox?: string }> = {
  // Health / Medical
  health: {
    path: 'M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z',
  },
  // Transport / Car
  car: {
    path: 'M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z',
  },
  // Entertainment / Film
  film: {
    path: 'M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z',
  },
  // Food / Pizza
  pizza: {
    path: 'M12 2C8.43 2 5.23 3.54 3.01 6L12 22l8.99-16C18.78 3.55 15.57 2 12 2zM7 7c0-1.1.9-2 2-2s2 .9 2 2-.9 2-2 2-2-.9-2-2zm5 8c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z',
  },
  // Bills / Document
  document: {
    path: 'M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z',
  },
  // Shopping / Cart
  shopping: {
    path: 'M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z',
  },
  // Home / House
  home: {
    path: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z',
  },
  // Education / Book
  education: {
    path: 'M12 3L1 9l11 6 9-4.91V17h2V9L12 3zm0 14.18L4 13v4.18l8 4.36 8-4.36V13l-8 4.18z',
  },
  // Savings / Piggy Bank
  savings: {
    path: 'M19.83 7.5l-2.27-2.27c.07-.42.18-.81.32-1.15A1.498 1.498 0 0016.5 2c-1.64 0-3.09.79-4 2h-5A5.5 5.5 0 002 9.5c0 2.36 1.49 4.38 3.58 5.16l-.78 2.62c-.23.79.32 1.58 1.14 1.58h3.02c.55 0 1.01-.42 1.06-.96l.14-1.9h3.68l.14 1.9c.05.54.51.96 1.06.96h3.02c.82 0 1.37-.79 1.14-1.58l-.4-1.35c.66-.33 1.26-.76 1.78-1.29l2.38.8c.5.17 1.04-.19 1.04-.71v-2.96c0-.3-.15-.58-.4-.75l-2.77-1.82c.53-.69.9-1.45 1.06-2.25.05-.25.08-.5.08-.76 0-.35-.05-.68-.13-1zM17.5 9c-.83 0-1.5-.67-1.5-1.5S16.67 6 17.5 6s1.5.67 1.5 1.5S18.33 9 17.5 9z',
  },
  // Utilities / Bolt
  utilities: {
    path: 'M7 2v11h3v9l7-12h-4l4-8z',
  },
  // Subscriptions / Repeat
  subscriptions: {
    path: 'M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z',
  },
  // Gifts / Gift
  gift: {
    path: 'M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z',
  },
  // Travel / Plane
  travel: {
    path: 'M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z',
  },
  // Default / Category
  default: {
    path: 'M12 2l-5.5 9h11L12 2zm0 3.84L13.93 9h-3.87L12 5.84zM17.5 13c-2.49 0-4.5 2.01-4.5 4.5s2.01 4.5 4.5 4.5 4.5-2.01 4.5-4.5-2.01-4.5-4.5-4.5zm0 7c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5zM3 21.5h8v-8H3v8zm2-6h4v4H5v-4z',
  },
}

// Get icon path, fallback to default
const iconData = computed(() => {
  const key = props.icon?.toLowerCase() || 'default'
  return iconPaths[key] || iconPaths.default
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="category-icon"
  >
    <path
      :d="iconData.path"
      :fill="color"
    />
  </svg>
</template>

<style scoped>
.category-icon {
  flex-shrink: 0;
}
</style>
