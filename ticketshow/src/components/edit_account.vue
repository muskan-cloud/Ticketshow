<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%"></h2>
        <form class="d-flex" @submit.prevent="search">
          <router-link to="/search" class="btn btn-dark">Search 🔎</router-link>
        </form>
      </div>
    </nav>
    <div class="card text-center">
      <div class="card-header">
        <h2 class="card-title">Update Your Details</h2>
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
            <label>Username:</label>
            <input
              type="text"
              name="username"
              placeholder="Username"
              v-model="formData.username"
              required
            /><br /><br />

            <label>New Password:</label>
            <input
              type="password"
              name="new_password"
              placeholder="New Password"
              v-model="formData.password"
            /><br /><br />

            <label>Confirm New Password:</label>
            <input
              type="password"
              name="confirm_new_password"
              placeholder="Confirm New Password"
              v-model="formData.confirm_password"
            /><br /><br />

            <button
              type="button"
              class="btn btn-dark"
              @click.prevent="editUser"
            >
              Update Details
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { logout } from "../app.js";

export default {
  name: "UserUpdate",
  data() {
    return {
      formData: {
        email: "",
        username: "",
        password: "",
        confirm_password: "",
      },
      UserEdited: false,
      error: "",
    };
  },
  computed: {
    currentUserId() {
      return this.$store.state.currentUserId;
    },
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserRoles() {
      return this.$store.state.currentUserRoles;
    },
    currentUserName() {
      return this.$store.state.currentUserName;
    },
  },
  created() {
    this.loadUser();
  },
  methods: {
    async loadUser() {
      const email = this.$store.state.currentUserEmail;
      const res = await fetch(`http://localhost:5000/api/users/${email}`, {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      });
      if (res.ok) {
        const data = await res.json();
        console.log(data);
        this.formData.email = data.email;
        this.formData.username = data.username;
      } else if (res.status == 401) {
        this.error = "you are not authorized to acccess this resource";
        alert(this.error);
        this.$router.push("/");
      } else {
        console.log("Something went wrong");
      }
    },
    async editUser() {
      const formdata = new FormData();
      if (this.formData.password !== this.formData.confirm_password) {
        alert("Passwords do not match");
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

      formdata.append("email", this.formData.email);
      formdata.append("username", this.formData.username);

      if (
        this.formData.password &&
        this.formData.password === this.formData.confirm_password
      ) {
        formdata.append("password", this.formData.password);
        formdata.append("confirm_password", this.formData.confirm_password);
      }

      const email = this.$store.state.currentUserEmail;

      const res = await fetch(`http://localhost:5000/api/users/${email}`, {
        method: "PUT",
        body: formdata,
        headers: {
          Authorization: "Bearer " + localStorage.getItem("auth_token"),
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      });
      const data = await res.json();
      if (res.ok) {
        this.UserEdited = true;
        console.log(data);
        this.$store.state.currentUserEmail = this.formData.email;
        this.$store.state.currentUsername = this.formData.username;
        const email_new = this.$store.state.currentUserEmail;
        this.$router.push(`/account/${email_new}`);
      } else {
        const error = data.response.error;
        alert(error);
      }
    },
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.card {
  max-width: 60%;
  margin: 0 auto;
  overflow: hidden;
}
</style>
