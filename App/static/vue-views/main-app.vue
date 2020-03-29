<template>
  <!-- <v-app> -->
    <div>
      <!-- // TODO responsividade! -->
      <p>teste consciente</p>
    </div>
  <!-- </v-app> -->
</template>

<script>
module.exports = {
  name: 'main-app',
}
</script>

<style scoped>
#app {
  font-family: Barlow, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

.round-border {
  border-radius: 5% !important;
}
</style>