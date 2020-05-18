<template>
    <div id="mapid">
        <v-snackbar v-model="snackbar" top >
            {{ txtsnack }}
            <v-btn text color="white" @click="snackbar = false" >Ok</v-btn>
        </v-snackbar>
        <!-- <v-card-actions class="float-left" style="z-index: 1"> 
            <p> Dados do: </p>
            <v-radio-group v-model="radioheat">
                <v-radio label="Brasil" value="brasil"></v-radio>
                <v-radio label="Recife" value="recife"></v-radio>
            </v-radio-group>
        </v-card-actions>  -->
    </div>
</template>

<script>
// ! -------------------------  COMENTÁRIOS DO DEV DISPONÍVEIS NO FIM DO CÓDIGO!! -----------------------
const globalRadius = 30

// ! VARIÁVEIS DE OVERRIDE, ALTERE COM CUIDADO

// ignora reajuste do raio e mantem apenas o existente em globalRadius
var overrideRadius = false

// ignora limite do zoom de acordo com a interpolação escolhida e permite zoom máximo/mínimo da API
// TODO tirar esse overrideZoom e limitar o zoom de acordo com a interpolação sendo usada
var overrideZoom = true

// ignora a intensidade recebida e deixa todos os pontos com intensidade máxima, deve ser usado com radius override
// ? não funciona com predições!
var overrideIntensity = false

// ! FIM DAS VARIÁVEIS DE OVERRIDE


// * VARIÁVEIS DE CONTROLE DA API

// número que a computed property "radius" eleva, de acordo com o nível do zoom
var powerPE = 2 // 14 - zoom
var powerBR = 1.7 // zoom - 5


// zoom inicial
var iniZoom = 14 //TODO lembrar que padrão de recife é 14 de zoom, brasil é 5

