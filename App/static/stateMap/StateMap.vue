<template>
    <div id="map">
        <v-snackbar v-model="snackbar" top >
            {{ txtsnack }}
            <v-btn text color="white" @click="snackbar = false" >Ok</v-btn>
        </v-snackbar>
    </div>
</template>
<script>
module.exports ={
    name: 'state-map',
    data: function (){
        return{
            menoscasos: 0,
            maiscasos: null,
            request: null,
            casos: [],
            map: null,
            geojson: null,
            style: null,
            txtsnack: 'Oi',
            snackbar: false,
            blockrequest: true
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        datedb: Date,
    },
    methods: {
        // TODO saber ultimo dia que se tem dados, pois não tem a partir de um certo dia
        // TODO snackbar informando
        // TODO informar na legenda que existe cor para ausencia de dados
        getCasos(){
            console.log(`datedb é ${this.datedb.toISOString()}`)
            if (this.request != null) {
                this.request.abort();
            }
            //pede a quantidade de casos confirmados de cada estado do dia
            this.request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'estadosdia', "dia": this.datedb.toISOString().substring(0,10), "estado": '', "cidade": '', "bairro": '',"maiorcaso": false},
                success: function (response) {
                    let resposta = JSON.parse(response)
                    if(resposta.length != 0){
                        this.casos = resposta
                        // console.log(this.casos)
                        console.log(`maiscasos = ${this.maiscasos} idsidhs menoscasos = ${this.menoscasos}`)
                        
                        // console.log(this.ultimoscasos)
                        this.geojson.setStyle(this.style)
                        let legenda = [this.maiscasos,this.menoscasos]
                        this.$emit('dados-legenda',legenda)   
                    }else {
                        // TODO tirar esse else pq nunca vai retornar nada
                        this.txtsnack = 'Não há casos pra esse dia, mantendo os números do último dia com dados'
                        this.snackbar = true
                        // console.log(this.ultimoscasos)
                    }
                    
                }
            })
        },
        getMaiorCaso(){
            this.blockrequest = true
            if (this.request != null) {
                this.request.abort();
            }
            this.request = $.ajax({
                // TODO fix async issue
                async: false,
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'estadosdia', "dia": this.datedb.toISOString().substring(0,10), "estado": '', "cidade": '', "bairro": '',"maiorcaso": true},
                success: function (response) {
                    // let resposta = JSON.parse(response)
                    this.maiscasos = Number(response)
                    console.log(`passando a maior quantidade de casos ${this.maiscasos} tipo é ${typeof(this.maiscasos)}`)
                    
                },
                complete: function (a,b) {
                    this.blockrequest = false
                }
            })
            
        }
    },
    mounted() {
        this.getMaiorCaso()
        var mapboxAccessToken = "pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw";
        var map = L.map('map',{zoomControl: false}).setView([-15.776250, -47.796619], 5);
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
            info.update(layer.feature.properties,this);
        }
        function resetHighlight(e) {
            this.geojson.resetStyle(e.target);
            info.update();
        }
        function zoomToFeature(e) {
            this.map.fitBounds(e.target.getBounds());
        }
        //TODO previousclick nao for num canto valido, resetar?
        let previousClick = null
        function clickHandler(e){
            // console.log('Console: ',e.target)
            if(previousClick){
                resetHighlight.call(this,previousClick)
                highlightFeature.call(this,e)
            }else{
                highlightFeature.call(this,e)
            }
            previousClick = e
        }
        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature.bind(this),
                mouseout: resetHighlight.bind(this),
                // click: zoomToFeature.bind(this),
                click: clickHandler.bind(this)
            });
        }
        
        function getColor(estado,that) {
            if(that.casos.length == 0) return '#800026'
            // DEBUG lista os casos
            // console.log(that.casos)
            let d = that.casos.find( elem => elem['estado_residencia'] === estado)
            //DEBUG se der certo, tirar mais e menoscasos e deixar so a media
            let media = (that.maiscasos + that.menoscasos) / 2
            // TODO limpar esse try catch
            try {
                d = d['quantidade_casos']
            } catch (error) {
                this.txtsnack = `não temos informações sobre ${estado} nesse dia,mantendo ultimos dados obtidos`
                this.snackbar = true
            }
            return d >= Math.floor(media * 1.5) ? '#ff0000' : // * tons de vermelho
                d >= Math.floor(media * 0.75)  ? '#ff2121' :
                d >= Math.floor(media * 0.625)  ? '#ff4040' :
                d >= Math.floor(media * 0.5)  ? '#ff5252' :
                d >= Math.floor(media * 0.375)   ? '#ff8080' :
                d >= Math.floor(media * 0.25)   ? '#ff9696' :
                d >= Math.floor(media * 0.125)   ? '#ffa8a8' : // * tons de amarelo
                d >= Math.floor(media * 0.03125)   ? '#ffc2c2' : // * AMARELO MEMSO TUDO AMARELO NISSO AQ
                    '#e6e6e6'
        }
        function style(feature) {
            return {
                fillColor: getColor(feature.properties.name,this),
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7
            };
        }
        var info = L.control();
        info.setPosition('topleft')

        info.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
            this.update();
            return this._div;
        };
        // method that we will use to update the control based on feature properties passed
        info.update = function (props, that) {
            let casos = 0
            let obitos = 0
            let casos_diarios = 0,obitos_diarios = 0,dados_dia = false
            if (props) {
                try {
                    let test = that.casos.find( elem => elem['estado_residencia'] === props.name)
                    casos = test['quantidade_casos']
                    obitos = test['obitos']
                    casos_diarios = test['quantidade_casos_diarios']
                    obitos_diarios = test['quantidade_obitos_diarios']
                    dados_dia = test['dados_dia_requisitado']
                } catch (error) {
                    console.log(`sem dados para ${props.name}`)
                }    
            }
            this._div.innerHTML = '<h4 class="text-center" >Número de casos confirmados</h4>' +  (props ?
                `<div style="display:flex; justify-content: center; align-items: center; flex-direction: column">
                    <h2 class="text-center" style="padding-top: 10px;color: white; font-family: Barlow, sans-serif;font-weight: 900">`
                        + props.name + 
                    `</h2>
                    <br /> 
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + casos + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos acumulados
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + obitos + 
                            `</h1>
                            <h4  class="text-center" style="padding-top: 25px;color: white">
                                Óbitos acumulados
                            </h4>
                        </div> 
                    </div>
                    <br />
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + casos_diarios + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos diários
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + obitos_diarios + 
                            `</h1>
                            <h4  class="text-center" style="padding-top: 25px;color: white">
                                Óbitos diários
                            </h4>
                        </div> 
                    </div>
                    ` + (!dados_dia ? `<br /><h5 class="text-center" style="color: white" >Os dados exibidos não são do dia desejado</h5>` : ``) + `
                </div>`
                : '<h5 style="color: white" class="text-center">Passe o mouse por um estado</h5>');
        };
        info.addTo(map);
        L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=' + mapboxAccessToken, {
            id: 'mapbox/light-v9',
            tileSize: 512,
            zoomOffset: -1,
            accessToken: 'pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw',
        }).addTo(map);
        this.style = style.bind(this)
        this.geojson = L.geoJson(statesData, {style: this.style, onEachFeature: onEachFeature.bind(this)})
        this.geojson.addTo(map)
        this.map = map
        this.getCasos()
    },
    computed: {
        datewatch() {
            return this.datedb;
        },
    },
    watch: {
        datewatch() {
            this.getCasos()
        }
    },
    
}
</script>

<style scoped>
#map { /* // DEBUG */
    height: 100%;
    width: 100%;
    z-index: 0;
}

.info {
    /* align-self: center; */
    /* margin: auto; */
    padding: 6px 8px;
    font: 14px/16px Arial, Helvetica, sans-serif;
    background: white;
    background: rgba(255,255,255,0.8);
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
    border-radius: 5px;
    
    z-index: 1;

}
@media (max-width: 600px) {
    .info {
        top: 5px;
    }
}
@media (min-width: 601px) {
    .info {
        left: 10vmin;
        top: 10px;
    }
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