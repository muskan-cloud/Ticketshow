<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">Theater Revenues</h2>
        <form class="d-flex" @submit.prevent="search">
          <router-link to="/search" class="btn btn-dark">Search🔎</router-link>
        </form>
      </div>
    </nav>
    <div>
      <div v-if="theaterDataList.length !== 0" class="card text-center">
        <div class="card-header">
          <h4 class="card-title">
            Shows at {{ theaterDataList[currentIndex].theaterName }}
          </h4>
        </div>
        <div class="carousel-container">
          <div id="carouselExampleFade" class="carousel slide carousel-fade">
            <div class="carousel-inner">
              <div
                v-for="(theaterData, index) in theaterDataList"
                :key="index"
                :class="['carousel-item', { active: index === currentIndex }]"
              >
                <img :src="theaterData.graphImageUrl" alt="Revenue Graph" />
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <h5>Total Revenue: ₹ {{ calculateTotalRevenue }}</h5>
        </div>
        <div v-if="theaterDataList.length > 1">
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
        <p>No revenue data available.</p>
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-between">
        <router-link
          :to="'/admin_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-left: 10px"
        >
          Back to your Dashboard
        </router-link>
        <div style="display: flex; align-items: center">
          <h5 style="margin: 0 10px">
            {{ currentUserName }}'s Total Revenue: ₹{{
              calculateUserTotalRevenue
            }}
          </h5>
        </div>
        <a
          href="/"
          class="btn btn-dark"
          @click.prevent="logout"
          style="margin-right: 10px"
        >
          Logout
        </a>
      </div>
    </footer>
  </div>
</template>

<script>
import { logout } from "../app.js";
export default {
  data() {
    return {
      theaterDataList: [],
      currentIndex: 0,
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserName() {
      return this.$store.state.currentUsername;
    },
    calculateTotalRevenue() {
      if (this.theaterDataList.length === 0) {
        return 0;
      }
      const currentTheaterData = this.theaterDataList[this.currentIndex];

      const totalRevenue = currentTheaterData.revenues.reduce(
        (sum, revenue) => sum + revenue,
        0
      );

      return totalRevenue;
    },
    calculateUserTotalRevenue() {
      if (this.theaterDataList.length === 0) {
        return 0;
      }

      const totalRevenue = this.theaterDataList.reduce((sum, theaterData) => {
        const theaterRevenue = theaterData.revenues.reduce(
          (theaterSum, revenue) => theaterSum + revenue,
          0
        );
        return sum + theaterRevenue;
      }, 0);

      return totalRevenue;
    },
  },

  mounted() {
    if (!this.currentUserEmail) {
      alert("you need to login or signup first");
      this.$router.push("/");
      return;
    }
    this.fetchRevenueData();
  },

  methods: {
    fetchRevenueData() {
      fetch(
        `http://localhost:5000/revenue/${this.$store.state.currentUserId}`,
        {
          method: "GET",
          headers: {
            "Authentication-Token": localStorage.getItem("auth-token"),
            "Content-Type": "application/json",
          },
        }
      )
        .then((response) => response.json())
        .then((data) => {
          this.theaterDataList = data;
        })
        .catch((error) => {
          console.error("Error fetching revenue data:", error);
        });
    },

    calculateBarHeight(revenue) {
      const maxHeight = 200;
      const maxRevenue = Math.max(
        ...this.theaterDataList.map((theater) => Math.max(...theater.revenues))
      );
      return `${maxHeight - (revenue / maxRevenue) * maxHeight}px`;
    },

    prevItem() {
      this.currentIndex =
        (this.currentIndex - 1 + this.theaterDataList.length) %
        this.theaterDataList.length;
    },

    nextItem() {
      this.currentIndex = (this.currentIndex + 1) % this.theaterDataList.length;
    },
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.carousel-container {
  max-width: 90%;
  margin: 0 auto;
  padding: 0px 0px;
  margin-top: 0%;
}

.card {
  margin: 0 auto;
  max-width: 40%;
  margin-bottom: 20px;
}

.carousel-inner img {
  max-width: 100%;
  height: auto;
}
</style>
