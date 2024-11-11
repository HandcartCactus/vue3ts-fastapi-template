<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div class="input">
        <label for="username" class="label">Username:</label>
        <input id="username" v-model="username" aria-label="Username" required />
      </div>
      <div class="input">
        <label for="password" class="label">Password:</label>
        <input :type="showPassword ? 'text' : 'password'" v-model="password" id="password" required
          aria-label="Password" />
        <button type="button" @click="togglePassword">Show Password</button>
      </div>
      <button type="submit" class="button">Login</button>
      <p v-if="error" class="feedback">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { AuthError, OtpChallenge, Token, loginUser } from  '@/services/authService';
import { useAuthStore } from '@/stores/authStore';

export default defineComponent({
  name: 'LoginComponent',
  emits: ['loggedIn'],
  setup(_, { emit }) {
    const authStore = useAuthStore();

    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const error = ref('')

    const login = async () => {
      try {
        let requires_2fa = false;
        const tokenOrChallenge:Token|OtpChallenge = await loginUser(username.value,  password.value);
        authStore.username = username.value;
        if (tokenOrChallenge instanceof OtpChallenge){
          requires_2fa = true;
        } else {
          authStore.token = (tokenOrChallenge as Token);
        }
        emit('loggedIn', requires_2fa) // Inform whether 2FA is required
      } catch (err) {
        if (err instanceof AuthError) {
          error.value = err.message;
        } else {
          error.value = 'An unexpected error occurred.';
        }
      }
    }

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    return {
      username,
      password,
      showPassword,
      error,
      login,
      togglePassword,
    }
  },
})
</script>
