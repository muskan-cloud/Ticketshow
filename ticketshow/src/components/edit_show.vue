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
        <h6>EDIT SHOW DETAILS!</h6>
      </div>

      <div class="card-body">
        <div class="container">
          <form enctype="multipart/form-data">
            <label style="margin-left: 100px">Show Image : </label>
            <input
              type="file"
              name="show_pic"
              placeholder="show_pic"
              v-on:change="onFilechange"
            /><br />
            <label>Show Name : </label>
            <input
              name="show_name"
              placeholder="show_name"
              style="height: 40px"
              v-model="formData.show_name"
              required
            /><br />
            <label>Show Description : </label>
            <input
              name="show_description"
              placeholder="show_description"
              style="height: 40px"
              v-model="formData.show_description"
              required
            /><br />
            <label>Show Timing : </label>
            <input
              type="datetime-local"
              name="show_timing"
              placeholder="show_timing"
              style="height: 40px"
              min="0"
              v-model="formData.show_timing"
              required
            /><br />
            <label>Show Duration (HH:MM:SS): </label>
            <input
              name="show_duration_hours"
              type="number"
              placeholder="hours"
              style="height: 40px"
              v-model="formData.show_duration_hours"
              min="0"
              required
            />
            <input
              name="show_duration_minutes"
              type="number"
              placeholder="minutes"
              style="height: 40px"
              v-model="formData.show_duration_minutes"
              min="0"
              max="59"
              required
            />
            <input
              name="show_duration_seconds"
              type="number"
              placeholder="seconds"
              style="height: 40px"
              v-model="formData.show_duration_seconds"
              min="0"
              max="59"
              required
            />
            <br />
            <label>Show Trailer: </label>
            <input
              name="show_trailer"
              placeholder="show_trailer"
              style="height: 40px"
              v-model="formData.show_trailer"
            /><br />
            <label>Show Price : </label>
            <input
              type="number"
              name="show_price"
              placeholder="show_price"
              style="height: 40px"
              min="0"
              v-model="formData.show_price"
              required
            /><br /><br />
            <button class="btn btn-dark" @click.prevent="editshow">
              Update show
            </button>
          </form>
        </div>
      </div>
      <div v-if="showEdited" class="alert alert-success">
        Show Edited successfully!
      </div>
      <div class="card-footer text-body-secondary">
        <router-link
          :to="{
            name: 'theater_shows',
            params: { theater_id: this.theater_id },
          }"
          class="btn btn-dark"
          >Back</router-link
        >
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-end">
        <router-link
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 80%"
          >Back to your Dashboard</router-link
        >
        <a
          href="/"
          class="btn btn-dark"
          @click.prevent="logout"
          style="margin-right: 10px"
          >Logout</a
        >
      </div>
    </footer>
  </div>
</template>

<script>
import { logout } from "../app.js";

export default {
  name: "EditShow",
  data() {
    return {
      theater_id: 0,
      show_id: 0,
      formData: {
        showid: 0,
        show_name: "",
        show_pic: null,
        show_description: "",
        show_price: 0,
        show_timing: null,
        show_trailer: null,
        show_duration_hours: 0,
        show_duration_minutes: 0,
        show_duration_seconds: 0,
      },
      showEdited: false,
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
  },
  created() {
    // Get the show ID from the URL parameter
    this.show_id = this.$route.params.show_id;
    // Load the show data
    this.loadShow();
  },
  methods: {
    async loadShow() {
      const showId = this.$route.params.show_id;
      const res = await fetch(`http://localhost:5000/api/show/${showId}`, {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      });
      if (res.ok) {
        const data = await res.json();
        console.log(data);
        this.theater_id = data.theater.theater_id;
        this.formData.showid = data.show_id;
        this.formData.show_name = data.show_name;
        this.formData.show_description = data.show_description;
        this.formData.show_trailer = data.show_trailer;
        this.formData.show_price = data.show_price;
        this.formData.show_timing = data.show_timing;
        const showDuration = data.show_duration;
        this.formData.show_duration_hours = Math.floor(showDuration / 3600);
        this.formData.show_duration_minutes = Math.floor(
          (showDuration % 3600) / 60
        );
        this.formData.show_duration_seconds = showDuration % 60;
      } else if (res.status == 401) {
        this.error = "you are not authorized to acccess this resource";
        alert(this.error);
        this.$router.push("/");
      } else {
        console.log("Something went wrong");
      }
    },
    onFilechange(event) {
      this.formData.show_pic = event.target.files[0];
    },
    async editshow() {
      const showDurationInSeconds =
        parseInt(this.formData.show_duration_hours) * 3600 +
        parseInt(this.formData.show_duration_minutes) * 60 +
        parseInt(this.formData.show_duration_seconds);

      const currentDateTime = new Date();
      const showDateTime = new Date(this.formData.show_timing);
      if (showDateTime.getTime() - currentDateTime.getTime() < 60 * 60 * 1000) {
        alert("Show timing must be at least one hour in the future.");
        return;
      }

      const theater_id = this.theater_id;
      // Fetch existing shows from the server
      const existingShowsResponse = await fetch(
        `http://localhost:5000/api/theaters/${theater_id}`,
        {
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );
      const existingShows = await existingShowsResponse.json();

      const newShowStartTime = new Date(this.formData.show_timing).getTime(); // Convert to milliseconds
      const newShowEndTime = newShowStartTime + showDurationInSeconds * 1000; // Convert duration to milliseconds

      const existingShowsWithoutCurrentShow = existingShows.filter(
        (existingShow) => existingShow.show_id !== this.formData.showid
      );
      console.log(existingShowsWithoutCurrentShow);
      for (const existingShow of existingShowsWithoutCurrentShow) {
        const existingShowStartTime = new Date(
          existingShow.show_timing
        ).getTime(); // Convert to milliseconds
        const existingShowEndTime =
          existingShowStartTime + existingShow.show_duration * 1000; // Convert duration to milliseconds

        if (
          (newShowStartTime >= existingShowStartTime &&
            newShowStartTime <= existingShowEndTime) ||
          (newShowEndTime >= existingShowStartTime &&
            newShowEndTime <= existingShowEndTime)
        ) {
          alert(
            "The show timing overlaps with an existing show in the same theater."
          );
          return;
        }
      }

      const formdata = new FormData();
      formdata.append("show_pic", this.formData.show_pic);
      formdata.append("show_price", this.formData.show_price);
      formdata.append("show_description", this.formData.show_description);
      formdata.append("show_trailer", this.formData.show_trailer);
      formdata.append("show_timing", this.formData.show_timing);
      formdata.append("show_name", this.formData.show_name);
      formdata.append("show_duration", showDurationInSeconds);

      const showId = this.$route.params.show_id;
      const res = await fetch(`http://localhost:5000/api/show/${showId}`, {
        method: "PUT",
        body: formdata,
        headers: {
          Authorization: "Bearer " + localStorage.getItem("auth_token"),
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      });

      if (res.ok) {
        this.showEdited = true;
        const data = await res.json();
        console.log(data);
        this.$router.push(`/theater/${this.theater_id}`);
      } else {
        console.log("Something went wrong");
      }
    },
    logout() {
      logout();
      this.$router.push("/");
    },
    getShowDurationInSeconds() {
      return (
        parseInt(this.formData.show_duration_hours) * 3600 +
        parseInt(this.formData.show_duration_minutes) * 60 +
        parseInt(this.formData.show_duration_seconds)
      );
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
