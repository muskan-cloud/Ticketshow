<template>
  <div id="app">
    <div class="card text-center">
      <div class="card-header">
        <h2 class="card-title">ADMIN-LOGIN</h2>
      </div>
      <div class="card-body">
        <div class="container">
          <form>
            <label>Email : </label>
            <input
              type="text"
              name="email"
              placeholder="Email"
              v-model="formData.email"
              required
            /><br /><br />

            <label>Password : </label>
            <input
              type="password"
              name="password"
              placeholder="Password"
              v-model="formData.password"
              required
            /><br /><br />
            <button class="btn btn-dark" @click.prevent="loginAdmin">
              Login
            </button>
          </form>
        </div>
      </div>
      <div class="card-footer text-body-secondary" style="margin-top: 10px">
        <router-link to="/" class="btn btn-dark">BACK TO HOME PAGE</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminLogin",
  data() {
    return {
      formData: {
        email: "",
        password: "",
      },
    };
  },
  methods: {
    async loginAdmin() {
      const res = await fetch(
        "http://localhost:5000/login?include_auth_token",
        {
          method: "post",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(this.formData),
        }
      );

      if (res.ok) {
        const data = await res.json();
        console.log(data);
        localStorage.setItem(
          "auth-token",
          data.response.user.authentication_token
        );
        this.$router.push(`admin_dashboard/${this.formData.email}`);
      } else {
        alert("Wrong Password or Email");
      }
    },
  },
};
</script>

<style scoped>
.card {
  max-width: 70%;
  margin-bottom: 10px;
}
</style>
