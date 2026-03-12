<script setup lang="ts">
definePageMeta({ layout: 'admin' })
useSeoMeta({ title: 'Admin — OFF Search - LockIner' })

const api = useApi()
const toast = useToast()

const query = ref('')
const barcode = ref('')
const lang = ref('')
const limit = ref(20)

const searchResults = ref<any[]>([])
const barcodeResult = ref<any>(null)
const searching = ref(false)
const selectedProduct = ref<any>(null)

// Wyszukiwanie po nazwie
const handleSearch = async () => {
  if (query.value.trim().length < 2) return
  searching.value = true
  barcodeResult.value = null
  selectedProduct.value = null
  try {
    const res = await api<{ query: string; count: number; results: any[] }>(
      `/api/v1/admin/off/search?q=${encodeURIComponent(query.value)}&limit=${limit.value}${lang.value ? `&lang=${lang.value}` : ''}`
    )
    searchResults.value = res.results
    if (res.results.length === 0) toast.add({ title: 'Brak wyników', color: 'yellow' })
  } catch {
    toast.add({ title: 'Błąd wyszukiwania', color: 'red' })
  } finally {
    searching.value = false
  }
}

// Wyszukiwanie po kodzie kreskowym
const handleBarcode = async () => {
  if (!barcode.value.trim()) return
  searching.value = true
  searchResults.value = []
  selectedProduct.value = null
  try {
    barcodeResult.value = await api<any>(`/api/v1/admin/off/barcode/${barcode.value.trim()}`)
    selectedProduct.value = barcodeResult.value
  } catch (e: any) {
    if (e?.status === 404) toast.add({ title: 'Nie znaleziono', description: `Brak produktu o kodzie ${barcode.value}`, color: 'yellow' })
    else toast.add({ title: 'Błąd', color: 'red' })
    barcodeResult.value = null
  } finally {
    searching.value = false
  }
}

const nutriscore_color = (grade: string) => ({
  a: 'text-electric-green bg-electric-green/10',
  b: 'text-electric-green/70 bg-electric-green/5',
  c: 'text-warning-orange bg-warning-orange/10',
  d: 'text-danger-red/70 bg-danger-red/5',
  e: 'text-danger-red bg-danger-red/10',
}[grade?.toLowerCase()] ?? 'text-pure-white/40 bg-white/5')

const fmt = (v: any) => v != null ? Number(v).toFixed(1) + 'g' : '—'
const fmtKcal = (v: any) => v != null ? Number(v).toFixed(0) + ' kcal' : '—'
</script>

