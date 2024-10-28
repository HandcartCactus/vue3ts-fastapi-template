<template>
  <div>
    <h2>Verify 2FA</h2>
    <form @submit.prevent="verify2FA">
      <div class="input">
        <label for="otp" class="label">One-Time Password:</label>
        <input id="otp" v-model="otp" aria-label="OTP" required />
      </div>
      <button type="submit" class="button">Verify 2FA</button>
      <p v-if="error" class="feedback">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'Verify2FA',
  emits: ['verified'],
  setup(_, { emit }) {
    const otp = ref('')
    const error = ref('')

    const verify2FA = async () => {
      try {
        const response = await axios.post('/auth/verify-2fa', {
          username: localStorage.getItem('username'), // Ensure this is dynamically set to the current username
          otp: otp.value,
        })
        const accessToken = response.data.access_token
        localStorage.setItem('accessToken', accessToken) // Save token
        emit('verified') // Indicate successful verification
      } catch (err) {
        if (axios.isAxiosError(err)) {
          const status = err.response?.status
          if (status === 401) {
            error.value = 'Invalid 2FA code.'
          } else if (status === 404) {
            error.value = '2FA not enabled for this user.'
          } else {
            error.value = 'An unexpected error occurred.'
          }
        }
      }
    }

    return {
      otp,
      error,
      verify2FA,
    }
  },
})
</script>
