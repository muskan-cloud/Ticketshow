<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">
          {{ currentUserName }}'s User Dashboard
        </h2>
        <form class="d-flex" role="search">
          <router-link to="/search" class="btn btn-dark">Search 🔎</router-link>
        </form>
      </div>
    </nav>

    <div>
      <div v-if="shows.length === 0" class="card text-center">
        <div class="card-header">
          <h4 class="card-title">Sorry No Shows Running!</h4>
        </div>
      </div>

      <div v-else>
        <div class="card text-center">
          <div class="card-header">
            <p>Shows</p>
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
                    :src="
                      'data:image/*;charset=utf-8;base64,' + showObj.show_pic
                    "
                    class="d-block w-100"
                    alt="Theater Image"
                    width="200"
                    height="500"
                  />
                </div>

                <div class="carousel-caption">
                  <router-link
                    :to="{
                      name: 'gotoshowforuser',
                      params: { show_id: showObj.show_id },
                    }"
                    class="btn btn-outline-light"
                  >
                    {{ showObj.show_name }} <br />
                    Location : {{ showObj.theater.theater_name }}
                  </router-link>
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
              <span
                class="carousel-control-prev-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Previous</span>
            </button>
            <button
              class="carousel-control-next"
              type="button"
              data-bs-target="#carouselExampleFade"
              data-bs-slide="next"
              @click="nextItem"
            >
              <span
                class="carousel-control-next-icon"
                aria-hidden="true"
              ></span>
              <span class="visually-hidden">Next</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar d-flex justify-content-between">
        <div>
          <a
            href="http://localhost:8025"
            target="_blank"
            class="btn btn-dark"
            style="margin-right: 10px"
            >Check Your MailBox</a
          >
        </div>
        <div>
          <router-link
            v-if="isAdmin"
            :to="'/admin_dashboard/' + currentUserEmail"
            class="btn btn-dark"
            style="margin-right: 10px"
          >
            Switch to Admin Dashboard</router-link
          >
          <a
            href="/"
            class="btn btn-dark"
            style="margin-right: 10px"
            @click.prevent="logout"
          >
            Logout
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { logout } from "../app.js";

export default {
  name: "UserDashboard",
  data() {
    return {
      account: {
        username: "",
        email: "",
        id: null,
        roles: [],
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
    currentUserName() {
      return this.$store.state.currentUsername;
    },
    isAdmin() {
      return this.account.roles.includes("<Role 1>");
    },
  },
  async mounted() {
    const email = this.$route.params.email;
    const resaccount = await fetch(`http://localhost:5000/api/users/${email}`, {
      headers: {
        "Content-Type": "application/json",
        "Authentication-Token": localStorage.getItem("auth-token"),
      },
    });
    const dataaccount = await resaccount.json();
    console.log(dataaccount);
    if (resaccount.ok) {
      this.account = dataaccount;
      this.$store.commit("setCurrentUser", {
        id: dataaccount.id,
        username: dataaccount.username,
        email: dataaccount.email,
        roles: dataaccount.roles,
      });
    } else if (resaccount.status == 401) {
      this.success = false;
      this.error = dataaccount.response.error;
    } else {
      this.success = false;
      this.error = dataaccount.message;
      alert("Something went wrong");
      this.$router.push("/");
      localStorage.clear();
    }

    const resdash = await fetch(
      `http://localhost:5000/api/user_dashboard/${email}`,
      {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );
    const datadash = await resdash.json();
    console.log(datadash);

    if (resdash.ok) {
      this.shows = datadash.sort((a, b) => {
        return new Date(b.show_timing) - new Date(a.show_timing);
      });
      console.log(this.shows);
    } else if (resdash.status == 401) {
      this.success = false;
      this.error = datadash.response.error;
    } else {
      this.success = false;
      this.error = datadash.message;
      alert(this.error);
      this.$router.push("/");
    }
  },
  methods: {
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
.navbar-brand {
  color: black;
}
</style>
