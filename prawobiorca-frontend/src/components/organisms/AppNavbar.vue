<script setup lang="ts">
import AuthControls from '@/components/molecules/AuthControls.vue'
import DarkModeToggle from '@/components/molecules/DarkModeToggle.vue'
</script>

<template>
  <el-header class="app-navbar">
    <div class="logo">PRAWOBIORCA</div>

    <div class="nav-controls">
      <DarkModeToggle />
      <AuthControls />
    </div>
  </el-header>
</template>

<style scoped>
.app-navbar {
  background-color: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--app-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo {
  color: var(--el-color-primary);
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 1px;
}
</style>
