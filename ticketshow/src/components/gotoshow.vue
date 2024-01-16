<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">Show Details</h2>
        <form class="d-flex" role="search">
          <router-link to="/search" class="btn btn-dark">Search 🔎</router-link>
        </form>
      </div>
    </nav>
    <div>
      <div class="card text-center">
        <div class="card-header">
          <h4>{{ show.show_name }}'s Details</h4>
        </div>
        <div class="card-body">
          <p>Show Date & Time 🗓️ : {{ formattedShowTiming }}</p>
          <p>Show Duration ⏱️: {{ showDuration }}</p>
          <p>Show genre : {{ show.show_description }}</p>
          <p>Show price : ₹ {{ show.show_price }}</p>
          <p v-if="show.show_trailer !== 'null'">
            <a v-bind:href="show.show_trailer" target="_blank" class="cus-link"
              >Watch Trailer</a
            >
          </p>
          <p v-else>
            No Trailer Added!
            <router-link
              v-if="show.theater.ut_id === currentUserId"
              :to="{
                name: 'edit_show',
                params: { show_id: show.show_id },
              }"
              class="btn btn-dark"
            >
              can update from here
            </router-link>
          </p>
          <p>Show Theater : {{ show.theater.theater_name }}</p>
          <p>Address : {{ show.theater.theater_address }}</p>
          <template v-if="show.show_rating > 0">
            <p>
              Show Rating:
              <span
                style="margin-right: 8px"
                v-for="(star, index) in Math.floor(show.show_rating)"
                :key="index"
              >
                <i class="bi bi-star-fill star"></i>
              </span>
              <template
                v-if="show.show_rating - Math.floor(show.show_rating) >= 0.5"
              >
                <i class="bi bi-star-half star"></i>
              </template>
              ({{ show.show_rating.toFixed(1) }} / 5)
            </p>
          </template>
          <template v-else> <p>No ratings yet</p> </template>
          <template v-if="hasTags"
            >Show Tags:
            <span
              v-for="tag in show.show_tags"
              :key="tag.id"
              class="tag"
              style="margin-right: 10px"
            >
              {{ tag.user_tag }}
            </span> </template
          ><template v-else><p>No Tags Yet</p></template>
        </div>
        <div class="card-footer text-body-secondary">
          <router-link
            :to="{
              name: 'theater_shows',
              params: { theater_id: show.theater.theater_id },
            }"
            class="btn btn-dark"
            style="margin-right: 10px"
            >See all shows at {{ show.theater.theater_name }}!</router-link
          >
          <router-link
            v-if="show.theater.ut_id === currentUserId"
            :to="{
              name: 'Prediction',
              params: { show_id: show.show_id },
            }"
            class="btn btn-dark"
            >Predict Popularity</router-link
          >
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
  name: "GoToShow",
  data() {
    return {
      show: {
        show_name: "",
        show_pic: null,
        show_description: "",
        show_price: 0,
        show_tags: [],
        show_timing: null,
        show_rating: 0,
        show_id: 0,
        show_trailer: 0,
        show_duration: 0,
        theater: {
          theater_name: "",
          theater_address: "",
          theater_id: 0,
          ut_id: 0,
        },
      },
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserUsername() {
      return this.$store.state.currentUsername;
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
    hasTags() {
      return this.show.show_tags && this.show.show_tags.length > 0;
    },
    showDuration() {
      const durationInSeconds = this.show.show_duration;
      const hours = Math.floor(durationInSeconds / 3600);
      const minutes = Math.floor((durationInSeconds % 3600) / 60);
      const seconds = durationInSeconds % 60;
      return `${hours}h ${minutes}m ${seconds}s`;
    },
    formattedShowTiming() {
      if (!this.show.show_timing) return "";

      const showDateTime = new Date(this.show.show_timing);
      const options = {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      };
      return showDateTime.toLocaleString(undefined, options);
    },
  },
  async mounted() {
    const show_id = this.$route.params.show_id;
    const resshow = await fetch(`http://localhost:5000/api/show/${show_id}`, {
      headers: {
        "Content-Type": "application/json",
        "Authentication-Token": localStorage.getItem("auth-token"),
      },
    });
    const datashow = await resshow.json();
    console.log(datashow);

    if (resshow.ok) {
      this.show = datashow;
    } else if (resshow.status == 401) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      this.error = datashow.message;
    }

    const res = await fetch(`http://localhost:5000/api/tag_show/${show_id}`, {
      headers: {
        "Authentication-Token": localStorage.getItem("auth-token"),
      },
    });

    if (res.ok) {
      const showtags = await res.json();
      console.log("showtags:", showtags);
      this.show.show_tags = showtags;
    } else {
      this.show.show_tags = null;
    }
  },
  methods: {
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.cus-link {
  color: black;
}
.star {
  color: rgb(255, 162, 0);
}
.card {
  max-width: 50%;
  margin-left: 25%;
}
@import "~bootstrap-icons/font/bootstrap-icons.css";
</style>
