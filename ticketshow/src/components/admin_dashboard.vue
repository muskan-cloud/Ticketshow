<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">
          {{ currentUserName }}'s Admin Dashboard
        </h2>
        <form class="d-flex" @submit.prevent="search">
          <router-link to="/search" class="btn btn-dark">Search 🔎</router-link>
        </form>
      </div>
    </nav>
    <div>
      <div v-if="theaters.length === 0" class="card text-center">
        <div class="card-header">
          <h4 class="card-title">You haven't added any theaters yet.</h4>
        </div>
      </div>

      <div v-else>
        <div class="card text-center">
          <div class="card-header">
            <h4 class="card-title">YOUR THEATERS!</h4>
          </div>
          <div
            id="carouselExampleFade"
            class="carousel slide carousel-fade"
            style="margin-top: 0px"
          >
            <div class="carousel-inner">
              <div
                v-for="(theaterObj, index) in theaters"
                :key="theaterObj.theater_id"
                :class="['carousel-item', { active: index === currentIndex }]"
              >
                <div>
                  <img
                    :src="
                      'data:image/*;charset=utf-8;base64,' +
                      theaterObj.theater_pic
                    "
                    class="d-block w-100"
                    alt="Theater Image"
                  />
                </div>
                <div class="carousel-caption">
                  <router-link
                    :to="{
                      name: 'theater_shows',
                      params: { theater_id: theaterObj.theater_id },
                    }"
                    class="btn btn-light"
                  >
                    {{ theaterObj.theater_name }}
                  </router-link>
                  <router-link
                    :to="{
                      name: 'edit_theater',
                      params: { theater_id: theaterObj.theater_id },
                    }"
                    class="btn btn-light"
                    style="margin-left: 15px; margin-right: 15px"
                  >
                    Edit
                  </router-link>
                  <h6 class="btn btn-light" @click="deletetheater(theaterObj)">
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
      <div
        class="navbar custom-navbar"
        style="display: flex; justify-content: space-between"
      >
        <div>
          <a
            href="http://localhost:8025"
            target="_blank"
            class="btn btn-dark"
            style="margin-left: 10px"
            >Check Your MailBox</a
          >
        </div>

        <div>
          <router-link
            v-if="isUser"
            :to="'/user_dashboard/' + currentUserEmail"
            class="btn btn-dark"
            style="margin-right: 10px"
          >
            Switch to User Dashboard</router-link
          >
          <router-link
            to="/add_theater"
            class="btn btn-dark"
            style="margin-right: 10px"
            >Add new Theater</router-link
          >
          <a
            href="/"
            class="btn btn-dark"
            style="margin-right: 10px"
            @click.prevent="logout"
            >Logout</a
          >
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { logout } from "/src/app.js";

export default {
  name: "AdminDashboard",
  data() {
    return {
      account: {
        username: "",
        email: "",
        id: null,
        roles: [],
      },
      theaters: [],
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
    isUser() {
      return this.account.roles.includes("<Role 2>");
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
      console.log("setting done!");
    } else if (resaccount.status == 401) {
      this.success = false;
      this.error = dataaccount.response.error;
    } else {
      this.success = false;
      this.error = dataaccount.message;
      alert("something went wrong");
      this.$router.push("/");
      localStorage.clear();
    }

    const cnmail = this.$store.state.currentUserEmail;
    const resdash = await fetch(
      `http://localhost:5000/api/admin_dashboard/${cnmail}`,
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
      this.theaters = datadash;
      console.log(this.theaters);
    } else if (resdash.status == 401) {
      this.success = false;
      this.error = datadash.response.error;
    } else {
      this.success = false;
      this.error = datadash.message;
      this.$router.push("/");
      alert(this.error);
      localStorage.clear();
    }
  },
  methods: {
    prevItem() {
      this.currentIndex =
        (this.currentIndex - 1 + this.theaters.length) % this.theaters.length;
    },
    nextItem() {
      this.currentIndex = (this.currentIndex + 1) % this.theaters.length;
    },
    async deletetheater(theater) {
      if (confirm("Are you sure you want to delete this theater?")) {
        const res = await fetch(
          `http://localhost:5000/api/users/${this.currentUserEmail}/theaters/${theater.theater_id}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );
        if (res.ok) {
          // Removing the theater from the list of theaters
          this.theaters = this.theaters.filter(
            (t) => t.theater_id !== theater.theater_id
          );
        } else if (res.status === 401) {
          this.success = false;
          this.error = res.response.error;
          logout();
        } else {
          this.success = false;
          this.error = "Failed to delete theater";
        }
      }
    },
    edittheater(theater) {
      const theaterId = theater.theater_id;
      this.$router.push({ name: "edit_theater", params: { theaterId } });
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
