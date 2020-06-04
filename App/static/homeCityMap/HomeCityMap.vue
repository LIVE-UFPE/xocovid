<template>
    <div :key="componentKey" style="border-radius: 25px" id="mapcity">
        <v-snackbar v-model="snackbar" top >
            {{ txtsnack }}
            <v-btn text color="white" @click="snackbar = false" >Ok</v-btn>
        </v-snackbar>
    </div>
</template>
<script>
module.exports ={
    name: 'home-city-map',
    data: function (){
        return{
            request: null,
            componentKey: 0,
            casos: [],
            ultimoscasos: [],
            txtsnack: '',
            snackbar: false,
            geojson: null,
            style: null,
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        estado: String,
        datedb: Date,
    },
    methods: {
        forceRerender() {
          this.componentKey += 1
        },
        getCasos(estado){
            if (this.request != null) {
                this.request.abort();
            }
            this.request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                // TODO rodar a busca no views.py
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'cidadesdia', "dia": this.datedb.toISOString().substring(0,10), "estado": estado, "cidade": '', "bairro": ''},
                success: function (response) {
                    let resposta = JSON.parse(response)
                    if(resposta.length != 0){
                        this.casos = resposta
                        // console.log('Casos: ',this.casos)
                        this.casos.forEach(element => {
                            this.ultimoscasos[element['municipio']] = element
                        });
                        this.geojson.setStyle(this.style)
                    }else {
                        this.txtsnack = 'Não há casos pra esse dia, mantendo os números do último dia com dados'
                        this.snackbar = true
                        // console.log(this.ultimoscasos)
                    }
                }
            })
            
        }
    },
    mounted() {
        // console.log(this.estado.split(' ').join('_'))
        this.estado = this.estado.slice(0,this.estado.length-5).split(' ').join('_')
        this.getCasos(this.estado)
        var objectCoord = {lat: [], lon: []}
        objectCoord.lat.push(eval(this.estado).features[0].geometry.coordinates[0][0][0])
        objectCoord.lon.push(eval(this.estado).features[0].geometry.coordinates[0][0][1])
        var mapboxAccessToken = "pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw";
        var map = L.map('mapcity').setView([parseFloat(objectCoord.lon), parseFloat(objectCoord.lat)], 6);
        // var geojson;
        var estadoLocal = this.estado
        this.geojson = L.geoJson(eval(this.estado), {style: style});
        
        function samDash(estado, cidade){
            buscaResponse = []
            // console.log('Object: ',buscaResponse, estadoLocal, cidade)
            var request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'cidades2', "estado": estadoLocal, "cidade": cidade, "bairro": ''},
                async: false,
                success: function (response) {
                    buscaResponse = JSON.parse(response)
                }
            })
            
            if(buscaResponse.length == 0){
                 return 0
            }else{
                 return buscaResponse[buscaResponse.length-1]['quantidade_casos']
            }
        }
        function samDashObitos(estado, cidade){
            buscaResponse = []
            
            var request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Óbitos', "keyBusca": 'cidades2', "estado": estadoLocal, "cidade": cidade, "bairro": ''},
                async: false,
                success: function (response) {
                    buscaResponse = JSON.parse(response)
                }
            })
            
            if(buscaResponse.length == 0){
                 return 0
            }else{
                 return buscaResponse[buscaResponse.length-1]['quantidade_casos']
            }
        }
        function highlightFeature(e) {
            var layer = e.target;
            layer.setStyle({
                weight: 5,
                color: '#1E9CF8',
                dashArray: '',
                fillOpacity: 0.7
            });
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                layer.bringToFront();
            }
            info.update(layer.feature.properties, this);
        }
        function resetHighlight(e) {
            this.geojson.resetStyle(e.target);
            info.update();
        }
        function zoomToFeature(e) {
            map.fitBounds(e.target.getBounds());
        }
        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature.bind(this),
                mouseout: resetHighlight.bind(this),
                click: zoomToFeature.bind(this),
            });
        }
        function getColor(d, media) {
            return d >= Math.floor(media * 0.875) ? '#ff0000' : // * tons de vermelho
                d >= Math.floor(media * 0.75)  ? '#ff4242' :
                d >= Math.floor(media * 0.625)  ? '#ff6e6e' :
                d >= Math.floor(media * 0.5)  ? '#ff8a8a' :
                d >= Math.floor(media * 0.375)   ? '#ffabab' :
                d >= Math.floor(media * 0.25)   ? '#ffbaba' :
                d >= Math.floor(media * 0.125)   ? '#ffd000' : // * tons de amarelo
                d >= Math.floor(media * 0.03125)   ? '#ffe054' : // * AMARELO MEMSO TUDO AMARELO NISSO AQ
                    '#38ff26'
        }
        function style(feature) {
            var casoLocal = 0
            var menor = 0
            var maior = 0
            var i = 0
            // console.log("Feature: ",this.casos)
            if(this.casos){
                this.casos.forEach(caso => {
                    if(!i){
                        maior = caso.quantidade_casos
                        menor = caso.quantidade_casos
                        i++
                    }
                    if(caso.quantidade_casos > maior)
                        maior = caso.quantidade_casos
                    if(caso.quantidade_casos < menor)
                        menor = caso.quantidade_casos
                    if(caso.municipio == feature.properties.NOME){
                        casoLocal = caso.quantidade_casos
                    }
                })
                // console.log('Casos Locais: ', casoLocal)
            }
            return {
                fillColor: getColor(casoLocal, (menor+maior)/2),
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7
            };
        }
        var info = L.control();
        
        info.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
            this.update();
            return this._div;
        };
        // console.log('ESTADO: ', this.estado)
        // method that we will use to update the control based on feature properties passed
        info.update = function (props, that) {
            let casos = 0
            let obitos = 0
            
            if (props) {
                try {
                    // console.log(props.NOME)
                    let test = that.casos.find( elem => elem['municipio'] === props.NOME)
                    casos = test['quantidade_casos']
                    obitos = test['obitos']
                } catch (error) {
                    // console.log('sem dados')
                    try {
                        casos = that.ultimoscasos[props.NOME]['quantidade_casos']
                        obitos = that.ultimoscasos[props.NOME]['obitos']
                    } catch (err) {
                        casos = 0
                        obitos = 0
                        // console.log('também não há dados anteriores para este municipio')
                    }
                        
                }    
            }
            this._div.innerHTML = (props ?
                `<div style="display:flex; justify-content: center; align-items: center; flex-direction: column">
                    <h2 class="text-center" style="padding-top: 10px;color: white; font-family: Barlow, sans-serif;font-weight: 900">`
                        + props.NOME + 
                    `</h2>
                    <br /> 
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + casos + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos confirmados
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + obitos + 
                            `</h1>
                            <h4  class="text-center" style="padding-top: 25px;color: white">
                                Óbitos confirmados
                            </h4>
                        </div> 
                    </div>
                    </div>`
                : 
                `<h5 style="color: white" class="text-center">
                    Passe o mouse por uma cidade
                </h5>`);
        };
        info.addTo(map);
        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=' + mapboxAccessToken, {
            id: 'mapbox/light-v9',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw',
        }).addTo(map);
        this.style = style.bind(this)    
        this.geojson = L.geoJson(eval(this.estado), {style: this.style, onEachFeature: onEachFeature.bind(this)}).addTo(map);
        this.geojson.addTo(map)
        this.map = map
        this.getCasos(this.estado)
    },
    computed: {
        datewatch() {
            return this.datedb;
        },
        estadoComp() {
            return this.estado.slice(0,this.estado.length-5).split(' ').join('_')
        }
    },
    watch: {
        datewatch() {
            
            this.getCasos(this.estadoComp)
        }
    }
    
}
</script>

<style scoped>
#mapcity { /* // DEBUG */
    height: 100%;
    width: 100%;
    z-index: 0;
}
.info {
    padding: 6px 8px;
    font: 14px/16px Arial, Helvetica, sans-serif;
    background: white;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
    border-radius: 5px;
    right: 84vmin;
    top: 10px;
}
.info h4 {
    margin: 0 0 5px;
    color: rgb(255, 255, 255);
}
.info b {
    margin: 0 0 5px;
    color: rgb(206, 206, 206);
    font-weight: 900;
    font-size:large;
}
.info .leaflet-control {
    background-color: #777;
}
.leaflet-control-zoom{
    margin-left: 80px;
    position:absolute;
    margin-top: 80px
}
/* .leaflet-control-container{
     margin-left: 200px;
} */
</style>