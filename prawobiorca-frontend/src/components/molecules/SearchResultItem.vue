<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  result: string
  score: number
  selectedCaseId?: string
}>()

const emit = defineEmits<{
  (e: 'add-to-case', payload: { documentContent: string }): void
}>()

const authStore = useAuthStore()
const { isUserLogged } = storeToRefs(authStore)

const handleAddToCase = () => {
  emit('add-to-case', { documentContent: props.result })
}
</script>

<template>
  <el-card shadow="hover">
    <div class="result-container">
      <label class="result-text">{{ result }}</label>
      <div class="score-column">
        <span class="score-label">Podobieństwo</span>
        <span class="score-value">{{ score.toFixed(3) }}</span>
      </div>
      <div class="actions">
        <el-tooltip
          v-if="isUserLogged"
          :disabled="!!selectedCaseId"
          content="Wybierz bieżącą sprawę, by dodać do niej wyszukany element."
          placement="top"
        >
          <span class="tooltip-wrapper">
            <el-button
              type="primary"
              size="small"
              :disabled="!selectedCaseId"
              @click="handleAddToCase"
            >
              Dodaj do sprawy
            </el-button>
          </span>
        </el-tooltip>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.result-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.result-text {
  flex: 1;
}

.score-column {
  flex-shrink: 0;
  min-width: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary, #909399);
}

.score-label {
  font-size: 0.75em;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 2px;
}

.score-value {
  font-size: 1.1em;
  font-weight: 500;
  color: var(--el-text-color-primary, #303133);
}

.actions {
  flex-shrink: 0;
}

.tooltip-wrapper {
  display: inline-block;
  cursor: not-allowed;
}
</style>
