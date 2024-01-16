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
        <h4>Predict '{{ show.show_name }}' SHOW popularity(bookings)!</h4>
      </div>
      <div class="card-body">
        <div class="container">
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
          <template v-else>
            <p>No ratings yet</p>
          </template>
          <p>Show Price: ₹ {{ show.show_price }}</p>
          <p>Capacity: {{ show.theater.theater_capacity }}</p>

          <button @click="predictBookings" class="btn btn-danger">
            ➡️Predict Bookings</button
          ><br /><br />

          <div v-if="predictionValue !== null">
            <div
              v-if="show.show_timing && new Date(show.show_timing) > new Date()"
            >
              <div>
                Total Bookings: {{ total_bookings }}
                <template v-if="total_bookings > predictionValue">
                  (Greater than prediction till present time.)
                </template>
                <template v-else>
                  (Less than or equal to prediction till present
                  time.)</template
                >
              </div>
              <div>
                Prediction: {{ predictionValue }}
                <h5 v-if="show.theater.theater_capacity < predictionValue">
                  [More than theater Capacity]
                </h5>
              </div>
            </div>
            <div v-else>
              <h4>Oh no! Show time has passed.</h4>
              <p>But Total bookings Done were : {{ total_bookings }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="card-footer text-body-secondary">
        <router-link
          :to="{
            name: 'gotoshow',
            params: { show_id: show.show_id },
          }"
          class="btn btn-dark"
          >Back to show Details!</router-link
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
  name: "Prediction",
  data() {
    return {
      show: {
        show_name: "",
        show_pic: null,
        show_description: "",
        show_price: 0,
        show_timing: null,
        show_rating: 0,
        show_id: 0,
        theater: {
          theater_name: "",
          theater_address: "",
        },
        userRating: null,
      },
      predictionValue: null,
      total_bookings: null,
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
    if (!this.currentUserId) {
      alert("you need to login or signup first");
      this.$router.push("/");
      return;
    }
    const show_id = this.$route.params.show_id;
    const resshow = await fetch(`http://localhost:5000/api/show/${show_id}`, {
      headers: {
        "Authentication-Token": localStorage.getItem("auth-token"),
      },
    });

    if (resshow.ok) {
      const datashow = await resshow.json();
      console.log(datashow);
      this.show = datashow;
    } else if (resshow.status == 401) {
      this.success = false;
      this.error = "Authentication required.";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      const errorData = await resshow.json();
      this.error = errorData.message;
    }

    const tores = await fetch(
      `http://localhost:5000/api/booked_tickets_count/${show_id}`,
      {
        headers: {
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );
    if (tores.ok) {
      const totbook = await tores.json();
      this.total_bookings = totbook;
    }
  },
  methods: {
    predictBookings() {
      // Prepare the request data
      const requestData = {
        show_id: this.show.show_id,
        show_price: this.show.show_price,
        capacity: this.show.theater.theater_capacity,
      };

      // Send the prediction request to the backend
      fetch(`http://localhost:5000/predict_bookings/${this.show.show_id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
        body: JSON.stringify(requestData),
      })
        .then((response) => response.json())
        .then((data) => {
          // Handle the response from the backend
          const prediction = data.prediction;
          // Do something with the prediction value, e.g., update a variable in your Vue component
          this.predictionValue = prediction;
        })
        .catch((error) => {
          // Handle any errors that occur during the request
          console.error("Prediction request failed:", error);
        });
    },
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
.star {
  color: rgb(255, 162, 0);
}

@import "~bootstrap-icons/font/bootstrap-icons.css";
</style>
