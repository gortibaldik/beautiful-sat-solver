<template>
  <div class="flexible-content">
    <!-- Sidebar -->
    <div class="sidebar-fixed position-fixed">
      <a class="logo-wrapper"
        ><img alt="" class="img-fluid" src="./assets/logo-mdb-vue-small.png"
      /></a>
      <mdb-list-group class="list-group-flush">
        <router-link to="/benchmarks" @click.native="activeItem = 1">
          <mdb-list-group-item
            :action="true"
            :class="activeItem === 1 && 'active'"
            ><mdb-icon
              icon="clipboard-list"
              class="mr-3"
            />Benchmarks</mdb-list-group-item
          >
        </router-link>
        <router-link to="/results" @click.native="activeItem = 2">
          <mdb-list-group-item
            :action="true"
            :class="activeItem === 2 && 'active'"
            ><mdb-icon
              icon="clipboard-list"
              class="mr-3"
            />Results</mdb-list-group-item
          >
        </router-link>
        <router-link to="/404" @click.native="activeItem = 5">
          <mdb-list-group-item
            :action="true"
            :class="activeItem === 5 && 'active'"
            ><mdb-icon
              icon="exclamation"
              class="mr-3"
            />404</mdb-list-group-item
          >
        </router-link>
      </mdb-list-group>
    </div>
    <!-- /Sidebar  -->
    <main>
      <div class="mt-5 p-5">
        <router-view></router-view>
      </div>
      <ftr color="primary-color-dark" class="text-center font-small darken-2">
        <p class="footer-copyright mb-0 py-3 text-center">
          &copy; {{ new Date().getFullYear() }} Copyright:
          <a href="https://github.com/gortibaldik/"> gortibaldik </a>
        </p>
      </ftr>
    </main>
  </div>
</template>

<script>
import {
  mdbIcon,
  mdbListGroup,
  mdbListGroupItem,
  mdbFooter,
  waves
} from "mdbvue";

export default {
  name: "AdminTemplate",
  components: {
    mdbListGroup,
    mdbListGroupItem,
    mdbIcon,
    ftr: mdbFooter
  },
  data() {
    return {
      activeItem: 1
    };
  },
  beforeMount() {
    this.activeItem = this.$route.matched[0].props.default.page;
  },
  mixins: [waves]
};
</script>

<style>
@import url("https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap");
.navbar-light .navbar-brand {
  margin-left: 15px;
  color: #2196f3 !important;
  font-weight: bolder;
}
</style>

<style scoped>
main {
  margin-top: -0%;
  background-color: #ededee;
}

.flexible-content {
  transition: padding-left 0.3s;
  padding-left: 270px;
  margin-top: -50px;
}

.flexible-navbar {
  transition: padding-left 0.5s;
  padding-left: 270px;
}

.sidebar-fixed {
  left: 0;
  top: 0;
  height: 100vh;
  width: 270px;
  box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.16), 0 2px 10px 0 rgba(0, 0, 0, 0.12);
  z-index: 1050;
  background-color: #fff;
  padding: 1.5rem;
  padding-top: 0;
}

.sidebar-fixed .logo-wrapper img {
  width: 100%;
  padding: 2.5rem;
}

.sidebar-fixed .list-group-item {
  display: block !important;
  transition: background-color 0.3s;
}

.sidebar-fixed .list-group .active {
  box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.16), 0 2px 10px 0 rgba(0, 0, 0, 0.12);
  border-radius: 5px;
}

@media (max-width: 1199.98px) {
  .sidebar-fixed {
    display: none;
  }
  .flexible-content {
    padding-left: 0;
  }
  .flexible-navbar {
    padding-left: 10px;
  }
}
</style>
