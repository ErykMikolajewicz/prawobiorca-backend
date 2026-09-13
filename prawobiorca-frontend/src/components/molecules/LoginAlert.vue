<script setup lang="ts">
import { computed } from 'vue'

type Props = {
  message: string
  type: 'info' | 'error'
}

const props = defineProps<Props>()

const title = computed(() => {
  return props.type === 'info' ? 'Info' : 'Błąd'
})
</script>

<template>
  <el-alert
    v-if="message"
    :title="title"
    :type="type"
    :description="message"
    :show-icon="true"
    :closable="false"
  />
</template>
