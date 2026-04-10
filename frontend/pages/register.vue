<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

definePageMeta({
  layout: "auth",
  middleware: "guest",
});

const { t } = useI18n()

useSeoMeta({
  title: "Register - LockIner",
  description: "Create your LockIner account",
});

const authStore = useAuthStore();
const router = useRouter();
const toast = useToast();

const recoveryKey = ref<string | null>(null);

// Form state
const form = ref({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  voucherCode: "",
});
const loading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const errors = ref({
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
  voucherCode: "",
  general: "",
});

// Password strength indicator
const passwordStrength = computed(() => {
  const password = form.value.password;
  if (!password) return { score: 0, label: "", color: "" };

  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  if (score <= 1) return { score, label: t('auth.password_strength_weak'), color: "bg-danger-red" };
  if (score <= 2) return { score, label: t('auth.password_strength_fair'), color: "bg-warning-orange" };
  if (score <= 3) return { score, label: t('auth.password_strength_good'), color: "bg-cyber-blue" };
  return { score, label: t('auth.password_strength_strong'), color: "bg-electric-green" };
});

// Validation
const validateForm = (): boolean => {
  errors.value = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    voucherCode: "",
    general: "",
  };
  let valid = true;

  if (!form.value.voucherCode || form.value.voucherCode.trim().length === 0) {
    errors.value.voucherCode = t('auth.voucher_required');
    valid = false;
  }

  if (!form.value.name || form.value.name.trim().length < 2) {
    errors.value.name = t('auth.name_min');
    valid = false;
  }

  if (!form.value.email) {
    errors.value.email = t('auth.email_required');
    valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = t('auth.email_invalid');
    valid = false;
  }

  if (!form.value.password) {
    errors.value.password = t('auth.password_required');
    valid = false;
  } else if (form.value.password.length < 8) {
    errors.value.password = t('auth.password_min');
    valid = false;
  }

  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.confirm_password_required');
    valid = false;
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = t('auth.passwords_mismatch');
    valid = false;
  }

  return valid;
};

