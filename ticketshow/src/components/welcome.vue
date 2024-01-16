<template>
  <div id="app">
    <div class="card text-center">
      <div class="card-header">
        <h2 class="card-title">WELCOME TO TICKET SHOW!</h2>
      </div>
      <div class="card-body">
        <h4>
          We are excited to have you! Please login according to your desired
          role.
        </h4>
        <br />
        <router-link
          to="/admin_login"
          class="btn btn-dark"
          style="margin-right: 10px"
          >Login as Admin</router-link
        >
        <router-link to="/user_login" class="btn btn-dark"
          >Login as User</router-link
        >
        <br />
      </div>
      <div class="card-footer text-body-secondary">
        <h5>
          New to TicketShow? Please signup according to your desired role.
        </h5>
        <br />
        <router-link
          to="/admin_signup"
          class="btn btn-dark"
          style="margin-right: 10px"
          >Signup as Admin</router-link
        >
        <router-link to="/general_signup" class="btn btn-dark"
          >Signup as User</router-link
        >
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Welcome",
};
</script>

<style>
.card {
  width: 100vw;
  max-width: 100%;
}
</style>
