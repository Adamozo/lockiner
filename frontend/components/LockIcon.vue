<script setup lang="ts">
interface Props {
  size?: number;
}

const props = withDefaults(defineProps<Props>(), {
  size: 32,
});

// Generate unique ID for this instance to avoid SVG gradient conflicts
const uniqueId = Math.random().toString(36).substring(2, 9)
const lockGradientId = `lockGradient-${uniqueId}`
const keyholeGradientId = `keyholeGradient-${uniqueId}`
const glowId = `glow-${uniqueId}`
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 100 100"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="transition-transform duration-300"
  >
    <defs>
      <!-- Gradient for lock body -->
      <linearGradient :id="lockGradientId" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: #00d4ff; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #00ff88; stop-opacity: 1" />
      </linearGradient>

      <!-- Gradient for keyhole -->
      <linearGradient :id="keyholeGradientId" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color: #0a0a0a; stop-opacity: 1" />
        <stop offset="100%" style="stop-color: #1a1a1a; stop-opacity: 0.9" />
      </linearGradient>

      <!-- Glow effect -->
      <filter :id="glowId" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="3.5" result="coloredBlur" />
        <feMerge>
          <feMergeNode in="coloredBlur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>

    <!-- Group with glow filter -->
    <g :filter="`url(#${glowId})`">
      <!-- Lock shackle (top arc) -->
      <path
        d="M 30 40
           L 30 28
           C 30 12, 70 12, 70 28
           L 70 40"
        fill="none"
        :stroke="`url(#${lockGradientId})`"
        stroke-width="8"
        stroke-linecap="round"
      />

      <!-- Lock body (rounded rectangle) -->
      <rect
        x="20"
        y="40"
        width="60"
        height="50"
        rx="8"
        ry="8"
        :fill="`url(#${lockGradientId})`"
        stroke="#00D4FF"
        stroke-width="2"
      />
    </g>

    <!-- Keyhole circle -->
    <circle
      cx="50"
      cy="58"
      r="8"
      :fill="`url(#${keyholeGradientId})`"
      stroke="#00D4FF"
      stroke-width="1"
    />

    <!-- Keyhole slot -->
    <rect
      x="47"
      y="62"
      width="6"
      height="14"
      rx="2"
      :fill="`url(#${keyholeGradientId})`"
    />

    <!-- Light reflection on lock body -->
    <path
      d="M 28 50 C 32 55, 34 65, 30 75 C 26 82, 24 78, 26 68 C 28 58, 26 48, 28 50 Z"
      fill="#FFFFFF"
      opacity="0.2"
      style="filter: blur(2px)"
    />
  </svg>
</template>
