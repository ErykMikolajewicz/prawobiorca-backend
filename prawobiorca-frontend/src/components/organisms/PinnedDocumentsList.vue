<script setup lang="ts">
import PinnedDocument from '@/components/molecules/PinnedDocument.vue'
import type { DocumentData } from '@/types/api/documents.ts'

defineProps<{ documents: Array<DocumentData> }>()

const emit = defineEmits<{
  (e: 'unpin', id: string): void
}>()

const handleUnpin = (id: string) => {
  emit('unpin', id)
}
</script>

<template>
  <div v-if="documents.length > 0">
    <PinnedDocument
      v-for="document in documents"
      :key="document.id"
      :document="document"
      @unpin="handleUnpin"
    />
  </div>
  <div v-else>
    <el-empty description="Brak przypiętych artykułów do tej sprawy." />
  </div>
</template>
