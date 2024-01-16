<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 32%">Search for Theaters or Shows! 🔎</h2>
      </div>
    </nav>
    <div class="card text-center search-card">
      <div class="card-header">
        <form @submit.prevent="search">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search for Theaters or Shows"
          />
          <button class="btn btn-dark" type="submit" style="margin-left: 10px">
            Search
          </button>
        </form>
      </div>

      <div class="card-body">
        <ul v-if="theaterResults.length">
          <h5 style="text-decoration: underline">Theaters</h5>
          <li v-for="theater in theaterResults" :key="theater.theater_id">
            <router-link
              :to="{
                name: 'theater_details',
                params: { theater_id: theater.theater_id },
              }"
              class="custom-link"
              >{{ theater.theater_name }}</router-link
            >
          </li>
        </ul>

        <ul v-if="showResults.length">
          <h5 style="text-decoration: underline">Shows</h5>
          <li v-for="show in showResults" :key="show.show_id">
            <router-link :to="getShowLink(show)" class="custom-link">{{
              show.show_name
            }}</router-link>
          </li>
        </ul>

        <p v-else-if="searched">No shows or theaters found.</p>
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
  name: "Search",
  data() {
    return {
      searchQuery: "",
      theaterResults: [],
      showResults: [],
      searched: false,
      error: "",
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUser() {
      return this.$store.state.currentUser;
    },
    isAdmin() {
      const currentUser = this.$store.state.currentUser;
      if (!currentUser) {
        return false;
      }

      const isAdmin = currentUser.roles.some((role) => role === "<Role 1>");
      return isAdmin;
    },
    isUser() {
      const currentUser = this.$store.state.currentUser;
      if (!currentUser) {
        return false;
      }
      const isUser = currentUser.roles.some((role) => role === "<Role 2>");
      return isUser;
    },
  },
  mounted() {
    if (!this.isAdmin && !this.isUser) {
      alert("please login to access this resource");
      this.$router.push("/");
    }
  },
  methods: {
    async search() {
      if (this.searchQuery.trim() === "") {
        return;
      }

      const res = await fetch(
        `http://localhost:5000/api/search?q=${this.searchQuery}`,
        {
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        const searchData = await res.json();
        this.searchResults = searchData;

        this.theaterResults = searchData.filter(
          (result) => result.theater_name !== undefined
        );
        this.showResults = searchData.filter(
          (result) => result.show_name !== undefined
        );
        this.searched =
          this.theaterResults.length === 0 && this.showResults.length === 0;
        console.log(this.theaterResults);
        console.log(this.showResults);
      } else if (res.status === 401) {
        this.success = false;
        this.error = "Authentication required.";
        alert(this.error);
        logout();
      } else {
        this.success = false;
        this.error = "Failed to perform search.";
        alert(this.error);
      }
    },
    getShowLink(show) {
      const currentUser = this.$store.state.currentUser;
      const isAdmin = currentUser.roles.some((role) => role === "<Role 1>");

      return {
        name: isAdmin ? "gotoshow" : "gotoshowforuser",
        params: { show_id: show.show_id },
      };
    },
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.search-card {
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
