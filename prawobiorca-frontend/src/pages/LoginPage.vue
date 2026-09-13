<script setup lang="ts">
import LoginForm from '@/components/organisms/LoginForm.vue'
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <h2 class="title">Logowanie</h2>

      <LoginForm />

      <p class="register-link">
        <router-link to="/accounts/register" custom v-slot="{ navigate, href }">
          <el-link :href="href" @click="navigate" type="primary"> Załóż konto </el-link>
        </router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  box-sizing: border-box;
}

.title {
  text-align: center;
  margin-bottom: 24px;
}

.register-link {
  text-align: center;
  margin-top: 16px;
}
</style>
