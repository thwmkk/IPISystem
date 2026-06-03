<template>
  <div class="login-page">
    <!-- Left side — branding -->
    <div class="login-brand">
      <div class="brand-content">
        <div class="brand-logo">
          <el-icon :size="32" color="#fff"><TrendCharts /></el-icon>
        </div>
        <h1 class="brand-title">IPI System</h1>
        <p class="brand-desc">
          Информационная система оценки индивидуальных<br />
          показателей эффективности научных сотрудников
        </p>
      </div>
    </div>

    <!-- Right side — form -->
    <div class="login-form-side">
      <div class="login-form-wrapper">
        <h2 class="form-title">Авторизация</h2>
        <p class="form-subtitle">Введите учётные данные для входа в систему</p>

        <el-alert
          v-if="loginError"
          :title="loginError"
          type="error"
          show-icon
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-form
          :model="form"
          :rules="rules"
          ref="formRef"
          @submit.prevent="handleLogin"
          class="form"
        >
          <el-form-item prop="email">
            <label class="field-label">Email</label>
            <el-input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              size="large"
              :prefix-icon="Message"
            />
          </el-form-item>

          <el-form-item prop="password">
            <label class="field-label">Пароль</label>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="Введите пароль"
              size="large"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>

          <el-button
            type="primary"
            size="large"
            class="login-btn"
            native-type="submit"
            :loading="loading"
          >
            Войти
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";
import {
  TrendCharts,
  Message,
  Lock,
} from "@element-plus/icons-vue";

const router = useRouter();
const auth = useAuthStore();
const formRef = ref();
const loading = ref(false);

const form = reactive({
  email: "",
  password: "",
});

const rules = {
  email: [{ required: true, message: "Введите email", trigger: "blur" }],
  password: [{ required: true, message: "Введите пароль", trigger: "blur" }],
};

const loginError = ref("");

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;
  loginError.value = "";
  try {
    await auth.login(form.email, form.password);
    router.push("/dashboard");
  } catch (err: any) {
    loginError.value = err.response?.data?.detail || "Ошибка входа";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Left — branding */
.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-brand::before {
  content: "";
  position: absolute;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15), transparent 70%);
  top: -100px;
  right: -100px;
}

.login-brand::after {
  content: "";
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1), transparent 70%);
  bottom: -80px;
  left: -80px;
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 400px;
  padding: 40px;
}

.brand-logo {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -1px;
  margin-bottom: 12px;
}

.brand-desc {
  font-size: 16px;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 32px;
}

.brand-org {
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.5;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Right — form */
.login-form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
}

.login-form-wrapper {
  width: 100%;
  max-width: 400px;
  padding: 40px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 40px;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.form .el-form-item {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 48px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  border-radius: var(--radius) !important;
  margin-top: 8px;
}
</style>
