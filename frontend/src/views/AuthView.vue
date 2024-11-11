<template>
  <div>
    <div v-if="step === 'choose'">
      <button @click="step = 'register'">Sign Up</button>
      <button @click="step = 'login'">Log In</button>
    </div>
    <div v-else-if="step !=='authenticated'">
      <button @click="step = 'choose'">Back</button>
    </div>
    <div v-else>
      <button @click="handleAccount()">Account</button>
      <button @click="logOut()">Log Out</button>
    </div>
    <RegisterComponent
      v-if="step === 'register'"
      @registered="handleRegistrationSuccess"
    />
    <LoginComponent v-if="step === 'login'" @loggedIn="handleLoginSuccess" />
    <Verify2FA v-if="step === 'verify2fa'" @verified="handleVerified" />
    <button v-if="step === 'enable2fa'" @click="step = 'setup2fa'">
      Enable 2FA
    </button>
    <Enable2FA v-if="step === 'setup2fa'" />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import RegisterComponent from '@/components/Auth/RegisterComponent.vue'
import LoginComponent from '@/components/Auth/LoginComponent.vue'
import Enable2FA from '@/components/Auth/Enable2FA.vue'
import Verify2FA from '@/components/Auth/Verify2FA.vue'
import { useAuthStore } from '@/stores/authStore'

export default defineComponent({
  name: 'AuthView',
  components: {
    RegisterComponent,
    LoginComponent,
    Enable2FA,
    Verify2FA,
  },
  setup() {
    const step = ref<
      'choose' | 'register' | 'login' | 'verify2fa' | 'enable2fa' | 'setup2fa' | 'authenticated'
    >('choose')

    const authStore = useAuthStore();

    const handleRegistrationSuccess = () => {
      step.value = 'login'
    }

    const handleLoginSuccess = (requires2FA: boolean) => {
      if (requires2FA) {
        step.value = 'verify2fa'
      } else {
        step.value = 'enable2fa'
      }
    }

    const handleAccount = () => {
      alert(`you are ${authStore.username}.`)
    }

    const handleVerified = () => {
      step.value = 'authenticated';
    }

    const logOut = () => {
      authStore.logout();
      step.value = 'choose';
    }

    return {
      step,
      handleRegistrationSuccess,
      handleLoginSuccess,
      handleVerified,
      handleAccount,
      logOut
    }
  },
})
</script>

<style scoped>
.input {
  display: flex;
  flex-direction: column;
  margin-bottom: 15px;
}

.label {
  font-size: 14px;
}

.feedback {
  font-size: 12px;
  color: red;
}

.button {
  padding: 10px;
  margin-top: 10px;
}
</style>
