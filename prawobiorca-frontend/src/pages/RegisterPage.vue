<script setup lang="ts">
import RegisterForm from '@/components/organisms/RegisterForm.vue'
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <h2 class="title">Rejestracja</h2>

      <RegisterForm />

      <p class="login-link">
        <router-link to="/auth/login" custom v-slot="{ navigate, href }">
          <el-link :href="href" @click="navigate" type="primary">
            Masz już konto? Zaloguj się
          </el-link>
        </router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  box-sizing: border-box;
}

.title {
  text-align: center;
  margin-bottom: 24px;
}

.login-link {
  text-align: center;
  margin-top: 16px;
}
</style>
