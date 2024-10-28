<template>
  <div>
    <div v-if="step === 'choose'">
      <button @click="step = 'register'">Sign Up</button>
      <button @click="step = 'login'">Log In</button>
    </div>
    <div v-else>
      <button @click="step = 'choose'">Back</button>
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
      'choose' | 'register' | 'login' | 'verify2fa' | 'enable2fa' | 'setup2fa'
    >('choose')

    const handleRegistrationSuccess = () => {
      alert('Registration successful! You can now log in.')
      step.value = 'login'
    }

    const handleLoginSuccess = (requires2FA: boolean) => {
      if (requires2FA) {
        step.value = 'verify2fa'
      } else {
        step.value = 'enable2fa'
      }
    }

    const handleVerified = () => {
      alert('You are logged in with 2FA!')
    }

    return {
      step,
      handleRegistrationSuccess,
      handleLoginSuccess,
      handleVerified,
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
