<template>
  <div class="text-center">
    <v-dialog
      v-model="dialog"
      width="500"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-app-bar-nav-icon v-bind="attrs" v-on="on">
            <v-icon>mdi-information-outline</v-icon>
        </v-app-bar-nav-icon>
      </template>

      <v-card>
        <v-card-title
          class="headline lighten-2"
          primary-title
        >
          <h1 style="#1E9CF8; font-size: x-large;font-family: Barlow; font-weight: 900">{{ $t("dialog.titulo") }}</h1>
        </v-card-title>
        
        <v-card-text class="mt2">
            <br/>
          <p>{{ $t("dialog.conteudo") }}<a href="mailto:contatosgis@live.cin.ufpe.br">contatosgis@live.cin.ufpe.br</a></p>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="dialog = false"
          >
            {{ $t("dialog.fechar") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>
<script>
module.exports ={
    name: 'about-dialog',
    data: function (){
        return{
            
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        dialog: Boolean
    },
    methods: {
    
    }
}
</script>