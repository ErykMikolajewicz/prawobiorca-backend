<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/api/accounts'
import { ElMessage } from 'element-plus'
import { getApiErrorMessage } from '@/utils/error'

const router = useRouter()

const form = reactive({
  username: '',
  password: '',
})

const errorMessage = ref('')
const isLoading = ref(false)

const onSubmit = async () => {
  if (!form.username || !form.password) {
    errorMessage.value = 'Wypełnij wszystkie pola.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    await register(form.username, form.password)

    ElMessage({
      message: 'Rejestracja przebiegła pomyślnie. Możesz się teraz zalogować.',
      type: 'success',
    })

    await router.push('/auth/login')
  } catch (error: unknown) {
    errorMessage.value = getApiErrorMessage(error, {
      conflictMessage: 'Nazwa użytkownika jest już zajęta.',
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <el-form :model="form" @keyup.enter="onSubmit" label-position="top">
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-3"
      :closable="false"
    />

    <el-form-item label="Nazwa użytkownika:" prop="username">
      <el-input v-model="form.username" id="username" required />
    </el-form-item>

    <el-form-item label="Hasło:" prop="password">
      <el-input v-model="form.password" type="password" id="password" show-password required />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" :loading="isLoading" @click="onSubmit"> Zarejestruj </el-button>
    </el-form-item>
  </el-form>
</template>
