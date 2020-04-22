<template>
    <div id="mapid">
        <v-snackbar v-model="snackbar" top >
            {{ txtsnack }}
            <v-btn text color="white" @click="snackbar = false" >Ok</v-btn>
        </v-snackbar>        
    </div>
</template>

<script>
module.exports = {
    name: 'covid-map',
    data: function (){
        return{
            mymap: null,
            circle: null,
            polygon: null,
            position: L.latLng(-8.046, -34.927),
            heatmap: null,
            txtsnack: 'Oi',
            snackbar: false,
            pins: [],
            request: null
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        datedb: Date,
        predicts: Array,
    },
    methods: {
        getpins(){
            console.log(`datedb é ${this.datedb.toISOString()}`)
            if (this.request != null) {
                this.request.abort();
                // console.log('cancelando requisição anterior')
            }
            this.request = $.ajax({
                context: this,
                type: 'GET',
                url: "get/ajax/pins",
                // TODO ajeitar async call
                data: {"day": this.datedb.toISOString().substring(0,10)},
                success: function (response) {
                    // seta pins
                    this.request = null
                    this.pins = response
                    // console.log('acabei AGORA os pins')
                    // console.log(this.pins)
                    let pinsLen = this.pins.length;
                    let pins_heat = [];
                    let maior_int = 0.0
                    let menor_int = 0.0

                    for( var i = 0; i < pinsLen; i++){
                        pins_heat.push({
                        'lat': this.pins[i].latitude,
                        'lng': this.pins[i].longitude,
                        'intensidade': this.pins[i].intensidade,
                        })
                        if(maior_int < this.pins[i].intensidade) maior_int = this.pins[i].intensidade;
                        if(menor_int > this.pins[i].intensidade) menor_int = this.pins[i].intensidade;
                    }
                    this.heatmap.reconfigure({
                        gradient: {
                            '.3': 'green',
                            '.65': 'yellow',
                            '1': 'red',
                        },
                        //? raio em pixels (na proporção 1/2 pixel/metro)
                        // TODO ajustar raio e formula de raio em todo canto
                        'radius': this.radius,
                        'scaleRadius': false,
                        latField: 'lat',
                        lngField: 'lng',
                        valueField: 'intensidade',
                        "useLocalExtrema": false,
                        'maxOpacity': .7,
                    })
                    this.heatmap.setData({
                        max: maior_int,
                        min: 0,
                        data: pins_heat,
                    });

                    console.log(`adicionando um total de ${pinsLen} no mapa`)
                    
                    this.txtsnack = "Mapa de calor atualizado!"
                    this.snackbar = true
                },
                error: function (response) {
                    console.log("erro na requisição atual, ou ela foi cancelada")
                }
            })
        }
    },
    mounted() {

        // TODO resolve location
        if(!("geolocation" in navigator)){
            console.log('fazer oq qd n tem localizaçao??');
            //TODO fazer isso aq, agr é o centro de recife
            this.position = L.latLng(-8.046, -34.927);
        }else{
            // get position, runs asyncly
            navigator.geolocation.getCurrentPosition(pos => {
                console.log(`lat é ${pos.coords.latitude} e long ${pos.coords.longitude}`)
                this.position = L.latLng(pos.coords.latitude,pos.coords.longitude);
                try{
                    this.mymap = L.map('mapid').setView(this.position, 13);
                } catch(e){
                    this.mymap.setView(this.position,13);
                }
                

            }, err => {
                console.log(`erro pegando localização: ${err}
                considerando o centro de recife`);
            })
        }
        

        this.mymap = L.map('mapid',{zoomControl: false}).setView(this.position, 14);

        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            // DEBUG 12 de zoom minimo p mostrar so a regiao metropolitana de Recife
            maxZoom: 18,
            minZoom: 9,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw',
        }).addTo(this.mymap);

        this.getpins()
        this.txtsnack = 'Carregando pontos...'
        this.snackbar = true

        this.heatmap = new HeatmapOverlay({
            gradient: {
                '.3': 'green',
                '.65': 'yellow',
                '1': 'red',
            },
            //? raio em pixels (na proporção 1/2 pixel/metro)
            // TODO ajustar raio e formula de raio em todo canto
            'radius': this.radius,
            'scaleRadius': false,
            latField: 'lat',
            lngField: 'lng',
            valueField: 'intensidade',
            "useLocalExtrema": false,
            'maxOpacity': .7,

        });

        this.heatmap.addTo(this.mymap);

        this.mymap.on('zoomend', function(ev) {
            if ( ev.target._zoom >= 14 ) {
                let config = {
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
                    'radius': 25,
                    'scaleRadius': false,
                    latField: 'lat',
                    lngField: 'lng',
                    valueField: 'intensidade',
                    "useLocalExtrema": false,
                    'minOpacity': 0,
                    'maxOpacity': .7,
                    'blur': 0.85,
                };
                console.log('mudando raio para '+ config.radius.toString()+'\n');
                // console.log(ev.target);
                let id = 0
                while(true){
                    try {
                        ev.target._layers[id].reconfigure(config);
                        break;
                    } catch (error) {
                        id++
                    }
                }
                // ev.target._layers[48].reconfigure(config);
                // this.heatmap.reconfigure(config);
                return;
            }else{ 
                let config = {
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
                    'radius': Math.floor( 25 / ( Math.pow(2,14 - ev.target._zoom) ) ),
                    'scaleRadius': false,
                    latField: 'lat',
                    lngField: 'lng',
                    valueField: 'intensidade',
                    "useLocalExtrema": false,
                    'minOpacity': 0,
                    'maxOpacity': .7,
                    'blur': 0.85,

                };
                console.log('mudando raio para '+ config.radius.toString()+'\n');
                // console.log(ev.target);
                let id = 0
                while(true){
                    try {
                        ev.target._layers[id].reconfigure(config);
                        break;
                    } catch (error) {
                        id++
                    }
                }
                // ev.target._layers[48].reconfigure(config);
                // this.heatmap.reconfigure(config);
                return;
            }
        });

    },
    computed: {
        // * abreviado de datewatch: function (){}
        datewatch() {
            return this.datedb;
        },
        radius() {
            let zum = this.mymap.getZoom();
            if ( zum >= 14 ) return 25;
            else return Math.floor( 25 / ( Math.pow(2,14 - zum) ) );
        }
    },
    watch: {
        // * abreviado de datewatch: function (){}
        datewatch() {
            let pins_heat = [];
            // DEBUG lista pro console.log
            let cons_log = 'A seguinte lista de pontos não serão inseridos pois estão fora da data desejada:\nData desejada: ' + this.datedb.toLocaleString('en-GB') + '\n';
            let qtd_pins_excluidos = 0
            let qtd_pins_inseridos = 0
            let predLen = this.predicts.length;
            // DEBUG se em algum momento eu pego o array de prediçoes
            cons_log += 'predLen: ' + predLen.toString() + '\n';
            let maior_int = 0.0
            let menor_int = 0.0
            let media = 0.0
            
            // * insere array de predições, vazio caso não seja hora de inserir
            if (predLen != [].length) {
                // ? datedb tem horário 23:59:58

                let data = new Date(this.lastInterpol);
                let data_intensidade = '';
                data.setHours(23,59,59);
                data.setDate( data.getDate() + 1 );
                console.log(`datedb é ${this.datedb.toString()} e data ${data.toString()}`);
                if( this.datedb < data ){
                    data_intensidade = '1';
                    this.txtsnack = 'Os dados agora são previstos pela IA';
                    this.snackbar = true;
                }else{
                    data.setDate( data.getDate() + 1 );
                    this.txtsnack = 'Previsões além de um dia podem ter uma flutuação mais significativa';
                    this.snackbar = true;
                    if( this.datedb < data ) data_intensidade = '2'; 
                    else data_intensidade = '3';
                }


                for( var i = 0; i < predLen; i++){
                    pins_heat.push({
                        'lat': this.predicts[i].latitude, 
                        'lng': this.predicts[i].longitude, 
                        'intensidade': (data_intensidade == '1' ? this.predicts[i].intensidade : (data_intensidade == '2' ? this.predicts[i].intensidade2 : this.predicts[i].intensidade3 )),
                    });
                    if(maior_int < this.predicts[i].intensidade) maior_int = this.predicts[i].intensidade;
                    if(menor_int > this.predicts[i].intensidade) menor_int = this.predicts[i].intensidade;
                    media += this.predicts[i].intensidade
                }
                cons_log += '\nInserindo pins da IA!\nMaior intensidade: '+ maior_int.toString()+'\nMédia: ' + (media/predLen).toString() +'\nIntensidade: '+data_intensidade+'\nRaio: '+ this.radius.toString()+'\n';
                this.heatmap.reconfigure({
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
                    //? raio em pixels (na proporção 1/2 pixel/metro)
                    // TODO ajustar raio e formula de raio em todo canto
                    'radius': this.radius,
                    'scaleRadius': false,
                    latField: 'lat',
                    lngField: 'lng',
                    valueField: 'intensidade',
                    "useLocalExtrema": false,
                    'maxOpacity': .7,
                })
                this.heatmap.setData({
                    max: maior_int,
                    min: 0,
                    data: pins_heat
                });
                console.log(cons_log)
            }else{
                this.getpins()
                this.txtsnack = 'Carregando pontos...'
                this.snackbar = true
            }
        }
    }
}
</script>

<style scoped>
#mapid { /* // DEBUG */
    height: 100%;
    z-index: 0;
}
</style>