<template>
  <!-- <v-app> -->
    <v-content>
      <!-- // TODO responsividade! -->
      <p>teste consciente</p>
    </v-content>
  <!-- </v-app> -->
</template>

<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'main-app',
}
</script>

<!-- 
// ! Rules of thumb!
// * Components serao feitos apenas se for necessaria a replicabilidade
// * (exemplo, um item de uma lista de itens)

// * Páginas únicas e pouco mutáveis não precisam ser completamente separadas
// * em componentes

// ! Criando todos os componentes a 1920x1080
// ! Sem foco na responsividade, pois a prioridade é estar integrado ao back-end

// TODO App.vue ter um AppBar global, que se esconde quando necessário???
-->

<style>
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