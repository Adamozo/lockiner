<script setup lang="ts">
</script>

<template>
  <div
    class="p-4 bg-cyber-blue/10 border border-cyber-blue/30 rounded-lg backdrop-blur-sm"
  >
    <div class="flex">
      <UIcon
        name="i-heroicons-information-circle"
        class="w-5 h-5 text-cyber-blue mr-3 flex-shrink-0 mt-0.5"
      />
      <div class="text-sm text-pure-white/80">
        <p class="font-medium text-pure-white mb-1">
          About OCR Providers
        </p>
        <p>
          Configure multiple AI providers for receipt OCR processing. Only
          one provider can be active at a time. Your API keys are stored
          securely and encrypted.
        </p>
        <ul class="mt-2 space-y-1 list-disc list-inside">
          <li>
            <strong>Gemini:</strong> Get API key from
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              class="text-cyber-blue hover:underline"
              >Google AI Studio</a
            >
          </li>
          <li>
            <strong>Claude:</strong> Get API key from
            <a
              href="https://console.anthropic.com/"
              target="_blank"
              class="text-cyber-blue hover:underline"
              >Anthropic Console</a
            >
          </li>
          <li>
            <strong>OpenAI:</strong> Get API key from
            <a
              href="https://platform.openai.com/api-keys"
              target="_blank"
              class="text-cyber-blue hover:underline"
              >OpenAI Platform</a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
