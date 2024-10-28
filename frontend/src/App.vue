<template>
  <div>
    <RouterView />
    <!-- <div>
      <h2>Welcome to the App!</h2>
      <button @click="logout">Logout</button>
    </div> -->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'App',
  components: {},
  setup() {
    const authenticated = ref(false)

    const onAuthenticated = (status: boolean) => {
      authenticated.value = status
    }

    const logout = () => {
      localStorage.removeItem('accessToken')
      authenticated.value = false
    }

    return { authenticated, onAuthenticated, logout }
  },
})
</script>

<style scoped>
/* Add any global styles here */
</style>
