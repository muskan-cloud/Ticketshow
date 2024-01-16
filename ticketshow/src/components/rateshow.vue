<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">
          Rate Show and Tag {{ showdata.show_name }} [{{
            showdata.theater.theater_name
          }}] !
        </h2>
        <form class="d-flex" role="search">
          <router-link to="/search" class="btn btn-dark">Search</router-link>
        </form>
      </div>
    </nav>
    <div class="card text-center">
      <template v-if="show.userRating !== null">
        <p>
          <label class="rated-text">You Rated:</label>
          <span class="star-rating">
            <span
              v-for="rating in 5"
              :key="rating"
              :class="{ 'star-filled': rating <= show.userRating }"
            >
              ★
            </span>
          </span>
          <button
            class="btn btn-danger"
            @click="unrateShow"
            style="margin-left: 5px"
          >
            Unrate
          </button>
        </p>
      </template>

      <form v-else @submit.prevent="submitRating">
        <label for="userRating">Your Rating:</label>
        <div class="star-rating">
          <span
            v-for="rating in 5"
            :key="rating"
            :class="{ 'star-filled': rating <= formData.userRating }"
            @click="formData.userRating = rating"
          >
            ★
          </span>
        </div>
        <button type="submit" class="btn btn-dark" style="margin-left: 5px">
          Submit Rating
        </button>
      </form>
      <br />
      <form @submit.prevent="submitTag">
        <label for="user_tag">Your Tag:</label>
        <input
          type="text"
          v-model="formData.user_tag"
          @input="checkDefaultValue()"
          required
        />
        <button type="submit" class="btn btn-dark" style="margin-left: 5px">
          Submit #Tag
        </button>
      </form>
    </div>
    <footer style="position: fixed; bottom: 0; width: 100%">
      <div class="navbar custom-navbar justify-content-end">
        <router-link
          :to="'/user_dashboard/' + currentUserEmail"
          class="btn btn-dark"
          style="margin-right: 1228px"
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
</template>

<script>
import { logout } from "../app.js";
export default {
  name: "RateShow",
  data() {
    return {
      show: {
        userRating: null,
      },
      showdata: {
        show_name: "",
        theater: {
          theater_name: "",
        },
      },
      formData: {
        userRating: 0,
        user_tag: "",
      },
      defaultTag: "#",
      showrated: false,
      showtagged: false,
      showratedbefore: false,
      error: "",
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
    this.formData.user_tag = this.defaultTag;
    const user_id = this.currentUserId;
    const show_id = this.$route.params.show_id;
    const res = await fetch(
      `http://localhost:5000/api/rate_show/${user_id}/${show_id}`,
      {
        headers: {
          "Content-Type": "application/json",
          "Authentication-Token": localStorage.getItem("auth-token"),
        },
      }
    );

    if (res.ok) {
      const userRating = await res.json();
      console.log("User Rating:", userRating);
      this.show.userRating = userRating;
    } else if (res.status == 401) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.show.userRating = null;
      this.error = "spomething went wrong";
      alert(this.error);
    }
    const s_id = this.$route.params.show_id;
    const resshow = await fetch(`http://localhost:5000/api/show/${s_id}`, {
      headers: {
        "Content-Type": "application/json",
        "Authentication-Token": localStorage.getItem("auth-token"),
      },
    });
    const datashow = await resshow.json();
    console.log(datashow);

    if (resshow.ok) {
      this.showdata = datashow;
    } else if (resshow.status == 401) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      this.error = datashow.message;
    }
  },
  methods: {
    async submitRating() {
      const userRating = this.formData.userRating;
      const formdata = new FormData();
      formdata.append("userRating", userRating);
      const user_id = this.$store.state.currentUserId;
      const show_id = this.$route.params.show_id;
      const res = await fetch(
        `http://localhost:5000/api/rate_show/${user_id}/${show_id}`,
        {
          method: "POST",
          body: formdata,
          headers: {
            Authorization: "Bearer " + localStorage.getItem("auth_token"),
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );
      const data = await res.json();
      if (res.ok) {
        this.showrated = true;
        console.log(data);
        alert("Show Rated Successfully");
      } else if (res.status == 401) {
        this.success = false;
        this.error = data.message;
      } else {
        console.log("Something went wrong");
      }
    },

    async submitTag() {
      this.formData.user_tag = this.formData.user_tag.trim();

      if (this.formData.user_tag === "" || this.formData.user_tag === "#") {
        alert("Please enter a valid tag.");
        return;
      }

      const user_tag = this.formData.user_tag;
      const formdata = new FormData();
      formdata.append("user_tag", user_tag);
      const user_id = this.$store.state.currentUserId;
      const show_id = this.$route.params.show_id;

      const res = await fetch(
        `http://localhost:5000/api/tag_show/${user_id}/${show_id}`,
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
        this.showtagged = true;
        const data = await res.json();
        console.log(data);
        alert("Show Tagged Successfully");
      } else {
        console.log("Something went wrong");
      }
    },
    async unrateShow() {
      if (confirm("Are you sure you want to unrate this show?")) {
        const show_id = this.$route.params.show_id;
        const user_id = this.$store.state.currentUserId;

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
          alert("Show unrated successfully.");
        } else {
          alert("Failed to unrate show.");
        }
      }
    },
    checkDefaultValue() {
      if (this.formData.user_tag === "") {
        this.formData.user_tag = this.defaultTag;
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
.rated-text {
  margin-right: 10px;
  color: black;
}
.star-rating {
  display: inline-block;
  font-size: 24px;
  color: #6cbaff;
  cursor: pointer;
}

.star-filled {
  color: rgb(255, 162, 0);
}
</style>
