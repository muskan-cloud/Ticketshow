<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
      </div>
    </nav>
    <div class="card text-center">
      <div class="card-header">
        <h4>ADD YOUR THEATER DETAILS!</h4>
      </div>

      <div class="card-body">
        <form enctype="multipart/form-data">
          <label style="margin-left: 100px">Theater Image : </label>
          <input
            type="file"
            name="theater_pic"
            v-on:change="onFilechange"
          /><br /><br />
          <label> Theater Name : </label>
          <input
            name="theater_name"
            placeholder="theater_name"
            style="height: 40px"
            v-model="formData.theater_name"
            required
          /><br /><br />
          <label>Theater Address :</label>
          <input
            name="theater_address"
            placeholder="theater_address"
            style="height: 40px"
            v-model="formData.theater_address"
            required
          /><br /><br />
          <label>Theater Capacity :</label>
          <input
            type="number"
            name="theater_capacity"
            placeholder="theater_capacity"
            style="height: 40px"
            min="0"
            v-model="formData.theater_capacity"
            required
          /><br /><br />
          <button class="btn btn-dark" @click.prevent="addTheater">
            Add Theater
          </button>
        </form>
      </div>
      <div v-if="theateradded" class="alert alert-success">
        Theater Added successfully!
      </div>
      <div class="card-footer text-body-secondary">
        <router-link
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          >Back to your Dashboard</router-link
        >
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-end">
        <a
          href="/"
          class="btn btn-dark"
          style="margin-right: 10px"
          @click.prevent="logout"
          >Logout</a
        >
      </div>
    </footer>
  </div>
</template>

<script>
import { logout } from "../app.js";

export default {
  name: "AddTheater",
  data() {
    return {
      formData: {
        theater_name: "",
        theater_pic: null,
        theater_address: "",
        theater_capacity: 0,
      },
      theateradded: false,
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserId() {
      return this.$store.state.currentUserId;
    },
  },
  methods: {
    onFilechange(event) {
      console.log(event);
      this.formData.theater_pic = event.target.files[0];
    },
    async addTheater() {
      if (!this.currentUserId) {
        alert("you need to login or signup first");
        this.$router.push("/");
        return;
      }
      const formdata = new FormData();
      formdata.append("theater_pic", this.formData.theater_pic);
      formdata.append("theater_name", this.formData.theater_name);
      formdata.append("theater_address", this.formData.theater_address);
      formdata.append("theater_capacity", this.formData.theater_capacity);
      const res = await fetch(
        `http://localhost:5000/api/${this.currentUserId}/add_theater`,
        {
          method: "POST",
          body: formdata,
          headers: {
            Authorization: "Bearer " + localStorage.getItem("auth_token"),
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        this.theateradded = true;
        const data = await res.json();
        console.log(data);
        this.$router.push(`/admin_dashboard/${this.currentUserEmail}`);
      } else if (res.status == 401) {
        alert("not authorized");
      } else {
        this.$router.push("/");
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
