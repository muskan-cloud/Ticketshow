<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">Theater Details</h2>
        <form class="d-flex" role="search">
          <router-link to="/search" class="btn btn-dark">Search</router-link>
        </form>
      </div>
    </nav>
    <div class="container">
      <div class="row">
        <div class="col-md-6" style="margin-top: 15%">
          <div class="card">
            <img
              :src="'data:image/*;charset=utf-8;base64,' + theater.theater_pic"
              class="theater-image"
              alt="Theater Image"
            />
          </div>
        </div>
        <div class="col-md-6">
          <div class="card text-center mt-2" style="margin-left: 5px">
            <div class="card-header py-2">
              <h3>{{ theater.theater_name }} Details</h3>
            </div>
            <div class="card-body pb-0 scrollable-card">
              <p>Theater Address: {{ theater.theater_address }}</p>
              <p>Capacity: {{ theater.theater_capacity }}</p>
              <ul v-if="shows.length" class="mt-2 mb-0">
                <p>Current Running Shows here!</p>
                <li v-for="show in shows" :key="show.show_id">
                  <router-link
                    v-if="isUser"
                    class="custom-link"
                    :to="'/gotoshowforuser/' + show.show_id"
                    >{{ show.show_name }}</router-link
                  >
                  <router-link
                    v-else
                    class="custom-link"
                    :to="'/gotoshow/' + show.show_id"
                    >{{ show.show_name }}</router-link
                  >
                </li>
              </ul>
            </div>
            <div class="card-footer text-body-secondary">
              <button
                v-if="isAdmin && theater.ut_id === currentUserId"
                class="btn btn-dark"
                @click="exportShowsCSV"
              >
                Export Theater Show Details [csv]
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-end">
        <router-link
          v-if="isAdmin && !isUser"
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 1228px"
          >Back to Your Dashboard</router-link
        >
        <router-link
          v-if="isUser && !isAdmin"
          :to="'/user_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 1228px"
          >Back to Your Dashboard</router-link
        >
        <router-link
          v-if="isAdmin && isUser"
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 10px"
          >Back to Admin Dashboard</router-link
        >
        <router-link
          v-if="isAdmin && isUser"
          :to="'/user_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 1000px"
          >Back to User Dashboard</router-link
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
  name: "TheaterDetails",
  data() {
    return {
      theater: {
        ut_id: 0,
        theater_name: "",
        theater_capacity: null,
        theater_id: null,
        theater_address: null,
        theater_pic: null,
      },
      shows: [],
      success: true,
      error: "Something went wrong",
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserId() {
      return this.$store.state.currentUserId;
    },
    isAdmin() {
      return this.$store.state.currentUserRoles.includes("<Role 1>");
    },
    isUser() {
      return this.$store.state.currentUserRoles.includes("<Role 2>");
    },
  },
  async mounted() {
    const theater_id = this.$route.params.theater_id;
    const restheater = await fetch(
      `http://localhost:5000/api/theater_details/${theater_id}`,
      {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );
    const datatheater = await restheater.json();
    console.log(datatheater);
    if (restheater.ok) {
      this.theater = datatheater;
    } else if (restheater.status == 401) {
      this.success = false;
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      this.error = datatheater.message;
      alert(datatheater.message);
      this.$router.push("/");
      localStorage.clear();
    }

    const resshowboard = await fetch(
      `http://localhost:5000/api/theaters/${theater_id}`,
      {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );
    const datashows = await resshowboard.json();
    console.log(datashows);

    if (resshowboard.ok) {
      this.shows = datashows;
      console.log(this.shows);
    } else if (resshowboard.status == 401) {
      this.success = false;
      this.error = datashows.response.error;
    } else {
      this.success = false;
      this.error = datashows.message;
      alert(this.error);
    }
  },
  methods: {
    getShowLink(show) {
      const currentUser = this.$store.state.currentUser;
      const isAdmin = currentUser.roles.some((roles) => roles === "<Role 1>");

      return {
        name: isAdmin ? "gotoshow" : "gotoshowforuser",
        params: { show_id: show.show_id },
      };
    },

    async exportShowsCSV() {
      try {
        const theater_id = this.$route.params.theater_id;
        const response = await fetch(
          `http://localhost:5000/export_shows_csv/${theater_id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
            responseType: "blob", // set response type to blob
          }
        );
        if (response.ok) {
          const csvTheater = await response.blob(); // convert response to blob
          const csvUrl = URL.createObjectURL(csvTheater); // create URL for the blob
          const a = document.createElement("a");
          a.href = csvUrl;
          a.download = `${this.theater.theater_name}_data.csv`; // set desired filename for CSV file
          a.click(); // simulate click on anchor tag to trigger download
          alert("CSV export job started");
        } else {
          alert("Failed to start CSV export job");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to start CSV export job");
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
  width: 100%;
  height: auto;
  margin-bottom: 20px;
}
.scrollable-card {
  height: auto;
  overflow-y: auto;
}

.theater-image {
  width: 100%;
  height: auto;
}

.custom-link:link,
.custom-link:visited {
  color: black;
  background-color: transparent;
  text-decoration: none;
}
.custom-link:hover {
  color: blue;
  background-color: transparent;
  text-decoration: underline;
}
</style>
