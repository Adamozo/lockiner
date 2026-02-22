<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

definePageMeta({
  layout: "auth",
  middleware: "guest",
});

const { t } = useI18n()

useSeoMeta({
  title: "Login - LockIner",
  description: "Login to your LockIner account",
});

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const toast = useToast();

// Form state
const form = ref({
  email: "",
  password: "",
});
const loading = ref(false);
const showPassword = ref(false);
const errors = ref({
  email: "",
  password: "",
  general: "",
});

// Validation
const validateForm = (): boolean => {
  errors.value = { email: "", password: "", general: "" };
  let valid = true;

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
  }

  return valid;
};

// Submit handler
const handleSubmit = async () => {
  if (!validateForm()) return;

  loading.value = true;
  errors.value.general = "";

  try {
    await authStore.login({
      email: form.value.email,
      password: form.value.password,
    });

    // If 2FA is required, don't redirect - show 2FA step
    if (authStore.requiresTwoFactor) {
      return;
    }

    toast.add({
      title: t('auth.login_success_title'),
      description: t('auth.login_success_desc'),
      color: "green",
    });

    // Redirect to intended destination or home
    const redirect = (route.query.redirect as string) || "/home";
    await router.push(redirect);
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string }; statusCode?: number };

    if (err.statusCode === 401) {
      errors.value.general = t('auth.invalid_credentials');
    } else if (err.data?.detail) {
      errors.value.general = err.data.detail;
    } else {
      errors.value.general = t('auth.error_generic');
    }
  } finally {
    loading.value = false;
  }
};

// 2FA state
const twoFactorCode = ref("");
const useRecoveryCode = ref(false);
const twoFactorLoading = ref(false);

const handleTwoFactorVerify = async () => {
  if (!twoFactorCode.value) return;

  twoFactorLoading.value = true;
  errors.value.general = "";

  try {
    await authStore.verifyTwoFactor(twoFactorCode.value);

    toast.add({
      title: t('auth.login_success_title'),
      description: t('auth.login_success_desc'),
      color: "green",
    });

    const redirect = (route.query.redirect as string) || "/home";
    await router.push(redirect);
  } catch {
    errors.value.general = t('auth.invalid_verification_code');
    twoFactorCode.value = "";
  } finally {
    twoFactorLoading.value = false;
  }
};

const cancelTwoFactor = () => {
  authStore.clearTwoFactor();
  twoFactorCode.value = "";
  useRecoveryCode.value = false;
  errors.value.general = "";
};
</script>

<template>
  <div
    class="bg-card-black border border-border-gray rounded-lg shadow-xl overflow-hidden"
  >
    <!-- Login Form (hidden when 2FA is required) -->
    <template v-if="!authStore.requiresTwoFactor">
      <!-- Header -->
      <div class="px-6 py-5 border-b border-border-gray relative">
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        />
        <h1 class="text-2xl font-bold text-pure-white">{{ $t('auth.welcome_back') }}</h1>
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
              autocomplete="current-password"
              :placeholder="$t('auth.password_placeholder')"
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
        </div>

        <!-- Submit -->
        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
          class="w-full"
        >
          {{ $t('auth.sign_in') }}
        </BaseButton>

        <!-- Register link -->
        <p class="text-center text-sm text-pure-white/60">
          {{ $t('auth.no_account') }}
          <NuxtLink
            to="/register"
            class="text-cyber-blue hover:text-cyber-blue/80 font-medium transition-colors"
          >
            {{ $t('auth.create_one') }}
          </NuxtLink>
        </p>
      </form>
    </template>

    <!-- 2FA Verification Panel -->
    <template v-else>
      <!-- Header -->
      <div class="px-6 py-5 border-b border-border-gray relative">
        <div
          class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-cyber-blue to-electric-green"
        />
        <h1 class="text-2xl font-bold text-pure-white">{{ $t('auth.two_factor_title') }}</h1>
        <p class="mt-1 text-sm text-pure-white/60">
          {{ useRecoveryCode ? $t('auth.two_factor_enter_recovery') : $t('auth.two_factor_enter_code') }}
        </p>
      </div>

      <form @submit.prevent="handleTwoFactorVerify" class="px-6 py-6 space-y-5">
        <!-- Error -->
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

        <!-- Code input -->
        <div>
          <label
            for="twoFactorCode"
            class="block text-sm font-medium text-pure-white mb-2"
          >
            {{ useRecoveryCode ? $t('auth.recovery_code') : $t('auth.verification_code') }}
          </label>
          <input
            id="twoFactorCode"
            v-model="twoFactorCode"
            type="text"
            :placeholder="useRecoveryCode ? 'XXXX-XXXX' : '000000'"
            autocomplete="one-time-code"
            :maxlength="useRecoveryCode ? 9 : 6"
            class="w-full px-4 py-3 border rounded-lg bg-background-black text-pure-white placeholder-pure-white/40 focus:outline-none focus:ring-2 border-border-gray focus:border-cyber-blue focus:ring-cyber-blue/30 text-center text-xl font-mono tracking-widest"
          />
        </div>

        <!-- Toggle recovery code mode -->
        <button
          type="button"
          class="text-sm text-cyber-blue hover:text-cyber-blue/80 transition-colors"
          @click="useRecoveryCode = !useRecoveryCode; twoFactorCode = ''"
        >
          {{ useRecoveryCode ? $t('auth.use_authenticator_instead') : $t('auth.use_recovery_instead') }}
        </button>

        <!-- Buttons -->
        <div class="flex gap-3">
          <BaseButton
            type="button"
            variant="ghost"
            class="flex-1"
            @click="cancelTwoFactor"
          >
            {{ $t('common.cancel') }}
          </BaseButton>
          <BaseButton
            type="submit"
            variant="primary"
            :loading="twoFactorLoading"
            class="flex-1"
          >
            {{ $t('auth.verify') }}
          </BaseButton>
        </div>
      </form>
    </template>
  </div>
</template>
