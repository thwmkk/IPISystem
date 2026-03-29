import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: {
      name: "Иван Иванов",
    },
    role: "manager", // 👈 поменяй: employee / manager / admin
    isAuthenticated: true,
  }),

  actions: {
    logout() {
      this.isAuthenticated = false;
    },
  },
});