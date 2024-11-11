<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <div class="input">
        <label for="username" class="label">Username:</label>
        <input
          id="username"
          v-model="username"
          aria-label="Username"
          required
        />
      </div>
      <div class="input">
        <label for="password" class="label">Password:</label>
        <input
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          id="password"
          required
          aria-label="Password"
        />
        <button type="button" @click="togglePassword">Show Password</button>
      </div>
      <button type="submit" class="button">Register</button>
      <p v-if="error" class="feedback">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { AuthError, registerUser, Token } from '@/services/authService';

export default defineComponent({
  name: 'RegisterComponent',
  emits: ['registered'],
  setup(_, { emit }) {
    const authStore = useAuthStore();
    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const error = ref('')

    const register = async () => {
      try {
        const token: Token = await registerUser(username.value,password.value);
        authStore.token = token;
        authStore.username = username.value;
        emit('registered')
      } catch (err) {
        if (err instanceof AuthError) {
          error.value = err.message
         } else {
          throw  err
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
      register,
      togglePassword,
    }
  },
})
</script>
