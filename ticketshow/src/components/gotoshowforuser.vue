<template>
  <div id="app">
    <nav class="navbar custom-navbar fixed-top">
      <div class="container-fluid">
        <router-link :to="'/account/' + currentUserEmail" class="navbar-brand"
          ><h1>Ticket Show📽️</h1></router-link
        >
        <h2 style="margin-right: 13%">Show Details</h2>
        <form class="d-flex" role="search">
          <router-link to="/search" class="btn btn-dark">Search🔎</router-link>
        </form>
      </div>
    </nav>
    <div>
      <div class="card text-center scrollable-card">
        <div class="card-header">
          <h4>{{ show.show_name }}</h4>
        </div>
        <div class="card-body" width="400" height="500">
          <p>Show Date and Time 🗓️: {{ formattedShowTiming }}</p>
          <p>Show Duration ⏱️: {{ showDuration }}</p>
          <p v-if="show.show_trailer !== 'null'">
            <a v-bind:href="show.show_trailer" target="_blank" class="cus-link"
              >Watch Trailer</a
            >
          </p>
          <p>Show genre: {{ show.show_description }}</p>
          <p>Theater name: {{ show.theater.theater_name }}</p>
          <p>Theater address: {{ show.theater.theater_address }}</p>
          <p>Show price: ₹ {{ show.show_price }}</p>
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
          <template v-if="hasTags"
            ><p>
              Show Tags:
              <span
                v-for="tag in show.show_tags"
                :key="tag.id"
                class="tag"
                style="margin-right: 10px"
              >
                {{ tag.user_tag }}
              </span>
            </p></template
          ><template v-else>
            <p>No Tags yet</p>
          </template>
          <template v-if="hasUserTags">
            <p>
              <span style="margin-right: 5px">Your Tags:</span>
              <span v-for="tag in show.userTag" :key="tag.id" class="tag">
                {{ tag.user_tag }}
                <button
                  class="btn btn-sm p-0"
                  @click="deleteTag(tag.id)"
                  style="
                    background: none;
                    border: none;
                    font-size: 10px;
                    margin-right: 5px;
                  "
                >
                  ❌
                </button></span
              >
            </p>
          </template>

          <template v-if="show.userRating !== null">
            <p>
              You Rated:
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
                class="btn btn-sm p-0"
                @click="unrateShow"
                style="
                  background: none;
                  border: none;
                  font-size: 10px;
                  margin-left: 10px;
                "
              >
                ❌
              </button>
            </p>
          </template>

          <router-link
            :to="{ name: 'rateshow', params: { show_id: show.show_id } }"
            class="btn btn-dark"
            >Rate / Tag Show</router-link
          ><br /><br />

          <router-link
            :to="{ name: 'book_show', params: { show_id: show.show_id } }"
            class="btn btn-dark"
            >Book Your Tickets Now! 📽️🍿</router-link
          >
        </div>
      </div>
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
  name: "GoToShowForUser",
  data() {
    return {
      show: {
        show_name: "",
        show_pic: null,
        show_description: "",
        show_price: 0,
        show_duration: 0,
        show_timing: null,
        show_trailer: 0,
        show_rating: 0,
        show_id: 0,
        show_tags: [],
        theater: {
          theater_name: "",
          theater_address: "",
        },
        userRating: null,
        userTag: [],
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
    showDuration() {
      const durationInSeconds = this.show.show_duration;
      const hours = Math.floor(durationInSeconds / 3600);
      const minutes = Math.floor((durationInSeconds % 3600) / 60);
      const seconds = durationInSeconds % 60;
      return `${hours}h ${minutes}m ${seconds}s`;
    },
    formattedShowTiming() {
      if (!this.show.show_timing) return ""; // Handle cases where show_timing is null or undefined

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
    hasUserTags() {
      return this.show.userTag && this.show.userTag.length > 0;
    },
    hasTags() {
      return this.show.show_tags && this.show.show_tags.length > 0;
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

    if (resshow.ok) {
      const datashow = await resshow.json();
      console.log(datashow);
      this.show = datashow;
      this.fetchUserRating(show_id);
      this.fetchUserTags(show_id);
    } else if (resshow.status == 401) {
      this.error = "you are not authorized to acccess this resource";
      alert(this.error);
      this.$router.push("/");
    } else {
      this.success = false;
      const errorData = await resshow.json();
      this.error = errorData.message;
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
    async unrateShow() {
      if (confirm("Are you sure you want to unrate this show?")) {
        const user_id = this.currentUserId;
        const show_id = this.show.show_id;

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
          this.show.userRating = null;
          alert("Show unrated successfully.");
          const resshow = await fetch(
            `http://localhost:5000/api/show/${show_id}`,
            {
              headers: {
                "Authentication-Token": localStorage.getItem("auth-token"),
              },
            }
          );

          if (resshow.ok) {
            const datashow = await resshow.json();
            console.log(datashow);
            this.show = datashow;
            this.fetchUserRating(show_id);
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
        } else {
          alert("Failed to unrate show.");
        }
      }
    },
    async fetchUserRating(show_id) {
      const user_id = this.currentUserId;
      const res = await fetch(
        `http://localhost:5000/api/rate_show/${user_id}/${show_id}`,
        {
          headers: {
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        const userRating = await res.json();
        console.log("User Rating:", userRating);
        this.show.userRating = userRating;
      } else {
        this.show.userRating = null;
      }
    },
    async fetchUserTags(show_id) {
      const user_id = this.currentUserId;
      const res = await fetch(
        `http://localhost:5000/api/tag_show/${user_id}/${show_id}`,
        {
          headers: {
            "Authentication-Token": localStorage.getItem("auth-token"),
          },
        }
      );

      if (res.ok) {
        const responseData = await res.json();

        // Assuming the backend now returns a list of tag objects, each containing 'id' and 'user_tag'
        const userTags = responseData.map((tag) => ({
          id: tag.id,
          user_tag: tag.user_tag,
        }));

        console.log("User Tags:", userTags);
        this.show.userTag = userTags;
      } else {
        this.show.userTag = [];
      }
    },

    async deleteTag(tag_id) {
      if (confirm("Are you sure you want to delete this tag?")) {
        const user_id = this.currentUserId;
        const show_id = this.show.show_id;

        const res = await fetch(
          `http://localhost:5000/api/tag_show/${user_id}/${show_id}/${tag_id}`,
          {
            method: "DELETE",
            headers: {
              "Authentication-Token": localStorage.getItem("auth-token"),
            },
          }
        );

        if (res.ok) {
          this.show.userTag = this.show.userTag.filter(
            (tag) => tag.id !== tag_id
          );
          alert("Tag deleted successfully.");
          this.$router.push(`/gotoshowforuser/${show_id}`);
        } else {
          alert("Failed to delete the tag.");
        }
      }
    },
  },
};
</script>

<style scoped>
.cus-link {
  color: black;
}
.card {
  max-width: 50%;
  margin-left: 25%;
}
.scrollable-card {
  height: 600px;
  overflow-y: auto;
}
.star-rating {
  display: inline-block;
  font-size: 24px;
  color: #004f51;
  cursor: pointer;
}

.star-filled {
  color: rgb(255, 162, 0);
}
.star {
  color: rgb(255, 162, 0);
}

@import "~bootstrap-icons/font/bootstrap-icons.css";
</style>
