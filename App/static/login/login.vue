<template>
    
    <!-- // TODO resolve validation-->
    <v-container fluid class="d-flex pa-0 ma-0" fill-height>
        <v-text-field 
            required 
            placeholder="Email"
            v-model="email"
            outlined 
            full-width
            height="100px" 
            single-line solo
        ></v-text-field> 
        <!-- // TODO detail more -->

        <v-text-field
            required 
            placeholder="Senha"
            v-model="password"
            outlined 
            full-width
            type="password"
            height="100px" 
            single-line solo
        ></v-text-field> 


        <v-btn
            color="primary"
            class="mt-8 mb-0"
            @click="submit"
            height="100px"
            width="100%"
        >

            <input type="submit" name="" value="Entrar">
            <!-- // TODO fix alignment -->
        </v-btn>
        
        <v-btn text class="mt-7 sub-botao d-block" width="100%" >Cadastrar</v-btn>
        <v-btn text class="mt-6 sub-botao d-block" width="100%" >Esqueci minha senha</v-btn>
    </v-container>
                
</template>

<script>
// ! componentes devem ser exportados dessa forma, para que o httpVueLoader funcione

module.exports = {
  name: 'login',
  methods: {
      submit () {
          console.log(`email é ${this.email} e senha ${this.password}`)
      },
  },
  data: () => ({
      email: null,
      password: null,
  }),
}
</script>

<style scoped>
.v-text-field, .v-btn {
    font-size: 30px;
    border-radius: 10px;
}

.sub-botao{
    font-size: 25px;
    font-weight: lighter;
    text-transform: none;
    letter-spacing: normal;
}

#top {
  font-family: Barlow, Helvetica, Arial, sans-serif;
  text-align: center;
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
  border-radius: 23px !important;
}
</style>