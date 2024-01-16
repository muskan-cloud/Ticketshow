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
        <h2>Book tickets for {{ show.show_name }}</h2>
      </div>

      <div class="card-body">
        <div class="container">
          <h4
            v-if="
              available_tickets > 0 &&
              (!show.show_timing || new Date(show.show_timing) >= new Date())
            "
          >
            Hurry! Only {{ available_tickets }} tickets left!
          </h4>
          <h4
            v-else-if="
              available_tickets > 0 &&
              show.show_timing &&
              new Date(show.show_timing) < new Date()
            "
          >
            Oh no! Show time has passed.
          </h4>
          <h4 v-else>Oh no! HouseFull!</h4>
          <br />
          <form
            @submit.prevent="bookshow"
            v-if="
              available_tickets > 0 &&
              (!show.show_timing || new Date(show.show_timing) >= new Date())
            "
          >
            <label style="margin-left: 10px">Number of tickets : </label>
            <input
              name="booking_tickets_count"
              type="number"
              style="height: 40px"
              v-model="formData.booking_tickets_count"
              required
            /><br /><br />
            <p>Total Price : ₹ {{ totalPrice }}</p>
            <button class="btn btn-dark" type="submit">Book Show</button>
          </form>
        </div>
      </div>
      <div class="card-footer text-body-secondary">
        <p class="card-text">Not sure About Details!</p>
        <router-link
          :to="{ name: 'gotoshowforuser', params: { show_id: show.show_id } }"
          class="btn btn-dark"
          >Go back to {{ show.show_name }} details.</router-link
        >
      </div>

      <footer class="custom-footer">
        <div class="navbar custom-navbar justify-content-end">
          <router-link
            :to="'/user_dashboard/' + currentUserEmail"
            class="btn btn-dark"
            style="margin-right: auto"
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
  </div>
</template>

<script>
import { logout } from "../app.js";

export default {
  name: "BookShow",
  data() {
    return {
      show: {
        show_name: "",
        show_pic: null,
        show_description: "",
        show_price: 0,
        show_timing: null,
        show_id: 0,
        theater: {
          theater_name: "",
          theater_address: "",
        },
      },
      available_tickets: 0,
      formData: {
        booking_tickets_count: "",
      },
      showbooked: false,
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserId() {
      return this.$store.state.currentUserId;
    },
    totalPrice() {
      const ticketCount = parseInt(this.formData.booking_tickets_count);
      const ticketPrice = parseFloat(this.show.show_price);
      if (isNaN(ticketCount) || ticketCount <= 0) {
        return 0;
      }
      return ticketCount * ticketPrice;
    },
  },
  async mounted() {
    await this.getShowDetails();
    await this.getAvailableTickets();
  },
  methods: {
    async getShowDetails() {
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
        this.show = data;
      } else if (res.status === 401) {
        this.error = "Authentication required.";
        alert(this.error);
        this.$router.push("/");
      } else {
        const errorData = await res.json();
        this.error = errorData.message;
      }
    },
    async getAvailableTickets() {
      const showId = this.$route.params.show_id;
      const res = await fetch(
        `http://localhost:5000/api/avl_tickets/${showId}`,
        {
          headers: {
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        const data = await res.json();
        console.log(data);
        this.available_tickets = data;
      } else if (res.status === 401) {
        this.error = "Authentication required.";
        alert(this.error);
        this.$router.push("/");
      } else {
        const errorData = await res.json();
        this.error = errorData.message;
      }
    },
    async bookshow() {
      const bookingCount = parseInt(this.formData.booking_tickets_count);
      if (bookingCount > this.available_tickets) {
        alert("Not enough tickets available. Please select a lower quantity.");
        return;
      }

      if (bookingCount === 0) {
        alert("Booking count cannot be zero.");
        return;
      }

      const formdata = new FormData();
      formdata.append("booking_tickets_count", bookingCount);

      const showId = this.$route.params.show_id;
      const res = await fetch(
        `http://localhost:5000/api/book_show/${this.currentUserId}/${showId}`,
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
        this.showbooked = true;
        const data = await res.json();
        console.log(data);
        alert("Show Booked Successfully , Enjoy The Show!🥳");
        this.$router.push(`/bookings/${this.currentUserId}`);
      } else {
        console.log("Something went wrong");
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
.custom-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
}
</style>
