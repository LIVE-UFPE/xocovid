<template>
    <div :key="componentKey" style="border-radius: 0px" id="mapcity">
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
            maiscasos: 0,
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
            this.txtsnack = "Coletando dados..."
            this.snackbar = true
            if (this.request != null) {
                this.request.abort();
            }
            this.request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                // TODO rodar a busca no views.py
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'cidadesdia', "dia": this.datedb.toISOString().substring(0,10), "estado": estado, "cidade": '', "bairro": '',"maiorcaso": false},
                success: function (response) {
                    let resposta = JSON.parse(response)
                    if(resposta.length != 0){
                        this.casos = resposta
                        // console.log('Casos: ',this.casos)

                        this.geojson.setStyle(this.style)
                        let legenda = [this.maiscasos,0]
                        this.$emit('dados-legenda',legenda) 
                    }else {
                        this.txtsnack = 'Não há casos pra esse dia, mantendo os números do último dia com dados'
                        this.snackbar = true
                        // console.log(this.ultimoscasos)
                    }
                }
            })
        },
        getMaiorCaso(estado){
            if (this.request != null) {
                this.request.abort();
            }
            this.request = $.ajax({
                // TODO fix async issue
                async: false,
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'cidadesdia', "dia": this.datedb.toISOString().substring(0,10), "estado": estado, "cidade": '', "bairro": '',"maiorcaso": true},
                success: function (response) {
                    // let resposta = JSON.parse(response)
                    this.maiscasos = Number(response)
                    console.log(`passando a maior quantidade de casos ${this.maiscasos} tipo é ${typeof(this.maiscasos)}`)
                    
                },
            })  
        },
        levenshtein(a,b){
            if(a.length == 0) return b.length; 
            if(b.length == 0) return a.length; 

            var matrix = [];

            // increment along the first column of each row
            var i;
            for(i = 0; i <= b.length; i++){
                matrix[i] = [i];
            }

            // increment each column in the first row
            var j;
            for(j = 0; j <= a.length; j++){
                matrix[0][j] = j;
            }

            // Fill in the rest of the matrix
            for(i = 1; i <= b.length; i++){
                for(j = 1; j <= a.length; j++){
                    if(b.charAt(i-1) == a.charAt(j-1)){
                        matrix[i][j] = matrix[i-1][j-1];
                    } else {
                        matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                                                Math.min(matrix[i][j-1] + 1, // insertion
                                                        matrix[i-1][j] + 1)); // deletion
                    }
                }
            }

            return matrix[b.length][a.length];
        }
    },
    mounted() {
        this.getMaiorCaso(this.estadoComp)
        var objectCoord = {lat: [], lon: []}
        objectCoord.lat.push(eval(this.estadoComp).features[0].geometry.coordinates[0][0][0])
        objectCoord.lon.push(eval(this.estadoComp).features[0].geometry.coordinates[0][0][1])
        //resposta = this.get_shapefile(this.estado)
        //objectCoord.lat.push(resposta[0].data.features[0].geometry.coordinates[0][0][0])
        //objectCoord.lon.push(resposta[0].data.features[0].geometry.coordinates[0][0][1])
        var mapboxAccessToken = "pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw";
        var map = L.map('mapcity',{zoomControl: false}).setView([parseFloat(objectCoord.lon), parseFloat(objectCoord.lat)], 6);
        // var geojson;
        var estadoLocal = this.estadoComp

        // this.geojson = L.geoJson(eval(this.estado), {style: style});

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
        // TODO encontrar motivo de Acaraú, no Ceará, nao dar uma cor, pois atualmente NENHUMA ALTERAÇÃO FEITA AQUI MUDA NO SITE
        function getColor(municipio, that) {
            if(that.casos.length == 0) return '#800026'

            // DEBUG
            // let test = that.casos.filter(elem => that.levenshtein(elem['municipio'], municipio) <= 2)
            // if(test.length > 1){
            //     console.log('array test:')
            //     console.log(test)
            // }

            // busque o municipio com nome igual ao do municipio pedido
            let d = that.casos.find( elem => elem['municipio'] == municipio )
            if(d == undefined){
                // busque o municipio com nome mais similar ao municipio pedido, c diferença de 1
                d = that.casos.find( elem => that.levenshtein(elem['municipio'], municipio) <= 1 )    
            }
            // ? será q seria conveniente também ele não pegar municipios que existam, mesmo q passem no levenshtein? p isso, precisaria do JSON c somente o nome dos municipios
            

            if(d == undefined) return '#6a00ff'
            if(d['quantidade_casos'] == -1) return '#6a00ff'
            d = d['quantidade_casos']
            //DEBUG se der certo, tirar mais e menoscasos e deixar so a media
            let media = that.maiscasos / 2
            return d >= Math.floor(media * 1) ? '#ff0000' : // * tons de vermelho
                d >= Math.floor(media * 0.75)  ? '#ff2121' :
                d >= Math.floor(media * 0.625)  ? '#ff4040' :
                d >= Math.floor(media * 0.5)  ? '#ff5252' :
                d >= Math.floor(media * 0.25)   ? '#ff8080' :
                d >= Math.floor(media * 0.125)   ? '#ff9696' :
                d >= Math.floor(media * 0.03125)   ? '#ffa8a8' : // * tons de amarelo
                d >= Math.floor(media * 0.015625)   ? '#ffc2c2' : // * AMARELO MEMSO TUDO AMARELO NISSO AQ
                    '#ffd9d9'
        }
        function style(feature) {
            return {
                fillColor: getColor(feature.properties.NOME, this),
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
            let casos_diarios = 0,obitos_diarios = 0
            
            if (props) {
                try {
                    // console.log(props.NOME)
                    let test = that.casos.find( elem => elem['municipio'] === props.NOME)
                    casos = test['quantidade_casos']
                    if(casos != -1){
                        obitos = test['obitos']
                        casos_diarios = test['quantidade_casos_diarios']
                        obitos_diarios = test['quantidade_obitos_diarios']
                        dados_dia = test['dados_dia_requisitado']
                    }
                    
                } catch (error) {
                    console.log(`sem dados para ${props.NOME}`)
                    casos = -1
                }    
            }

            this._div.innerHTML = (props ?
                `<div style="display:flex; justify-content: center; align-items: center; flex-direction: column;">
                    <h2 class="text-center" style="padding-top: 10px;color: white; font-family: Barlow, sans-serif;font-weight: 900">`
                        + props.NOME + 
                    `</h2>
                    <br /> 
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + (casos != -1 ? casos : `-`) + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos confirmados
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + (casos != -1 ? obitos : `-`) + 
                            `</h1>
                            <h4  class="text-center" style="padding-top: 25px;color: white">
                                Óbitos confirmados
                            </h4>
                        </div> 
                    </div>
                    <br />
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + (casos != -1 ? casos_diarios : `-`) + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos diários
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 5px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + (casos != -1 ? obitos_diarios : `-`) + 
                            `</h1>
                            <h4  class="text-center" style="padding-top: 25px;color: white">
                                Óbitos diários
                            </h4>
                        </div> 
                    </div>
                    ` + (casos == -1 ? `` : (!dados_dia ? `<br /><h5 class="text-center" style="color: white" >Os dados exibidos não são do dia desejado</h5>` : ``)) + `
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
        this.geojson = L.geoJson(eval(this.estadoComp), {style: this.style, onEachFeature: onEachFeature.bind(this)})
        //resposta = this.get_shapefile(this.estado)
        //this.geojson = L.geoJson(resposta[0].data, {style: this.style, onEachFeature: onEachFeature.bind(this)})
        this.geojson.addTo(map)
        this.map = map
        this.getCasos(this.estadoComp)
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
    /* right: 84vmin; */
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