<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-bold text-pure-white flex items-center gap-3">
        <UIcon name="i-heroicons-magnifying-glass" class="w-7 h-7 text-warning-orange" />
        Open Food Facts Search
      </h1>
      <p class="mt-1 text-pure-white/50 text-sm">Przeszukaj bazę 4M+ produktów — po nazwie lub kodzie EAN</p>
    </header>

    <!-- Wyszukiwarki -->
    <div class="grid md:grid-cols-2 gap-4">
      <!-- Po nazwie -->
      <div class="bg-card-black border border-border-gray rounded-xl p-5 space-y-3">
        <h3 class="text-xs font-semibold text-pure-white/40 uppercase tracking-wider">Szukaj po nazwie</h3>
        <div class="flex gap-2">
          <input
            v-model="query"
            type="text"
            placeholder="np. jogurt, coca-cola..."
            @keyup.enter="handleSearch"
            class="flex-1 px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-warning-orange"
          />
          <button
            @click="handleSearch"
            :disabled="searching || query.trim().length < 2"
            class="px-4 py-2 bg-warning-orange/10 border border-warning-orange/30 rounded-lg text-warning-orange hover:bg-warning-orange/20 transition-colors disabled:opacity-40"
          >
            <UIcon v-if="!searching" name="i-heroicons-magnifying-glass" class="w-4 h-4" />
            <div v-else class="w-4 h-4 border-2 border-warning-orange border-t-transparent rounded-full animate-spin" />
          </button>
        </div>
        <div class="flex gap-2">
          <select
            v-model="lang"
            class="px-2 py-1.5 bg-background-black border border-border-gray rounded-lg text-xs text-pure-white/70 focus:outline-none focus:border-warning-orange"
          >
            <option value="">Wszystkie języki</option>
            <option value="pl">Polski</option>
            <option value="en">Angielski</option>
            <option value="de">Niemiecki</option>
            <option value="fr">Francuski</option>
          </select>
          <select
            v-model.number="limit"
            class="px-2 py-1.5 bg-background-black border border-border-gray rounded-lg text-xs text-pure-white/70 focus:outline-none focus:border-warning-orange"
          >
            <option :value="10">10 wyników</option>
            <option :value="20">20 wyników</option>
            <option :value="50">50 wyników</option>
            <option :value="100">100 wyników</option>
          </select>
        </div>
      </div>

      <!-- Po kodzie EAN -->
      <div class="bg-card-black border border-border-gray rounded-xl p-5 space-y-3">
        <h3 class="text-xs font-semibold text-pure-white/40 uppercase tracking-wider">Szukaj po kodzie EAN</h3>
        <div class="flex gap-2">
          <input
            v-model="barcode"
            type="text"
            placeholder="np. 5901234567890"
            @keyup.enter="handleBarcode"
            class="flex-1 px-3 py-2 bg-background-black border border-border-gray rounded-lg text-pure-white placeholder-pure-white/20 focus:outline-none focus:border-warning-orange font-mono"
          />
          <button
            @click="handleBarcode"
            :disabled="searching || !barcode.trim()"
            class="px-4 py-2 bg-warning-orange/10 border border-warning-orange/30 rounded-lg text-warning-orange hover:bg-warning-orange/20 transition-colors disabled:opacity-40"
          >
            <UIcon v-if="!searching" name="i-heroicons-viewfinder-circle" class="w-4 h-4" />
            <div v-else class="w-4 h-4 border-2 border-warning-orange border-t-transparent rounded-full animate-spin" />
          </button>
        </div>
        <p class="text-xs text-pure-white/30">Wpisz pełny kod EAN-8 lub EAN-13</p>
      </div>
    </div>

    <!-- Wyniki wyszukiwania (lista) + szczegóły -->
    <div v-if="searchResults.length || selectedProduct" class="grid md:grid-cols-2 gap-4">

      <!-- Lista wyników -->
      <div v-if="searchResults.length" class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="px-4 py-3 border-b border-border-gray">
          <span class="text-xs text-pure-white/40">{{ searchResults.length }} wyników</span>
        </div>
        <div class="divide-y divide-border-gray/50 max-h-[600px] overflow-y-auto">
          <button
            v-for="p in searchResults" :key="p.code"
            @click="selectedProduct = p"
            class="w-full flex items-center gap-3 px-4 py-3 hover:bg-background-black/40 transition-colors text-left"
            :class="selectedProduct?.code === p.code ? 'bg-warning-orange/5 border-l-2 border-warning-orange' : ''"
          >
            <img v-if="p.image_url" :src="p.image_url" class="w-10 h-10 object-contain rounded flex-shrink-0" />
            <div v-else class="w-10 h-10 bg-background-black rounded flex-shrink-0 flex items-center justify-center">
              <UIcon name="i-heroicons-photo" class="w-5 h-5 text-pure-white/20" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm text-pure-white font-medium truncate">{{ p.product_name }}</div>
              <div class="text-xs text-pure-white/40 truncate">{{ p.brands || '—' }} · {{ p.code }}</div>
            </div>
            <span v-if="p.nutriscore_grade" class="text-xs font-bold uppercase px-1.5 py-0.5 rounded" :class="nutriscore_color(p.nutriscore_grade)">
              {{ p.nutriscore_grade }}
            </span>
          </button>
        </div>
      </div>

      <!-- Szczegóły produktu -->
      <div v-if="selectedProduct" class="bg-card-black border border-border-gray rounded-xl overflow-hidden">
        <div class="flex items-start gap-4 p-5 border-b border-border-gray">
          <img v-if="selectedProduct.image_url" :src="selectedProduct.image_url_full || selectedProduct.image_url" class="w-20 h-20 object-contain rounded" />
          <div class="flex-1 min-w-0">
            <h2 class="text-base font-bold text-pure-white">{{ selectedProduct.product_name }}</h2>
            <p v-if="selectedProduct.brands" class="text-sm text-pure-white/50 mt-0.5">{{ selectedProduct.brands }}</p>
            <p class="text-xs text-pure-white/30 font-mono mt-1">EAN: {{ selectedProduct.code }}</p>
            <div class="flex items-center gap-2 mt-2">
              <span v-if="selectedProduct.nutriscore_grade" class="text-xs font-bold uppercase px-2 py-0.5 rounded" :class="nutriscore_color(selectedProduct.nutriscore_grade)">
                Nutri-Score {{ selectedProduct.nutriscore_grade?.toUpperCase() }}
              </span>
              <span v-if="selectedProduct.nova_group" class="text-xs px-2 py-0.5 rounded bg-white/5 text-pure-white/40">
                NOVA {{ selectedProduct.nova_group }}
              </span>
            </div>
          </div>
        </div>

        <!-- Wartości odżywcze -->
        <div class="p-5 space-y-4">
          <h3 class="text-xs font-semibold text-pure-white/40 uppercase tracking-wider">Wartości odżywcze / 100g</h3>
          <div class="grid grid-cols-2 gap-2">
            <div class="bg-background-black rounded-lg p-3">
              <div class="text-xs text-pure-white/40 mb-0.5">Kalorie</div>
              <div class="text-lg font-bold text-warning-orange">{{ fmtKcal(selectedProduct.calories) }}</div>
            </div>
            <div class="bg-background-black rounded-lg p-3">
              <div class="text-xs text-pure-white/40 mb-0.5">Białko</div>
              <div class="text-lg font-bold text-cyber-blue">{{ fmt(selectedProduct.protein) }}</div>
            </div>
            <div class="bg-background-black rounded-lg p-3">
              <div class="text-xs text-pure-white/40 mb-0.5">Węglowodany</div>
              <div class="text-lg font-bold text-electric-green">{{ fmt(selectedProduct.carbohydrates) }}</div>
            </div>
            <div class="bg-background-black rounded-lg p-3">
              <div class="text-xs text-pure-white/40 mb-0.5">Tłuszcze</div>
              <div class="text-lg font-bold text-pure-white/70">{{ fmt(selectedProduct.fat) }}</div>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div class="bg-background-black rounded-lg p-2.5">
              <div class="text-xs text-pure-white/30">Błonnik</div>
              <div class="text-sm font-semibold text-pure-white/60">{{ fmt(selectedProduct.fiber) }}</div>
            </div>
            <div class="bg-background-black rounded-lg p-2.5">
              <div class="text-xs text-pure-white/30">Cukry</div>
              <div class="text-sm font-semibold text-pure-white/60">{{ fmt(selectedProduct.sugar) }}</div>
            </div>
            <div class="bg-background-black rounded-lg p-2.5">
              <div class="text-xs text-pure-white/30">Sól</div>
              <div class="text-sm font-semibold text-pure-white/60">{{ fmt(selectedProduct.salt) }}</div>
            </div>
          </div>

          <!-- Pozostałe dane -->
          <div v-if="selectedProduct.quantity" class="text-xs text-pure-white/30">Opakowanie: {{ selectedProduct.quantity }}</div>
          <div v-if="selectedProduct.lang" class="text-xs text-pure-white/30">Język: {{ selectedProduct.lang }}</div>
          <div v-if="selectedProduct.countries_tags?.length" class="text-xs text-pure-white/30">
            Kraje: {{ selectedProduct.countries_tags.slice(0, 3).join(', ') }}
          </div>

          <!-- Raw JSON (dla devów) -->
          <details class="mt-2">
            <summary class="text-xs text-pure-white/30 cursor-pointer hover:text-pure-white/50">Pełny JSON</summary>
            <pre class="mt-2 text-xs text-pure-white/50 bg-background-black rounded-lg p-3 overflow-x-auto max-h-64">{{ JSON.stringify(selectedProduct, null, 2) }}</pre>
          </details>
        </div>
      </div>
    </div>

    <!-- Pusty stan -->
    <div v-else-if="!searching" class="text-center py-16 text-pure-white/20">
      <UIcon name="i-heroicons-magnifying-glass" class="w-12 h-12 mx-auto mb-3" />
      <p>Wpisz nazwę produktu lub kod EAN żeby zacząć</p>
    </div>
  </div>
</template>
