<template>
  <div id="app">
    <div class="card text-center">
      <div class="card-header">
        <h2 class="card-title">USER-LOGIN</h2>
      </div>

      <div class="card-body">
        <div class="container">
          <form>
            <label>Email:</label>
            <input
              type="text"
              name="email"
              placeholder="Email"
              v-model="formData.email"
              required
            /><br /><br />

            <label>Password:</label>
            <input
              type="password"
              name="password"
              placeholder="Password"
              v-model="formData.password"
              required
            /><br /><br />

            <button
              type="button"
              class="btn btn-dark"
              @click.prevent="loginUser"
            >
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
  name: "UserLogin",
  data() {
    return {
      formData: {
        email: "",
        password: "",
      },
    };
  },
  methods: {
    async loginUser() {
      try {
        const res = await fetch(
          "http://localhost:5000/login?include_auth_token",
          {
            method: "POST",
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
          this.$router.push(`/user_dashboard/${this.formData.email}`);
        } else {
          alert("Wrong Password or Email");
        }
      } catch (error) {
        console.error(error);
        console.log("An error occurred while logging in");
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