// Submit handler
const handleSubmit = async () => {
  if (!validateForm()) return;

  loading.value = true;
  errors.value.general = "";

  try {
    // Register the user — DEK is generated inside the store action
    const { recoveryKey: key } = await authStore.register({
      name: form.value.name.trim(),
      email: form.value.email,
      password: form.value.password,
      voucher_code: form.value.voucherCode.trim(),
    });

    // Show recovery key screen instead of redirecting immediately
    recoveryKey.value = key;
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; statusCode?: number };

    if (
      err.statusCode === 400 &&
      err.data?.detail?.toLowerCase().includes("voucher")
    ) {
      errors.value.voucherCode = t('auth.voucher_invalid');
    } else if (err.statusCode === 409 && err.data?.detail?.includes("email")) {
      errors.value.email = t('auth.email_taken');
    } else if (err.data?.detail) {
      errors.value.general = err.data.detail;
    } else {
      errors.value.general = t('auth.error_generic');
    }
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <!-- Recovery key screen shown after successful registration -->
  <AuthRecoveryKeyScreen
    v-if="recoveryKey"
    :recovery-key="recoveryKey"
    @proceed="router.push('/login')"
  />

  <div
    v-else
    class="bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden"
  >
    <!-- Header -->
    <div class="px-6 py-5 border-b border-border-gray relative">
      <div
        class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
      />
      <h1 class="text-2xl font-bold text-pure-white">{{ $t('auth.create_account') }}</h1>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="px-6 py-6 space-y-5">
      <!-- General error -->
      <div
        v-if="errors.general"
        class="p-4 bg-danger-red/10 border border-danger-red/30 rounded-lg"
      >
        <div class="flex items-center gap-2 text-danger-red">
          <UIcon
            name="i-heroicons-exclamation-circle"
            class="w-5 h-5 flex-shrink-0"
          />
          <span class="text-sm">{{ errors.general }}</span>
        </div>
      </div>

      <!-- Voucher Code -->
      <div>
        <label
          for="voucherCode"
          class="block text-sm font-medium text-pure-white mb-2"
        >
          {{ $t('auth.voucher_code') }}
          <span class="text-danger-red">*</span>
        </label>
        <div class="relative">
          <input
            id="voucherCode"
            v-model="form.voucherCode"
            type="text"
            autocomplete="off"
            :placeholder="$t('auth.voucher_placeholder')"
            :class="[
              'w-full px-4 py-2.5 pl-11 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors font-mono uppercase tracking-wider',
              errors.voucherCode
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-electric-green focus:ring-electric-green/30',
            ]"
          />
          <UIcon
            name="i-heroicons-ticket"
            class="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-pure-white/40"
          />
        </div>
        <p v-if="errors.voucherCode" class="mt-1 text-sm text-danger-red">
          {{ errors.voucherCode }}
        </p>
        <p v-else class="mt-1 text-xs text-pure-white/40">
          {{ $t('auth.voucher_hint') }}
        </p>
      </div>

      <!-- Name -->
      <div>
        <label
          for="name"
          class="block text-sm font-medium text-pure-white mb-2"
        >
          {{ $t('auth.name') }}
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          autocomplete="name"
          :placeholder="$t('auth.name_placeholder')"
          :class="[
            'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
            errors.name
              ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
              : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
          ]"
        />
        <p v-if="errors.name" class="mt-1 text-sm text-danger-red">
          {{ errors.name }}
        </p>
      </div>

      <!-- Email -->
      <div>
        <label
          for="email"
          class="block text-sm font-medium text-pure-white mb-2"
        >
          {{ $t('auth.email') }}
        </label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          autocomplete="email"
          :placeholder="$t('auth.email_placeholder')"
          :class="[
            'w-full px-4 py-2.5 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
            errors.email
              ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
              : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
          ]"
        />
        <p v-if="errors.email" class="mt-1 text-sm text-danger-red">
          {{ errors.email }}
        </p>
      </div>

      <!-- Password -->
      <div>
        <label
          for="password"
          class="block text-sm font-medium text-pure-white mb-2"
        >
          {{ $t('auth.password') }}
        </label>
        <div class="relative">
          <input
            id="password"
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :placeholder="$t('auth.password_create_placeholder')"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              errors.password
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showPassword = !showPassword"
          >
            <UIcon
              :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
              class="w-5 h-5"
            />
          </button>
        </div>
        <p v-if="errors.password" class="mt-1 text-sm text-danger-red">
          {{ errors.password }}
        </p>

        <!-- Password strength indicator -->
        <div v-if="form.password" class="mt-2">
          <div class="flex items-center gap-2">
            <div
              class="flex-1 h-1.5 bg-border-gray rounded-full overflow-hidden"
            >
              <div
                class="h-full transition-all duration-300"
                :class="passwordStrength.color"
                :style="{ width: `${(passwordStrength.score / 5) * 100}%` }"
              />
            </div>
            <span
              class="text-xs"
              :class="passwordStrength.color.replace('bg-', 'text-')"
            >
              {{ passwordStrength.label }}
            </span>
          </div>
        </div>
      </div>

      <!-- Confirm Password -->
      <div>
        <label
          for="confirmPassword"
          class="block text-sm font-medium text-pure-white mb-2"
        >
          {{ $t('auth.confirm_password') }}
        </label>
        <div class="relative">
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            autocomplete="new-password"
            :placeholder="$t('auth.confirm_password_placeholder')"
            :class="[
              'w-full px-4 py-2.5 pr-12 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 transition-colors',
              errors.confirmPassword
                ? 'border-danger-red focus:border-danger-red focus:ring-danger-red/30'
                : 'border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30',
            ]"
          />
          <button
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-pure-white/40 hover:text-pure-white transition-colors"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <UIcon
              :name="
                showConfirmPassword
                  ? 'i-heroicons-eye-slash'
                  : 'i-heroicons-eye'
              "
              class="w-5 h-5"
            />
          </button>
        </div>
        <p v-if="errors.confirmPassword" class="mt-1 text-sm text-danger-red">
          {{ errors.confirmPassword }}
        </p>
      </div>

      <!-- Submit -->
      <BaseButton
        type="submit"
        variant="primary"
        :loading="loading"
        class="w-full"
      >
        {{ $t('auth.create_account_btn') }}
      </BaseButton>

      <!-- Login link -->
      <p class="text-center text-sm text-pure-white/60">
        {{ $t('auth.already_account') }}
        <NuxtLink
          to="/login"
          class="text-cyber-blue hover:text-cyber-blue/80 font-medium transition-colors"
        >
          {{ $t('auth.sign_in') }}
        </NuxtLink>
      </p>
    </form>
  </div>
</template>
