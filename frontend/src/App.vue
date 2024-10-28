<template>
  <div>
    <LoginComponent v-if="!authenticated" @authenticated="onAuthenticated" />
    <div v-else>
      <h2>Welcome to the App!</h2>
      <button @click="logout">Logout</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import LoginComponent from '@/components/LoginComponent.vue';

export default defineComponent({
  name: 'App',
  components: {
    LoginComponent,
  },
  setup() {
    const authenticated = ref(false);

    const onAuthenticated = (status: boolean) => {
      authenticated.value = status;
    };

    const logout = () => {
      localStorage.removeItem('accessToken');
      authenticated.value = false;
    };

    return { authenticated, onAuthenticated, logout };
  },
});
</script>

<style scoped>
/* Add any global styles here */
</style>