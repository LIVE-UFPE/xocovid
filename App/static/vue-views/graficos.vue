<template>
    <v-container fluid fill-height>
        <v-app-bar
            color="#1E9CF8"
            dense
            dark
            flat
            absolute
            style="z-index: 1"
        >
            <v-app-bar-nav-icon></v-app-bar-nav-icon>
            
            <v-toolbar-title>XÔ COVID</v-toolbar-title>

            <v-spacer></v-spacer>

            <v-menu left bottom >

            <template v-slot:activator="{ on }">
                <v-btn icon v-on="on">
                <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
            </template>

            <v-list>
                <v-list-item
                v-for="n in 5"
                :key="n"
                @click="load_option(n)"
                >
                <v-list-item-title>Option [[n]]</v-list-item-title>
                </v-list-item>

                <!-- TELA GRAFICOS //TODO melhorar o path aqui -->
                <v-list-item
                href="home">
                <v-list-item-title>Home</v-list-item-title>
                </v-list-item>
            </v-list>
            </v-menu>
            <v-btn href="logout" class="ma-2" text icon color="blue lighten-5">
            <v-icon>cancel</v-icon>
            </v-btn>
        </v-app-bar>

        <v-row fluid fill-height class="d-block ">
            <p class="text-center">Logo</p>

            <v-card raised width="80%" class="accent" >

            </v-card>
        </v-row>
    </v-container>
</template>

<script>
module.exports = {
    name: 'graficos-vue'
}
</script>

<style scoped>

</style>