// * FIM DAS VARIÁVEIS DE CONTROLE DA API


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
            request: null,
            maxintlocal: 0,
            brasilheat: true,
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        datedb: Date,
        predicts: Array,
        predictspe: Array,
        lastinterpol: Date,

        //deve pegar a maior intensidade global do BR e PE
        maiorintbr: Number,
        maiorintpe: Number,

        //? 0 é diário, 1 é global
        maxint: Number,
        radioheat: String,
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
                data: {"day": this.datedb.toISOString().substring(0,10), "brasilheat": this.brasilheat},
                success: function (response) {
                    // seta pins
                    this.request = null
                    this.pins = response
                    let pinsLen = this.pins.length;
                    let pins_heat = [];
                    let maior_int = 0.0
                    let menor_int = 0.0
                    // TODO não precisar iterar de novo aqui
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
                        'radius': this.radius,
                        'scaleRadius': false,
                        latField: 'lat',
                        lngField: 'lng',
                        valueField: 'intensidade',
                        "useLocalExtrema": false,
                        'maxOpacity': .7,
                    })
                    this.maxintlocal = maior_int
                    this.heatmap.setData({
                        max: overrideIntensity ? 0.1 : (this.maxint == 0 ? maior_int : (this.brasilheat ? this.maiorintbr : this.maiorintpe) ),
                        min: 0,
                        data: pins_heat,
                    });

                    console.log(`adicionando um total de ${pinsLen} no mapa`)
                    console.log(`maior intensidade global é ${this.brasilheat ? this.maiorintbr : this.maiorintpe}, a local é de ${maior_int}. menor intensidade local é ${menor_int}`)
                    
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
            // console.log('fazer oq qd n tem localizaçao??');
            //TODO fazer isso aq, agr é o centro de recife
            this.position = L.latLng(-8.046, -34.927);
        }else{
            // get position, runs asyncly
            navigator.geolocation.getCurrentPosition(pos => {
                //console.log(`lat é ${pos.coords.latitude} e long ${pos.coords.longitude}`)
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
        

        this.mymap = L.map('mapid',{zoomControl: false}).setView(this.position, iniZoom);

        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            // TODO alterar maxzoom prum valor onde n se pode ver os pontos
            maxZoom: 18,
            minZoom: overrideZoom ? 1 : 9,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw',
        }).addTo(this.mymap);

        // DEBUG check zoom level
        console.log(`zoom level: ${this.mymap.getZoom()}`)

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
            console.log('zum é '+ this.mymap.getZoom().toString())
            let config = {
                gradient: {
                    '.3': 'green',
                    '.65': 'yellow',
                    '1': 'red',
                },
                'radius': this.radius,
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
            this.heatmap.reconfigure(config);    
        }, this);

    },
    computed: {
        // * abreviado de datewatch: function (){}
        datewatch() {
            return this.datedb;
        },
        radius() {
            let zum = this.mymap.getZoom();
            // ? se não estou usando a interpol do brasil, preciso diminuir o raio conforme me distancio, pra manter a proporção no zoom ao nivel 14
            if (!this.brasilheat){
                if ( zum >= 14 ) return globalRadius;
                else return overrideRadius ? globalRadius : Math.floor( globalRadius / ( Math.pow(powerPE,14 - zum) ) );

            // ? se estou usando a interpol do brasil, preciso aumentar o raio conforme me aproximo pra manter a proporção no zoom ao nivel 5
            }else{
                if ( zum <= 5 ) return globalRadius;
                else return overrideRadius ? globalRadius : Math.floor( globalRadius * ( Math.pow(powerBR,zum - 5) ) );
            }
            
        },
        maxintwatcher() {
            return this.maxint
        },
        radioheatwatcher() {
            return this.radioheat;
        }
    },
    watch: {
        radioheatwatcher() {
            if (this.radioheat == 'brasil') this.brasilheat = true
            else this.brasilheat = false
            this.getpins()
            // DEBUG checando se o radial muda
            console.log(`radioheat mudou para ${this.radioheat} e brasilheat agora é ${this.brasilheat}`)
        },
        maxintwatcher() {

            //diário
            if (this.maxint == 0) {
                this.heatmap.getinstante().setDataMax(this.maxintlocal)
                console.log(`intensidade maxima mudou para ${this.maxintlocal}`)
            }else{
               this.heatmap.getinstante().setDataMax(this.brasilheat ? this.maiorintbr : this.maiorintpe)
               console.log(`intensidade maxima mudou para ${this.brasilheat ? this.maiorintbr : this.maiorintpe}`)
            }
        },
        // * abreviado de datewatch: function (){}
        datewatch() {
            let pins_heat = [];
            // DEBUG lista pro console.log
            let cons_log = 'A seguinte lista de pontos não serão inseridos pois estão fora da data desejada:\nData desejada: ' + this.datedb.toISOString() + '\n';
            let qtd_pins_excluidos = 0
            let qtd_pins_inseridos = 0
            let predLen = this.brasilheat ? this.predicts.length : this.predictspe.length;
            // DEBUG se em algum momento eu pego o array de prediçoes
            cons_log += 'predLen: ' + predLen.toString() + '\n';
            let maior_int = 0.0
            let menor_int = 0.0
            let media = 0.0
            
            // * insere array de predições, vazio caso não seja hora de inserir
            if (predLen != [].length) {
                // ? datedb tem horário 23:59:58

                let data = new Date(this.lastinterpol);
                let data_intensidade = '';
                data.setHours(23,59,59);
                data.setDate( data.getDate() + 1 );
                console.log(`lastinterpol é ${this.lastinterpol} e data ${data.toISOString()}`);
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

                if (this.brasilheat) {
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
                } else {
                    for( var i = 0; i < predLen; i++){
                        pins_heat.push({
                            'lat': this.predictspe[i].latitude, 
                            'lng': this.predictspe[i].longitude, 
                            'intensidade': (data_intensidade == '1' ? this.predictspe[i].intensidade : (data_intensidade == '2' ? this.predictspe[i].intensidade2 : this.predictspe[i].intensidade3 )),
                        });
                        if(maior_int < this.predictspe[i].intensidade) maior_int = this.predictspe[i].intensidade;
                        if(menor_int > this.predictspe[i].intensidade) menor_int = this.predictspe[i].intensidade;
                        media += this.predictspe[i].intensidade
                    } 
                }
                
                cons_log += '\nInserindo pins da IA!\nMaior intensidade: '+ maior_int.toString()+'\nMédia: ' + (media/predLen).toString() +'\nIntensidade: '+data_intensidade+'\nRaio: '+ this.radius.toString()+'\n';
                this.heatmap.reconfigure({
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
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

// ! ---------------------------------- COMENTÁRIOS DO DEV!! --------------------------------------------

// zoom de 5 com raio de 25 torna perceptível a "camada verde" no heatmap
// raio crescendo na taxa globalRadius * 2^(zoom - 5 ) é perceptível até zoom de 13, a partir do momento em que o raio passa de 6000 ele não renderiza o ponto

// dando override na intensidade dos pontos(todos com intensidade maxima) evidencia que eles são sempre visíveis, não importa o nível de zoom. o que faz eles desaparecerem não é o zoom
// acrescentando mais uma cor no gradiente abaixo de ver podemos ver que o sumiço dos pontos se dá ao fato de que o ponto em si tem uma intensidade tão pequena que ele se torna "invisível", a cor que a API dá aos pontos perto de 0%, mas, quando eles começam a "se juntar" conforme aumentamos o raio/tiramos o zoom, a intensidade é combinada e acaba aumentando. por isso a camada verde é visível até um certo ponto, mas some logo após, considerando o limite máximo de 6000 de raio por ponto


// testando usar limite mínimo diferente de zero a fim de ver se os pontos deixam de serem "transparentes", mas teoricamente isso só iria aumentar a quantidade de pontos transparentes
// sem sucesso, a menor intensidade naturalmente é zero!


// de resumo, a camada verde na verdade é um conjunto de pontos com intensidade mínima, que acabam se juntando devido ao nível de zoom, o que é inevitável, pois o raio mínimo é de 1. isso explica porque mesmo aumentando o raio, uma hora os pontos somem também, em conjunto com o raio máximo de 6000
</script>

<style scoped>
#mapid { /* // DEBUG */
    height: 100%;
    z-index: 0;
}
</style>