<script setup lang="ts">
import type { DocumentData } from '@/types/api/documents.ts'

type Props = { document: DocumentData }
const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'unpin', id: string): void
}>()

const handleUnpin = () => {
  emit('unpin', props.document.id)
}
</script>

<template>
  <el-card shadow="hover">
    <template #header>
      <strong>Źródło:</strong>
      <em>{{ document.presentationName }}</em>
      <el-button type="danger" @click="handleUnpin">Odepnij</el-button>
    </template>
    <p>{{ document.content }}</p>
  </el-card>
</template>
