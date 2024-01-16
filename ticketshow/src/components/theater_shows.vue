<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">Theater shows</h2>
        <form class="d-flex" @submit.prevent="search">
          <router-link to="/search" class="btn btn-dark">Search🔎</router-link>
        </form>
      </div>
    </nav>
    <div>
      <div v-if="shows.length !== 0" class="card text-center">
        <div class="card-header">
          <h4 class="card-title">Shows at {{ theater.theater_name }}</h4>
        </div>
        <div
          id="carouselExampleFade"
          class="carousel slide carousel-fade"
          style="margin-top: 0px"
        >
          <div class="carousel-inner">
            <div
              v-for="(showObj, index) in shows"
              :key="showObj.show_id"
              :class="['carousel-item', { active: index === currentIndex }]"
            >
              <div>
                <img
                  :src="'data:image/*;charset=utf-8;base64,' + showObj.show_pic"
                  class="d-block w-100"
                  alt="Show Image"
                  width="200"
                  height="500"
                />
              </div>
              <div class="carousel-caption">
                <router-link
                  :to="{
                    name: 'gotoshow',
                    params: { show_id: showObj.show_id },
                  }"
                  class="btn btn-light"
                >
                  {{ showObj.show_name }}
                </router-link>
                <router-link
                  v-if="theater.ut_id === currentUserId"
                  :to="{
                    name: 'edit_show',
                    params: { show_id: showObj.show_id },
                  }"
                  class="btn btn-light"
                  style="margin-left: 10px; margin-right: 10px"
                >
                  Edit
                </router-link>
                <h6
                  v-if="theater.ut_id === currentUserId"
                  class="btn btn-light"
                  @click="deleteshow(showObj)"
                >
                  Delete
                </h6>
              </div>
            </div>
          </div>
          <button
            class="carousel-control-prev"
            type="button"
            data-bs-target="#carouselExampleFade"
            data-bs-slide="prev"
            @click="prevItem"
          >
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button
            class="carousel-control-next"
            type="button"
            data-bs-target="#carouselExampleFade"
            data-bs-slide="next"
            @click="nextItem"
          >
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
        </div>
      </div>
      <div v-else class="card text-center">
        <h4>No Shows at {{ theater.theater_name }}</h4>
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-end">
        <router-link
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 1095px"
          >Back to your Dashboard</router-link
        >
        <router-link
          to="/add_show"
          class="btn btn-dark"
          style="margin-right: 10px"
          >Add new show</router-link
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
  name: "TheaterShows",
  data() {
    return {
      theater: {
        theater_name: "",
        theater_capacity: null,
        theater_id: null,
        theater_address: null,
        theater_pic: null,
        ut_id: 0,
      },
      shows: [],
      success: true,
      error: "Something went wrong",
      currentIndex: 0,
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
    const theaterData = await restheater.json();
    console.log(theaterData);
    if (restheater.ok) {
      this.theater = theaterData;
    } else if (restheater.status == 401) {
      this.success = false;
      this.error = theaterData.response.error;
    } else {
      this.success = false;
      this.error = theaterData.message;
      alert(theaterData.message);
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
      this.shows = datashows.sort((a, b) => {
        return new Date(b.show_timing) - new Date(a.show_timing);
      });
      console.log(this.shows);
    } else if (resshowboard.status == 401) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      this.error = datashows.message;
      alert(this.error);
    }
  },
  methods: {
    async deleteshow(show) {
      if (confirm("Are you sure you want to delete this show?")) {
        const res = await fetch(
          `http://localhost:5000/api/show/${show.show_id}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );
        if (res.ok) {
          this.shows = this.shows.filter((s) => s.show_id !== show.show_id);
        } else if (res.status === 401) {
          this.success = false;
          this.error = "you are not authorized!";
          alert(this.error);
          logout();
        } else {
          this.success = false;
          this.error = "Failed to delete show";
        }
      }
    },
    editshow(showObj) {
      const showId = showObj.show_id;
      this.$router.push({ name: "edit_show", params: { showId } });
    },
    logout() {
      logout();
      this.$router.push("/");
    },
    prevItem() {
      this.currentIndex =
        (this.currentIndex - 1 + this.shows.length) % this.shows.length;
    },
    nextItem() {
      this.currentIndex = (this.currentIndex + 1) % this.shows.length;
    },
  },
};
</script>

<style scoped>
.card {
  max-width: 500px;
  margin: 0 auto;
  overflow: hidden;
}
.carousel {
  display: flex;
  justify-content: center;
}

.carousel {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
