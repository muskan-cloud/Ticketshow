<template>
  <div id="app">
    <div class="card text-center">
      <div class="card-header">
        <h2 class="card-title">ADMIN-SIGNUP</h2>
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
            <label>Username : </label>
            <input
              type="text"
              name="username"
              placeholder="username"
              v-model="formData.username"
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
            <label>Confirm password : </label>
            <input
              type="password"
              name="confirm_password"
              placeholder="Confirm Password"
              v-model="formData.confirm_password"
              required
            /><br /><br />
            <button
              type="button"
              class="btn btn-dark"
              @click.prevent="signupAdmin"
            >
              Sign up
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
  name: "AdminSignup",
  data() {
    return {
      formData: {
        username: "",
        email: "",
        password: "",
        confirm_password: "",
        general_signup: "",
      },
    };
  },
  methods: {
    async signupAdmin() {
      if (this.formData.password !== this.formData.confirm_password) {
        console.log("Passwords do not match");
        return;
      }
      if (this.formData.password.length < 6) {
        alert("Password should be at least 6 characters long");
        return;
      }

      if (!/\d/.test(this.formData.password)) {
        alert("Password must contain at least one number");
        return;
      }

      const askGeneralSignup = confirm("Do you want to have general signup?");
      this.formData.general_signup = askGeneralSignup;

      const res = await fetch("http://localhost:5000/api/admin_signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(this.formData),
      });
      const data = await res.json();
      if (res.ok) {
        alert(data.message);
        this.$router.push("/");
      } else {
        this.error = data.message;
        alert(this.error);
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
