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
        <h4>EDIT YOUR THEATER DETAILS!</h4>
      </div>

      <div class="card-body">
        <div class="container">
          <form enctype="multipart/form-data">
            <label style="margin-left: 100px">Theater Image : </label>
            <input
              type="file"
              name="theater_pic"
              placeholder="theater_pic"
              style="height: 40px"
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
            <button class="btn btn-dark" @click.prevent="editTheater">
              Update Theater
            </button>
          </form>
        </div>
      </div>
      <div v-if="theaterEdited" class="alert alert-success">
        Theater Edited successfully!
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
  name: "EditTheater",
  data() {
    return {
      theaterId: this.theaterId,
      formData: {
        theater_name: "",
        theater_pic: null,
        theater_address: "",
        theater_capacity: 0,
      },
      theaterEdited: false,
      error: "",
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
  },
  created() {
    this.theaterId = this.$route.params.theaterId;
    this.loadTheater();
  },
  methods: {
    async loadTheater() {
      const theaterId = this.$route.params.theater_id;
      const res = await fetch(
        `http://localhost:5000/api/theater_details/${theaterId}`,
        {
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );
      const data = await res.json();
      if (res.ok) {
        console.log(data);
        this.formData.theater_capacity = data.theater_capacity;
        this.formData.theater_address = data.theater_address;
        this.formData.theater_name = data.theater_name;
      } else if (res.status == 401) {
        this.error = "you are not authorized to acccess this resource";
        alert(this.error);
        this.$router.push("/");
      } else {
        alert(res.message);
      }
    },
    onFilechange(event) {
      this.formData.theater_pic = event.target.files[0];
    },
    async editTheater() {
      const formdata = new FormData();
      formdata.append("theater_pic", this.formData.theater_pic);
      formdata.append("theater_capacity", this.formData.theater_capacity);
      formdata.append("theater_address", this.formData.theater_address);
      formdata.append("theater_name", this.formData.theater_name);

      const theaterId = this.$route.params.theater_id;
      const res = await fetch(
        `http://localhost:5000/api/theaters/${theaterId}`,
        {
          method: "PUT",
          body: formdata,
          headers: {
            Authorization: "Bearer " + localStorage.getItem("auth_token"),
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        this.theaterEdited = true;
        const data = await res.json();
        console.log(data);
        this.$router.push(`/admin_dashboard/${this.currentUserEmail}`);
      } else if (res.status == 401) {
        this.error = "you are not authorized to acccess this resource";
        alert(this.error);
        this.$router.push("/");
      } else {
        console.log("Something went wrong");
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
