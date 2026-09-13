<script setup lang="ts">
import { reactive } from 'vue'

import type { searchParams } from '@/types/api/search.ts'

const props = defineProps<{
  searchParams: searchParams
}>()

const emit = defineEmits<{
  (e: 'search', searchConfig: searchParams): void
}>()

const searchParams = reactive<searchParams>({
  ...props.searchParams,
  threshold: props.searchParams.threshold ?? 0.2,
})

function onSubmit() {
  if (searchParams.query.trim()) {
    emit('search', { ...searchParams })
  }
}
</script>

<template>
  <el-form @submit.prevent="onSubmit">
    <el-form-item label="Twoje zapytanie:">
      <el-input v-model="searchParams.query" placeholder="Wpisz treść..." clearable required />
    </el-form-item>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="Poziom istotności:">
          <div style="display: flex; align-items: center; gap: 15px; width: 100%">
            <el-slider
              v-model="searchParams.threshold"
              :min="-1"
              :max="1"
              :step="0.1"
              :show-tooltip="false"
              style="flex: 1"
            />
            <span
              style="
                color: var(--el-text-color-primary);
                min-width: 40px;
                text-align: center;
                font-weight: 500;
              "
            >
              {{ searchParams.threshold.toFixed(1) }}
            </span>
          </div>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Maksymalna liczba wyników:">
          <el-input-number
            v-model="searchParams.limit"
            :min="1"
            :step="1"
            placeholder="Brak limitu"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
    </el-row>
    <el-form-item>
      <el-button native-type="submit">Przeszukaj</el-button>
    </el-form-item>
  </el-form>
</template>
