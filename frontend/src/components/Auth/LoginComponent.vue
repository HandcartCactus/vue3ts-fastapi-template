<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
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
      <button type="submit" class="button">Login</button>
      <p v-if="error" class="feedback">{{ error }}</p>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'

export default defineComponent({
  name: 'LoginComponent',
  emits: ['loggedIn'],
  setup(_, { emit }) {
    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const error = ref('')

    const login = async () => {
      try {
        const response = await axios.post('/auth/token', {
          username: username.value,
          password: password.value,
          grant_type: 'password',
        })
        const { access_token, requires_2fa } = response.data
        if (!requires_2fa) {
          localStorage.setItem('accessToken', access_token) // Save token
        }
        localStorage.setItem('username', username.value)
        emit('loggedIn', requires_2fa) // Inform whether 2FA is required
      } catch (err) {
        if (axios.isAxiosError(err)) {
          const status = err.response?.status
          if (status === 401) {
            error.value = 'Incorrect username or password.'
          } else {
            error.value = 'An unexpected error occurred.'
          }
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
