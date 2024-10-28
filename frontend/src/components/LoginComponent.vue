<template>
    <div>
      <h2 v-if="!isAuthenticated">Sign Up</h2>
      <form v-if="!isAuthenticated" @submit.prevent="register">
        <input v-model="username" placeholder="Username" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit">Sign Up</button>
        <p v-if="registerError" class="error">{{ registerError }}</p>
      </form>
  
      <h2 v-if="!isAuthenticated">Login</h2>
      <form v-if="!isAuthenticated" @submit.prevent="login">
        <input v-model="username" placeholder="Username" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit">Login</button>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </form>
  
      <div v-if="isAuthenticated && !twoFAEnabled">
        <h2>Welcome, {{ username }}</h2>
        <button @click="enable2FA">Enable 2FA</button>
      </div>
  
      <div v-if="qrCode">
        <h3>Scan this QR Code with your Authenticator App</h3>
        <img :src="qrCode" alt="QR Code" />
        <form @submit.prevent="verify2FA">
          <input v-model="otp" placeholder="Enter OTP" required />
          <button type="submit">Verify 2FA</button>
        </form>
        <p v-if="twoFAError" class="error">{{ twoFAError }}</p>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  
  export default defineComponent({
    name: 'LoginComponent',
    emits: ['authenticated'],
    setup(_, { emit }) {
      const username = ref('');
      const password = ref('');
      const otp = ref('');
      const isAuthenticated = ref(false);
      const twoFAEnabled = ref(false);
      const qrCode = ref('');
      const registerError = ref('');
      const loginError = ref('');
      const twoFAError = ref('');
  
      const register = async () => {
        registerError.value = '';
        try {
          const response = await fetch('/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username.value, password: password.value }),
          });
  
          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            isAuthenticated.value = true;
            emit('authenticated', true);
          } else if (response.status === 409) {
            registerError.value = 'Username already taken. Please choose another.';
          } else {
            registerError.value = 'Registration failed. Please try again.';
          }
        } catch {
          registerError.value = 'Network error. Please try again later.';
        }
      };
  
      const login = async () => {
        loginError.value = '';
        try {
          const response = await fetch('/auth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username.value, password: password.value }),
          });
  
          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            isAuthenticated.value = true;
            emit('authenticated', true);
          } else {
            loginError.value = 'Invalid credentials. Please try again.';
          }
        } catch {
          loginError.value = 'Network error. Please try again later.';
        }
      };
  
      const enable2FA = async () => {
        try {
          const token = localStorage.getItem('accessToken');
          const response = await fetch('/auth/enable-2fa', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
  
          if (response.ok) {
            const data = await response.json();
            qrCode.value = data.qrCode;
            twoFAEnabled.value = true;
          }
        } catch (error) {
          console.error('Failed to enable 2FA:', error);
        }
      };
  
      const verify2FA = async () => {
        twoFAError.value = '';
        try {
          const token = localStorage.getItem('accessToken');
          const response = await fetch('/auth/verify-2fa', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username.value, otp: otp.value }),
          });
  
          if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access_token);
            qrCode.value = '';
            otp.value = '';
            isAuthenticated.value = true;
            twoFAEnabled.value = true;
          } else {
            twoFAError.value = 'Invalid OTP. Please try again.';
          }
        } catch {
          twoFAError.value = 'Network error. Please try again later.';
        }
      };
  
      return {
        username,
        password,
        otp,
        isAuthenticated,
        twoFAEnabled,
        qrCode,
        registerError,
        loginError,
        twoFAError,
        register,
        login,
        enable2FA,
        verify2FA,
      };
    },
  });
  </script>
  
  <style scoped>
  .error {
    color: red;
  }
  </style>  