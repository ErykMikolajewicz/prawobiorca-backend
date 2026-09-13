<script setup lang="ts">
import CaseCard from '@/components/molecules/CaseCard.vue'
import CaseCreationCard from '@/components/molecules/CaseCreationCard.vue'

type Props = {
  cases: Array<{
    id: string
    name: string
  }>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'case-deleted', caseId: string): void
  (e: 'case-created', newCase: { id: string; name: string }): void
}>()
</script>

<template>
  <div class="user-cases-container">
    <h2 class="section-title">Moje sprawy</h2>

    <div class="cases-grid">
      <CaseCard
        v-for="(userCase, index) in props.cases"
        :key="userCase.id"
        :userCase="userCase"
        :index="index + 1"
        @deleted="(id) => emit('case-deleted', id)"
      />

      <CaseCreationCard @case-created="(newCase) => emit('case-created', newCase)" />
    </div>
  </div>
</template>

<style scoped>
.user-cases-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding-left: 12px;
  border-left: 4px solid var(--el-color-primary);
}

.cases-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
}
</style>
