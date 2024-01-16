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
        <h4>ADD YOUR SHOW DETAILS!</h4>
      </div>

      <div class="card-body scrollable-card">
        <div class="container">
          <form enctype="multipart/form-data">
            <label style="margin-left: 100px">Show Image : </label>
            <input
              type="file"
              name="show_pic"
              v-on:change="onFilechange"
            /><br /><br />
            <label>Show Name : </label>
            <input
              name="show_name"
              placeholder="show_name"
              style="height: 40px"
              v-model="formData.show_name"
              required
            /><br /><br />
            <label>Show Genre: </label>
            <input
              name="show_description"
              placeholder="show_genre"
              style="height: 40px"
              v-model="formData.show_description"
              required
            /><br /><br />
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
            <br /><br />
            <label>Show Trailer: </label>
            <input
              name="show_trailer"
              placeholder="show_trailer"
              style="height: 40px"
              v-model="formData.show_trailer"
            />

            <a href="https://www.google.com/search" target="_blank"
              >can search from here</a
            >
            <br /><br />
            <label>Select Theaters:</label>
            <div v-for="theater in theaters" :key="theater.theater_id">
              <input
                type="checkbox"
                :value="theater.theater_id"
                v-model="selectedTheaters"
              />
              <label style="margin-right: 10px">{{
                theater.theater_name
              }}</label>
              <label>Show Price :</label>
              <input
                type="number"
                name="show_price"
                placeholder="show_price"
                style="height: 40px"
                min="0"
                v-model="theater.price"
                required
              /><br /><br />
              <label>Show Timing :</label>
              <input
                name="show_timing"
                type="datetime-local"
                placeholder="show_timing"
                style="height: 40px"
                v-model="theater.show_timing"
                required
              /><br /><br />
            </div>
            <button class="btn btn-dark" @click.prevent="addshow">
              Add Show
            </button>
          </form>
        </div>
      </div>
      <div v-if="showadded" class="alert alert-success">
        Show Added successfully!
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
  name: "AddShow",
  data() {
    return {
      formData: {
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
      showadded: false,
      theaters: [],
      selectedTheaters: [],
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
  async mounted() {
    const currentUserEmail = this.$store.state.currentUserEmail;
    const res = await fetch(
      `http://localhost:5000/api/admin_dashboard/${currentUserEmail}`,
      {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );
    if (res.ok) {
      const theaters = await res.json();
      this.theaters = theaters;
      this.theaters = theaters.map((theater) => ({
        ...theater,
        price: 0,
        show_timing: null,
      }));
      console.log(theaters);
    } else if (res.status == 403) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      console.error("Error fetching theaters:");
    }
  },
  methods: {
    onFilechange(event) {
      console.log(event);
      this.formData.show_pic = event.target.files[0];
    },
    async fetchTheaterShows(theaterId) {
      const response = await fetch(
        `http://localhost:5000/api/theaters/${theaterId}`,
        {
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );
      if (response.ok) {
        const theaterShows = await response.json();
        console.log("Theater Shows:", theaterShows); // Add this line
        return theaterShows;
      } else if (response.status == 401) {
        this.error = "you are not authorized to access this resource";
        alert(this.error);
        this.$router.push("/");
      } else {
        console.error("Error fetching theater shows:", theaterId);
        return [];
      }
    },

    checkShowTimingClash(existingShows, theaterShowTiming) {
      console.log("Checking clashes..");
      const newShowStartTime = new Date(theaterShowTiming);
      console.log("New Show Start Time:", newShowStartTime);

      const showDurationInSeconds =
        parseInt(this.formData.show_duration_hours) * 3600 +
        parseInt(this.formData.show_duration_minutes) * 60 +
        parseInt(this.formData.show_duration_seconds);
      const newShowEndTime = new Date(
        newShowStartTime.getTime() + showDurationInSeconds * 1000
      );
      console.log("New Show End Time:", newShowEndTime);

      console.log("Existing Shows:", existingShows);

      for (const existingShow of existingShows) {
        const existingShowStartTime = new Date(existingShow.show_timing);
        console.log("Existing Show Start Time:", existingShowStartTime);
        const showDurationInSeconds = existingShow.show_duration;
        const existingShowEndTime = new Date(
          existingShowStartTime.getTime() + showDurationInSeconds * 1000
        );

        console.log("Existing Show End Time:", existingShowEndTime);

        // Check if the new show overlaps with the existing show for the current theater
        if (
          (newShowStartTime >= existingShowStartTime &&
            newShowStartTime <= existingShowEndTime) ||
          (newShowEndTime >= existingShowStartTime &&
            newShowEndTime <= existingShowEndTime) ||
          (newShowStartTime <= existingShowStartTime &&
            newShowEndTime >= existingShowEndTime)
        ) {
          console.log(
            "Clash found with show in theater: " +
              existingShow.theater.theater_name
          );
          return existingShow.theater.theater_name;
        }
      }

      console.log("No clashes found");
      return null;
    },
    async addshow() {
      const currentDateTime = new Date();

      for (const theaterId of this.selectedTheaters) {
        const theater = this.theaters.find((t) => t.theater_id === theaterId);
        const theaterPrice = theater.price;
        const theaterShowTiming = theater.show_timing;

        // Checking if the show timing is at least one hour in the future
        const showDateTime = new Date(theaterShowTiming);
        if (
          showDateTime.getTime() - currentDateTime.getTime() <
          60 * 60 * 1000
        ) {
          alert("Show timing must be at least one hour in the future.");
          return;
        }

        const theaterShows = await this.fetchTheaterShows(theaterId);
        const clashTheaterName = this.checkShowTimingClash(
          theaterShows,
          theaterShowTiming
        );

        if (clashTheaterName) {
          alert(
            `The show timing overlaps with an existing show in theater: ${clashTheaterName}.`
          );
          return;
        }

        const formdata = new FormData();
        formdata.append("show_pic", this.formData.show_pic);
        formdata.append("show_name", this.formData.show_name);
        formdata.append("show_description", this.formData.show_description);
        formdata.append("show_price", theaterPrice);
        formdata.append("show_trailer", this.formData.show_trailer);
        formdata.append("show_timing", theaterShowTiming);

        const showDurationInSeconds =
          parseInt(this.formData.show_duration_hours) * 3600 +
          parseInt(this.formData.show_duration_minutes) * 60 +
          parseInt(this.formData.show_duration_seconds);

        formdata.append("show_duration", showDurationInSeconds);

        const res = await fetch(
          `http://localhost:5000/api/${this.currentUserId}/${theaterId}/theater/add_show`,
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
          this.showadded = true;
          const data = await res.json();
          console.log(data);
          this.$router.push(`/admin_dashboard/${this.currentUserEmail}`);
        } else {
          console.log("Something went wrong");
        }
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
  max-height: fit-content;
  margin: 0 auto;
  overflow: hidden;
}
</style>
