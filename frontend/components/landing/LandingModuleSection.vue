<script setup lang="ts">
import { ref, computed } from "vue";

export interface ModuleSlide {
  tab: string;
  icon: string;
  title: string;
  description: string;
  highlights: string[];
}

export interface ModuleData {
  name: string;
  headline: string;
  subheadline: string;
  icon: string;
  color: "electric-green" | "warning-orange" | "cyber-blue";
  comingSoon?: boolean;
  slides: ModuleSlide[];
}

const props = defineProps<{ module: ModuleData }>();

const colorMap = {
  "electric-green": {
    bg: "bg-electric-green/10",
    bgStrong: "bg-electric-green/15",
    text: "text-electric-green",
    border: "border-electric-green/20",
    check: "bg-electric-green/15 text-electric-green",
    activeTab: "bg-electric-green/10 text-electric-green font-semibold",
    inactiveTab: "text-pure-white/45 hover:text-pure-white/75 hover:bg-white/5",
    activeMobileTab: "text-electric-green font-bold",
    dot: "bg-electric-green",
    dotInactive: "bg-electric-green/25",
  },
  "warning-orange": {
    bg: "bg-warning-orange/10",
    bgStrong: "bg-warning-orange/15",
    text: "text-warning-orange",
    border: "border-warning-orange/20",
    check: "bg-warning-orange/15 text-warning-orange",
    activeTab: "bg-warning-orange/10 text-warning-orange font-semibold",
    inactiveTab: "text-pure-white/45 hover:text-pure-white/75 hover:bg-white/5",
    activeMobileTab: "text-warning-orange font-bold",
    dot: "bg-warning-orange",
    dotInactive: "bg-warning-orange/25",
  },
  "cyber-blue": {
    bg: "bg-cyber-blue/10",
    bgStrong: "bg-cyber-blue/15",
    text: "text-cyber-blue",
    border: "border-cyber-blue/20",
    check: "bg-cyber-blue/15 text-cyber-blue",
    activeTab: "bg-cyber-blue/10 text-cyber-blue font-semibold",
    inactiveTab: "text-pure-white/45 hover:text-pure-white/75 hover:bg-white/5",
    activeMobileTab: "text-cyber-blue font-bold",
    dot: "bg-cyber-blue",
    dotInactive: "bg-cyber-blue/25",
  },
};

const c = computed(() => colorMap[props.module.color]);
const current = ref(0);
const total = computed(() => props.module.slides.length);

const prevIndex = computed(() => (current.value - 1 + total.value) % total.value);
const nextIndex = computed(() => (current.value + 1) % total.value);

function goTo(i: number) {
  current.value = (i + total.value) % total.value;
}

// Touch swipe
let touchStartX = 0;
function onTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX;
}
function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) < 40) return;
  if (dx < 0) goTo(current.value + 1);
  else goTo(current.value - 1);
}
</script>

<template>
  <section class="border-t border-border-gray">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28">

      <!-- Section header -->
      <div class="mb-12 md:mb-16">
        <div class="flex items-center gap-2.5 mb-6">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
            :class="c.bg"
          >
            <UIcon :name="module.icon" class="w-4 h-4" :class="c.text" />
          </div>
          <span class="text-sm font-bold tracking-widest uppercase" :class="c.text">
            {{ module.name }}
          </span>
          <span
            v-if="module.comingSoon"
            class="text-xs px-2.5 py-0.5 rounded-full bg-white/8 text-white/40 border border-white/10 font-medium"
          >
            coming soon
          </span>
        </div>

        <h2
          class="text-4xl md:text-5xl lg:text-6xl font-bold text-pure-white leading-tight mb-5 max-w-4xl"
        >
          {{ module.headline }}
        </h2>

        <p class="text-pure-white/55 text-lg leading-relaxed max-w-2xl">
          {{ module.subheadline }}
        </p>
      </div>

      <!-- Tab nav + content -->
      <div class="flex flex-col lg:flex-row gap-4 lg:gap-8">

        <!-- Desktop: vertical tab list -->
        <nav class="hidden lg:block lg:w-52 shrink-0">
          <div class="flex flex-col gap-1.5">
            <button
              v-for="(slide, i) in module.slides"
              :key="slide.tab"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-left transition-all duration-150 w-full"
              :class="current === i ? c.activeTab : c.inactiveTab"
              @click="current = i"
            >
              <UIcon :name="slide.icon" class="w-4 h-4 shrink-0" />
              <span class="text-sm whitespace-nowrap">{{ slide.tab }}</span>
            </button>
          </div>
        </nav>

        <!-- Content card -->
        <div class="flex-1 flex flex-col gap-0">

          <!-- Mobile swiper tab bar -->
          <div class="lg:hidden flex items-center justify-between mb-3 select-none">
            <!-- Prev -->
            <button
              class="flex items-center gap-1.5 text-sm text-pure-white/35 hover:text-pure-white/60 transition-colors min-w-0 flex-1"
              @click="goTo(current - 1)"
            >
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4 shrink-0" />
              <span class="truncate">{{ module.slides[prevIndex].tab }}</span>
            </button>

            <!-- Current -->
            <div class="flex items-center gap-1.5 px-3">
              <UIcon :name="module.slides[current].icon" class="w-4 h-4 shrink-0" :class="c.text" />
              <span class="text-sm" :class="c.activeMobileTab">{{ module.slides[current].tab }}</span>
            </div>

            <!-- Next -->
            <button
              class="flex items-center gap-1.5 text-sm text-pure-white/35 hover:text-pure-white/60 transition-colors min-w-0 flex-1 justify-end"
              @click="goTo(current + 1)"
            >
              <span class="truncate">{{ module.slides[nextIndex].tab }}</span>
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4 shrink-0" />
            </button>
          </div>

          <!-- Card -->
          <div
            class="flex-1 bg-card-black border rounded-2xl overflow-hidden"
            :class="c.border"
            @touchstart.passive="onTouchStart"
            @touchend.passive="onTouchEnd"
          >
            <div
              v-for="(slide, i) in module.slides"
              :key="slide.tab"
              v-show="current === i"
              class="p-6 md:p-8 lg:p-10"
            >
              <h3
                class="text-2xl md:text-3xl font-bold text-pure-white mb-4 leading-snug"
              >
                {{ slide.title }}
              </h3>
              <p
                class="text-pure-white/60 text-base leading-relaxed mb-8 max-w-2xl"
              >
                {{ slide.description }}
              </p>
              <ul class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <li
                  v-for="h in slide.highlights"
                  :key="h"
                  class="flex items-center gap-3 text-sm text-pure-white/70"
                >
                  <span
                    class="w-5 h-5 rounded-md flex items-center justify-center shrink-0"
                    :class="c.check"
                  >
                    <UIcon name="i-heroicons-check" class="w-3 h-3" />
                  </span>
                  {{ h }}
                </li>
              </ul>
            </div>
          </div>

          <!-- Mobile dot indicators -->
          <div class="lg:hidden flex justify-center gap-1.5 mt-3">
            <span
              v-for="(_, i) in module.slides"
              :key="i"
              class="rounded-full transition-all duration-200"
              :class="i === current ? [c.dot, 'w-4 h-1'] : [c.dotInactive, 'w-1 h-1']"
            />
          </div>

        </div>
      </div>
    </div>
  </section>
</template>
