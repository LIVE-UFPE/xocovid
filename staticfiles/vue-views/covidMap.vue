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
                this.mymap = L.map('mapid').setView(this.position, 13.5);

            }, err => {
                console.log(`erro pegando localização: ${err}
                considerando o centro de recife`);
            })
        }
        

        this.mymap = L.map('mapid',{zoomControl: false,}).setView(this.position, 13.5);

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
        let pins_heat = []
        for( var i = 0; i < pinsLen; i++){
            let coord = L.latLng(this.pins[i].latitude, this.pins[i].longitude);
            pins_heat.push(coord)
        }

        // minOpacity - the minimum opacity the heat will start at
        // maxZoom - zoom level where the points reach maximum intensity (as intensity scales with zoom), equals maxZoom of the map by default
        // max - maximum point intensity, 1.0 by default
        // radius - radius of each "point" of the heatmap, 25 by default
        // blur - amount of blur, 15 by default
        // gradient - color gradient config, e.g. {0.4: 'blue', 0.65: 'lime', 1: 'red'}
        this.heatmap = L.heatLayer(pins_heat,{
            gradient: {0.3: 'green', 0.65: 'yellow', 1: 'red'},
            minOpacity: 0.37,
            radius: 25
        });

        this.heatmap.addTo(this.mymap);

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
            // DEBUG lista pro console.log
            let cons_log = 'A seguinte lista de pontos não serão inseridos pois estão fora da data desejada:\nData desejada: ' + this.datedb.toLocaleString('en-GB') + '\n';
            let qtd_pins_excluidos = 0
            let predLen = this.predicts.length;
            // DEBUG se em algum momento eu pego o array de prediçoes
            cons_log += 'predLen: ' + predLen.toString() + '\n';
            let maior_int = 0.0
            let media = 0.0
            let reds = 0
            // * insere array de predições, vazio caso não seja hora de inserir
            if (predLen != [].length) {
                for( var i = 0; i < predLen; i++){
                    pins_heat.push([ this.predicts[i].latitude, this.predicts[i].longitude, this.predicts[i].intensidade ])
                    if(maior_int < this.predicts[i].intensidade) maior_int = this.predicts[i].intensidade;
                    media += this.predicts[i].intensidade
                    if(this.predicts[i].intensidade > 0.75) reds += 1
                }
                cons_log += '\nInserindo pins da IA!\nMaior intensidade: '+ maior_int.toString()+' Média: ' + (media/predLen).toString() +'\nPontos vermelhos: '+ reds.toString()+'\n';
                this.heatmap.setOptions({
                    gradient: {0.25: 'lightgreen',0.5: 'green', 0.75: 'yellow', 1: 'red'},
                    minOpacity: 0,
                    // DEBUG diminuindo raio enquanto não tem normalizado 
                    radius: 25
                });
            }else{
                let pinsLen = this.pins.length;
                let data_notification = new Date();
                // * pega os pins que batem com a data desejada ou antes e joga em pins_heat
                for( var i = 0; i < pinsLen; i++){

                    // TODO think of UTC issue
                    data_notification = new Date(this.pins[i].data_notificacao);
                    // pega somente os pins cuja data antecede a desejada pelo usuario (menor ou igual)
                    if (data_notification <= this.datedb){
                        let coord = L.latLng(this.pins[i].latitude, this.pins[i].longitude);
                        pins_heat.push(coord)
                    }else{
                        cons_log += 'pin com data ' + data_notification.toISOString() + '\n';
                        qtd_pins_excluidos += 1;
                    }
                }
                cons_log += '\nQuantidade de pins não inseridos: ' + qtd_pins_excluidos.toString() + '\n';
                this.heatmap.setOptions({
                    gradient: {0.3: 'green', 0.65: 'yellow', 1: 'red'},
                    minOpacity: 0.37,
                    radius: 25
                });
            }

            this.heatmap.setLatLngs(pins_heat);
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