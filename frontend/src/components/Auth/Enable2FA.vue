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
import axios from 'axios'

export default defineComponent({
  name: 'Enable2FA',
  setup() {
    const provisioningUri = ref('')
    const qrCodeBase64 = ref('')
    const error = ref('')

    const enable2FA = async () => {
      try {
        const token = localStorage.getItem('accessToken') // Retrieve stored token
        const response = await axios.post('/auth/enable-2fa', null, {
          headers: { Authorization: `Bearer ${token}` },
        })
        provisioningUri.value = response.data.provisioning_uri
        qrCodeBase64.value = response.data.qr_code_base64
      } catch (err) {
        if (axios.isAxiosError(err)) {
          error.value = 'An unexpected error occurred while enabling 2FA.'
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
