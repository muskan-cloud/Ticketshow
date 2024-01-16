import { createStore } from "vuex";

export default createStore({
  state: {
    currentUser: null,
    currentUserId: null,
    currentUserEmail: null,
    currentUsername: null,
    currentUserRoles: [],
    theaters: [],
  },
  mutations: {
    setCurrentUser(state, user) {
      state.currentUser = user;
      state.currentUserEmail = user.email;
      state.currentUserId = user.id;
      state.currentUsername = user.username;
      state.currentUserRoles = user.roles;
    },
    settheaters(state, theaters) {
      state.theaters = theaters;
    },
  },
});
