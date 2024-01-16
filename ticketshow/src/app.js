import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import store from "./store/store.js";
import App from "./App.vue";
import revenues from "./components/revenues.vue";
import welcome from "./components/welcome.vue";
import admin_signup from "./components/admin_signup.vue";
import user_signup from "./components/user_signup.vue";
import admin_login from "./components/admin_login.vue";
import user_login from "./components/user_login.vue";
import admin_dashboard from "./components/admin_dashboard.vue";
import user_dashboard from "./components/user_dashboard.vue";
import add_theater from "./components/add_theater.vue";
import edit_theater from "./components/edit_theater.vue";
import add_show from "./components/add_show.vue";
import theater_shows from "./components/theater_shows.vue";
import gotoshow from "./components/gotoshow.vue";
import gotoshowforuser from "./components/gotoshowforuser.vue";
import edit_show from "./components/edit_show.vue";
import book_show from "./components/book_show.vue";
import search from "./components/search.vue";
import theater_details from "./components/theater_details.vue";
import user_booked from "./components/user_booked.vue";
import rateshow from "./components/rateshow.vue";
import Prediction from "./components/prediction.vue";
import Account from "./components/account.vue";
import UserUpdate from "./components/edit_account.vue";

const routes = [
  { path: "/", component: welcome },
  { path: "/admin_signup", component: admin_signup },
  { path: "/general_signup", component: user_signup },
  { path: "/admin_login", component: admin_login },
  { path: "/user_login", component: user_login },
  { path: "/user_update/:id", component: UserUpdate, props: true },
  { path: "/revenues/:id", component: revenues, props: true },
  { path: "/admin_dashboard/:email", component: admin_dashboard, props: true },
  { path: "/user_dashboard/:email", component: user_dashboard, props: true },
  { path: "/account/:email", component: Account, props: true },
  { path: "/add_theater", component: add_theater },
  {
    path: "/edit_theater/:theater_id",
    component: edit_theater,
    name: "edit_theater",
    props: true,
  },
  {
    path: "/theater/:theater_id",
    component: theater_shows,
    name: "theater_shows",
    props: true,
  },
  {
    path: "/add_show",
    component: add_show,
    name: "add_show",
  },
  {
    path: "/gotoshow/:show_id",
    component: gotoshow,
    name: "gotoshow",
    props: true,
  },
  {
    path: "/gotoshowforuser/:show_id",
    component: gotoshowforuser,
    name: "gotoshowforuser",
    props: true,
  },
  {
    path: "/edit_show/:show_id",
    component: edit_show,
    name: "edit_show",
    props: true,
  },
  {
    path: "/book_show/:show_id",
    component: book_show,
    name: "book_show",
    props: true,
  },
  {
    path: "/theater_details/:theater_id",
    component: theater_details,
    name: "theater_details",
    props: true,
  },
  { path: "/search", component: search },
  {
    path: "/bookings/:user_id",
    component: user_booked,
    name: "user_booked",
    props: true,
  },
  {
    path: "/rate_show/:show_id",
    component: rateshow,
    name: "rateshow",
    props: true,
  },
  {
    path: "/predict_popularity/:show_id",
    component: Prediction,
    name: "Prediction",
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);

app.use(router);
app.use(store);

app.mount("#app");

export const logout = async () => {
  const res = await fetch("/");
  if (res.ok) {
    localStorage.clear();
  } else {
    console.log("could not log out");
  }
};

app.config.globalProperties.$logout = logout;
