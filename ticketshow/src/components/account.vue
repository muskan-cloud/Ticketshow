<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <a class="navbar-brand"><h1>Ticket Show 📽️</h1></a>
        <h2 style="margin-right: 10%">{{ account.username }}'s Profile</h2>
        <form class="d-flex" role="search">
          <router-link
            v-if="isAdmin"
            :to="'/revenues/' + currentUserId"
            class="btn btn-dark"
            style="margin-right: 10px"
            >Revenue</router-link
          >
          <router-link :to="'/user_update/' + account.id" class="btn btn-dark"
            >edit account</router-link
          >
        </form>
      </div>
    </nav>
    <div class="card text-center">
      <div class="card-header">
        <h4>Your Email: {{ account.email }}</h4>
        <h4>Username : {{ account.username }}</h4>
        <h4 style="text-decoration: underline">Roles</h4>
        <h5 v-if="isAdmin && isUser">Admin , General User</h5>
        <h5 v-if="isUser && !isAdmin">General User</h5>
        <h5 v-if="!isUser && isAdmin">Admin</h5>
      </div>
      <div
        v-if="isAdmin && account.theaters.length !== 0"
        class="card-body scrollable-card"
      >
        <h3
          style="text-decoration: underline"
          v-if="account.theaters.length !== 0"
        >
          Your Theaters and their respective shows:
        </h3>
        <br />
        <div v-for="theater in account.theaters" :key="theater.theater_id">
          <h4 v-if="theater.shows.length !== 0">
            <router-link
              :to="{
                name: 'theater_details',
                params: { theater_id: theater.theater_id },
              }"
              class="custom-link"
              >{{ theater.theater_name }}'s Shows:</router-link
            >
          </h4>
          <h4 v-else>{{ theater.theater_name }}</h4>
          <br />
          <ul v-if="theater.shows.length !== 0">
            <li v-for="show in theater.shows" :key="show.show_id">
              <router-link
                :to="{
                  name: 'gotoshow',
                  params: { show_id: show.show_id },
                }"
                class="custom-link"
                >{{ show.show_name }} -
                {{ formatShowTiming(show.show_timing) }}</router-link
              >
            </li>
          </ul>
          <br />
        </div>
      </div>
      <div
        v-else-if="isAdmin && account.theaters.length === 0"
        class="card-body"
      >
        Please add your theater.
        <router-link
          to="/add_theater"
          class="btn btn-dark"
          style="margin-right: 10px"
          >Add new Theater</router-link
        >
      </div>
      <div v-else class="card-body" style="display: none"></div>

      <div class="card-footer">
        <router-link
          v-if="isUser"
          :to="'/bookings/' + account.id"
          class="btn btn-dark"
          style="margin-right: 10px"
        >
          Shows Booked!
        </router-link>
      </div>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div
        class="navbar custom-navbar"
        style="display: flex; justify-content: space-between"
      >
        <div>
          <router-link
            v-if="isAdmin && !isUser"
            :to="'/admin_dashboard/' + currentUserEmail"
            class="btn btn-dark"
            style="margin-right: 10px"
            >Back to Your Dashboard</router-link
          >
          <router-link
            v-if="isUser && !isAdmin"
            :to="'/user_dashboard/' + currentUserEmail"
            class="btn btn-dark"
            style="margin-right: 10px"
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
            style="margin-right: 10px"
            >Back to User Dashboard</router-link
          >
          <button class="btn btn-dark" for="export-format">
            Choose Export Format:

            <select id="export-format" v-model="selectedExportFormat">
              <option value="pdf">PDF</option>
              <option value="html">HTML</option>
            </select>
          </button>
          <button
            class="btn btn-dark"
            style="margin-left: 10px"
            @click="exportSelectedFormat('user')"
          >
            Export Report [User]
          </button>
          <button
            v-if="account.theaters.length !== 0"
            class="btn btn-dark"
            style="margin-left: 10px"
            @click="exportSelectedFormat('admin')"
          >
            Export Report [Admin]
          </button>
        </div>
        <div>
          <button
            class="btn btn-danger"
            style="margin-right: 10px"
            @click="deleteaccount(currentUserEmail)"
          >
            Delete Account
          </button>
          <a
            href="/"
            class="btn btn-dark"
            @click.prevent="logout"
            style="margin-right: 10px"
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
  name: "account",
  data() {
    return {
      account: {
        username: "",
        email: "",
        id: null,
        roles: [],
        theaters: [],
      },
      selectedExportFormat: "pdf",
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
      return this.account.roles.includes("<Role 1>");
    },
    isUser() {
      return this.account.roles.includes("<Role 2>");
    },
  },
  async mounted() {
    const email = this.$store.state.currentUserEmail;
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
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      this.error = dataaccount.message;
      alert(this.error);
      this.$router.push("/");
      localStorage.clear();
    }
  },
  methods: {
    formatShowTiming(showTiming) {
      const showDateTime = new Date(showTiming);
      const options = {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      };
      return showDateTime.toLocaleString(undefined, options);
    },
    async exportSelectedFormat(type) {
      const isUser = type === "user";
      try {
        const format = this.selectedExportFormat;

        if (format) {
          if (format === "pdf") {
            if (isUser) {
              this.exportUserReport();
            } else {
              this.exportAdminReport();
            }
          } else if (format === "html") {
            if (isUser) {
              this.exportUserHtmlReport();
            } else {
              this.exportAdminHtmlReport();
            }
          } else {
            alert("Invalid export format choice");
          }
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred while choosing export format");
      }
    },
    async exportUserReport() {
      try {
        const user_id = this.account.id;
        const response = await fetch(
          `http://localhost:5000/export_report/${user_id}`,
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
          a.download = `${this.account.id}_data.pdf`;
          a.click();
          alert("PDF export job started");
        } else {
          alert("Failed to start PDF export job");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to start PDF export job");
      }
    },
    async exportAdminReport() {
      try {
        const user_id = this.account.id;
        const response = await fetch(
          `http://localhost:5000/export_admin_report/${user_id}`,
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
          a.download = `${this.account.id}_theaters_data.pdf`;
          a.click();
          alert("Pdf export job started");
        } else {
          alert("Failed to start Pdf export job");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to start Pdf export job");
      }
    },
    async exportUserHtmlReport() {
      try {
        const user_id = this.account.id;
        const response = await fetch(
          `http://localhost:5000/export_report_user_html/${user_id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
            responseType: "text",
          }
        );
        if (response.ok) {
          const HTMLReport = await response.text();
          const a = document.createElement("a");
          a.href =
            "data:text/html;charset=utf-8," + encodeURIComponent(HTMLReport);
          a.download = `${this.account.id}_data.html`;
          a.click();
          alert("HTML export job started");
        } else {
          alert("Failed to start HTML export job");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to start HTML export job");
      }
    },
    async exportAdminHtmlReport() {
      try {
        const user_id = this.account.id;
        const response = await fetch(
          `http://localhost:5000/export_report_admin_html/${user_id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
            responseType: "text",
          }
        );
        if (response.ok) {
          const HTMLReport = await response.text();
          const a = document.createElement("a");
          a.href =
            "data:text/html;charset=utf-8," + encodeURIComponent(HTMLReport);
          a.download = `${this.account.id}_theaters_data.html`;
          a.click();
          alert("HTML export job started");
        } else {
          alert("Failed to start HTML export job");
        }
      } catch (error) {
        console.error(error);
        alert("Failed to start HTML export job");
      }
    },
    async deleteaccount(email) {
      if (
        confirm(
          "Are you sure you want to delete your account?,You can download your Tickets or cancel Bookings if any Booked by clicking on shows booked button."
        )
      ) {
        const res = await fetch(`http://localhost:5000/api/users/${email}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        });
        if (res.ok) {
          alert("Account deleted successfully");
          this.$router.push("/");
        } else if (res.status === 401) {
          this.success = false;
          this.error = res.response.error;
          logout();
        } else {
          this.success = false;
          this.error = "Failed to delete account";
        }
      }
    },
    logout() {
      logout();
      this.$router.push("/");
    },
  },
};
</script>

<style>
.custom-link:link,
.custom-link:visited {
  color: black;
  background-color: transparent;
  text-decoration: none;
}
</style>
