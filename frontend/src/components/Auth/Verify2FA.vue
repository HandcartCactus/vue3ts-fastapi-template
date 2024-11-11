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
import { useAuthStore } from '@/stores/authStore'
import { verify2fa, Token, AuthError } from '@/services/authService';

export default defineComponent({
  name: 'Verify2FA',
  emits: ['verified'],
  setup(_, { emit }) {
    const otp = ref('')
    const error = ref('')

    const authStore = useAuthStore();


    const verify2FA = async () => {
      try {
        if (authStore.username == null) {
          throw new AuthError('Username not found')
        }
        const token:Token = await verify2fa(authStore.username, otp.value);
        authStore.token = token;
        emit('verified');
      } catch (err) {
        if (err instanceof AuthError) {
          error.value = err.message;
        } else {
          error.value = 'An unexpected error occurred.';
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
