<template>
    <div id="mapid">

        
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
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        pins: Array,
        datedb: Date,
        predicts: Array,
    },
    mounted: function (){
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
        

        this.mymap = L.map('mapid',{zoomControl: false,zoom: 4}).setView(this.position, 14);

        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            // DEBUG com 15 de zoom os pontos da predição já se agrupam
            maxZoom: 18,
            id: 'mapbox/streets-v11',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw',
        }).addTo(this.mymap);


        let pinsLen = this.pins.length;
        let pins_heat = [];
        for( var i = 0; i < pinsLen; i++){
            pins_heat.push({
                'lat': this.pins[i].latitude,
                'lng': this.pins[i].longitude,
                'intensidade': 0.35,
            })
        }

        this.heatmap = new HeatmapOverlay({
            gradient: {
                '.3': 'green',
                '.65': 'yellow',
                '1': 'red',
            },
            //? raio em pixels (na proporção 1/2 pixel/metro)
            'radius': 50,
            'scaleRadius': false,
            latField: 'lat',
            lngField: 'lng',
            valueField: 'intensidade',
            "useLocalExtrema": false,
        });

        this.heatmap.addTo(this.mymap);

        this.heatmap.setData({
            max: 1,
            min: 0,
            data: pins_heat,
        });

        console.log(`adicionando um total de ${pinsLen} no mapa`)
    },
    computed: {
        // * abreviado de datewatch: function (){}
        datewatch() {
            return this.datedb;
        },
    },
    watch: {
        // ? mudar o array de entrada do heatmap de acordo com o botão pressionado em home.html
        // * abreviado de datewatch: function (){}
        datewatch() {
            let pins_heat = [];
            let config = {};
            // DEBUG lista pro console.log
            let cons_log = 'A seguinte lista de pontos não serão inseridos pois estão fora da data desejada:\nData desejada: ' + this.datedb.toLocaleString('en-GB') + '\n';
            let qtd_pins_excluidos = 0
            let predLen = this.predicts.length;
            // DEBUG se em algum momento eu pego o array de prediçoes
            cons_log += 'predLen: ' + predLen.toString() + '\n';
            let maior_int = 0.0
            let menor_int = 0.0
            let media = 0.0
            
            // * insere array de predições, vazio caso não seja hora de inserir
            if (predLen != [].length) {
                // ? datedb tem horário 23:59:58
                let data = new Date();
                let data_intensidade = '';
                data.setHours(23,59,59);
                data.setDate( data.getDate() + 1 );
                if( this.datedb < data ){
                    data_intensidade = '1';
                }else{
                    data.setDate( data.getDate() + 1 );

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
                cons_log += '\nInserindo pins da IA!\nMaior intensidade: '+ maior_int.toString()+' Média: ' + (media/predLen).toString() +'\nIntensidade: '+data_intensidade+'\n';
                config = {
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
                    'radius': 50,
                    'scaleRadius': false,
                    latField: 'lat',
                    lngField: 'lng',
                    valueField: 'intensidade',
                    "useLocalExtrema": false,
                    'minOpacity': 0,
                    'maxOpacity': .8,
                    'blur': 0.85,

                };
            }else{
                let pinsLen = this.pins.length;
                let data_notification = new Date();
                // * pega os pins que batem com a data desejada ou antes e joga em pins_heat
                for( var i = 0; i < pinsLen; i++){

                    // TODO think of UTC issue
                    data_notification = new Date(this.pins[i].data_notificacao);
                    // pega somente os pins cuja data antecede a desejada pelo usuario (menor ou igual)
                    if (data_notification <= this.datedb){
                        pins_heat.push({
                            'lat': this.pins[i].latitude,
                            'lng': this.pins[i].longitude,
                            'intensidade': 0.35,
                        })
                    }else{
                        cons_log += 'pin com data ' + data_notification.toISOString() + '\n';
                        qtd_pins_excluidos += 1;
                    }
                }
                cons_log += '\nQuantidade de pins não inseridos: ' + qtd_pins_excluidos.toString() + '\n';
                config = {
                    gradient: {
                        '.3': 'green',
                        '.65': 'yellow',
                        '1': 'red',
                    },
                    //? raio em pixels (na proporção 1/2 pixel/metro)
                    'radius': 50,
                    'scaleRadius': false,
                    latField: 'lat',
                    lngField: 'lng',
                    valueField: 'intensidade',
                    "useLocalExtrema": false,
                };
            }

            this.heatmap.reconfigure(config)
            this.heatmap.setData({
                max: maior_int == 0.0 ? 1 : maior_int,
                min: menor_int,
                data: pins_heat
            });
            console.log(cons_log)
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