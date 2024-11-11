<template>
  <div>
    <h2>Enable 2FA</h2>
    <button @click="enable2FA" class="button">
      Enable Two-Factor Authentication
    </button>
    <div v-if="provisioningUri">
      <p>Provisioning URI: {{ provisioningUri }}</p>
      <img :src="'data:image/png;base64,' + qrCodeBase64" alt="QR Code" />
    </div>
    <p v-if="error" class="feedback">{{ error }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { AuthError, OtpSetup, enable2fa } from  '@/services/authService';
import { useAuthStore } from '@/stores/authStore';


export default defineComponent({
  name: 'Enable2FA',
  setup() {
    const authStore =  useAuthStore();
    const provisioningUri = ref('')
    const qrCodeBase64 = ref('')
    const error = ref('')

    const enable2FA = async () => {
      try {
        const otpSetup:OtpSetup = await enable2fa(authStore.getTokenStr);
        provisioningUri.value = otpSetup.provisioningUri;
        qrCodeBase64.value = otpSetup.qrCodeBase64;
      } catch (err) {
        if (err instanceof AuthError) {
          error.value = err.message;
        } else {
          throw new Error('Unexpected error');
        }
      }
    }

    return {
      enable2FA,
      provisioningUri,
      qrCodeBase64,
      error,
    }
  },
})
</script>
