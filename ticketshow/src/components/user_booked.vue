<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 12%">Shows Booked by {{ currentUserName }}</h2>
        <button class="btn btn-dark" @click="exportBookingsCSV">
          Export All Booking Details [csv]
        </button>
      </div>
    </nav>
    <div v-if="bookedShows.length === 0" class="card text-center">
      <div class="card-header">
        <h4 class="card-title">You haven't booked any shows yet!</h4>
      </div>
    </div>
    <div v-else class="card text-center table-card">
      <table>
        <thead>
          <tr>
            <th class="table-heading">Show Name</th>
            <th class="table-heading">No. of Tickets Booked</th>
            <th class="table-heading">seat numbers</th>
            <th class="table-heading">Rating</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in bookedShows" :key="booking.booking_id">
            <router-link
              :to="{
                name: 'gotoshowforuser',
                params: { show_id: booking.show.show_id },
              }"
              class="btn btn-outline-dark"
            >
              {{ booking.show.show_name }}</router-link
            >
            <td>{{ booking.booking_tickets_count }}</td>
            <td>{{ booking.seat_range }}</td>
            <td>
              <router-link
                :to="{
                  name: 'rateshow',
                  params: { show_id: booking.show.show_id },
                }"
                class="btn btn-dark"
                >Rate/Tag Show</router-link
              >
            </td>
            <td>
              <button class="btn btn-info" @click="downloadTicket(booking)">
                Download Ticket
              </button>
            </td>
            <td>
              <button
                v-if="
                  !booking.show.show_timing ||
                  new Date(booking.show.show_timing) >= new Date()
                "
                class="btn btn-danger"
                @click="CancelBooking(booking)"
              >
                Cancel Booking
              </button>
              <button v-else class="btn btn-success">Watched!</button>
            </td>
          </tr>
        </tbody>
      </table>
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
  name: "UserBooked",
  data() {
    return {
      bookedShows: [],
    };
  },
  computed: {
    currentUserEmail() {
      return this.$store.state.currentUserEmail;
    },
    currentUserName() {
      return this.$store.state.currentUsername;
    },
    isAdmin() {
      return this.$store.state.currentUserRoles.includes("<Role 1>");
    },
    isUser() {
      return this.$store.state.currentUserRoles.includes("<Role 2>");
    },
  },
  async mounted() {
    const user_id = this.$route.params.user_id;

    const resshowboard = await fetch(
      `http://localhost:5000/api/bookings/${user_id}`,
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
      this.bookedShows = datashows;

      for (const booking of this.bookedShows) {
        const show_id = booking.show.show_id;
        const res = await fetch(
          `http://localhost:5000/api/rate_show/${user_id}/${show_id}`,
          {
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );
        const data = await res.json();
        console.log(data);

        if (res.ok) {
          booking.showRating = data;
        } else {
          booking.showRating = null;
        }
      }
    } else if (resshowboard.status == 401) {
      this.success = false;
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
    async unrateShow(booking) {
      if (confirm("Are you sure you want to unrate this show?")) {
        const user_id = this.$route.params.user_id;
        const show_id = booking.show.show_id;

        const res = await fetch(
          `http://localhost:5000/api/rate_show/${user_id}/${show_id}`,
          {
            method: "DELETE",
            headers: {
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );

        if (res.ok) {
          booking.showRating = null;
          alert("Show unrated successfully.");
        } else {
          alert("Failed to unrate show.");
        }
      }
    },
    async CancelBooking(booking) {
      if (confirm("Are you sure you want to delete this booking?")) {
        const user_id = this.$route.params.user_id;
        const show_id = booking.show.show_id;
        const booking_id = booking.booking_id;
        const res = await fetch(
          `http://localhost:5000/api/cancel_booking/${user_id}/${show_id}/${booking_id}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );

        if (res.ok) {
          this.bookedShows = this.bookedShows.filter(
            (booking) => booking.show.show_id !== show_id
          );
          alert("Booking Cancelled successfully.");
        } else {
          alert("Failed to delete booking.");
        }
      }
    },
    async downloadTicket(booking) {
      try {
        const booking_id = booking.booking_id;
        const response = await fetch(
          `http://localhost:5000/download_ticket/${booking_id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
            responseType: "blob",
          }
        );
        if (response.ok) {
          const pdfReport = await response.blob();
          const pdfUrl = URL.createObjectURL(pdfReport);
          const a = document.createElement("a");
          a.href = pdfUrl;
          a.download = `${booking.booking_id}_ticket.pdf`;
          a.click();
          alert("Ticket Download started");
        } else {
          alert("Failed to download Ticket!");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to download Ticket!");
      }
    },
    async exportBookingsCSV() {
      try {
        const user_id = this.$route.params.user_id;
        const response = await fetch(
          `http://localhost:5000/export_user_csv/${user_id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
            responseType: "blob",
          }
        );
        if (response.ok) {
          const csvBook = await response.blob();
          const csvUrl = URL.createObjectURL(csvBook);
          const a = document.createElement("a");
          a.href = csvUrl;
          a.download = `${user_id}_data.csv`;
          a.click();
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

<style scoped></style>
