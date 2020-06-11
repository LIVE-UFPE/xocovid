Skip to content
Search or jump to…

Pull requests
Issues
Marketplace
Explore
 
@gabrielsm0405 
LIVE-UFPE
/
xocovid
Private
2
00
 Code
 Issues 0
 Pull requests 0 Actions
 Projects 0
 Wiki
 Security 0
 Insights
 Settings
xocovid/App/static/cityMap/CityMap.vue
@sbjsouza sbjsouza Improved graphs responsivity and fixed MapCity data
28d81d7 1 hour ago
230 lines (222 sloc)  8.23 KB
  
<template>
    <div :key="componentKey" style="border-radius: 0px !important" id="mapcity">

    </div>
</template>
<script>
module.exports ={
    name: 'city-map',
    data: function (){
        return{
            test: null,
            componentKey: 0
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        estado: String
    },
    methods: {
        forceRerender() {
          this.componentKey += 1
        },  
    },
    mounted() {
        console.log(this.estado.split(' ').join('_'))
        this.estado = this.estado.slice(0,this.estado.length-5).split(' ').join('_')
        console.log("Estado: ", this.estado)
        var objectCoord = {lat: [], lon: []}
        objectCoord.lat.push(eval(this.estado).features[0].geometry.coordinates[0][0][0])
        objectCoord.lon.push(eval(this.estado).features[0].geometry.coordinates[0][0][1])
        var mapboxAccessToken = "pk.eyJ1IjoibHVjYXNqb2IiLCJhIjoiY2s4Z2dxbmF1MDFmdjNkbzlrdzR5ajBqbCJ9.HlQrZzNxyOKpsIwn6DmvKw";
        var map = L.map('mapcity').setView([parseFloat(objectCoord.lon), parseFloat(objectCoord.lat)], 6);
        var geojson;
        let estadoGlobal = this.estado
        var buttonStatus = false
        var previousClick = null
        geojson = L.geoJson(eval(this.estado), {style: style});
        
        function samDash(estado, cidade){
            buscaResponse = []
            var request = $.ajax({
                context: this,
                type: 'GET',
                url: "get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'cidades2', "estado": estadoGlobal, "cidade": cidade, "bairro": ''},
                async: false,
                success: function (response) {
                    buscaResponse = JSON.parse(response)
                }
            })
            console.log('response: ', buscaResponse)
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
                url: "get_data",
                data: {"informacao": 'Óbitos', "keyBusca": 'cidades2', "estado": estadoGlobal, "cidade": cidade, "bairro": ''},
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
            info.update(layer.feature.properties);
        }
        function resetHighlight(e) {
            geojson.resetStyle(e.target);
            info.update();
        }
        function zoomToFeature(e) {
            map.fitBounds(e.target.getBounds());
        }
        function clickHandler(e){
            console.log('Console: ',e.target)
            if(previousClick){
                resetHighlight(previousClick)
                highlightFeature(e)  
            }else{
                highlightFeature(e)  
            }
            buttonStatus = !buttonStatus
            previousClick = e
        }
        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
                click: clickHandler
                // click: zoomToFeature
            });
        }
        function getColor(d) {
            return d > 1000 ? '#800026' :
                d > 15  ? '#800026' :
                d > 12  ? '#800026' :
                d > 10  ? '#800026' :
                d > 3   ? '#800026' :
                d > 2   ? '#800026' :
                d > 1   ? '#800026' :
                            '#800026';
        }
        function style(feature) {
            return {
                fillColor: getColor(feature.properties.NOME),
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
        console.log('ESTADO: ', this.estado)
        // method that we will use to update the control based on feature properties passed
        info.update = function (props) {
            this._div.innerHTML = (props ?
                `<div style="display:flex; justify-content: center; align-items: center; flex-direction: column">
                    <h2 class="text-center" style="padding-top: 10px;color: white; font-family: Barlow, sans-serif;font-weight: 900">`
                        + props.NOME + 
                    `</h2>
                    <br /> 
                    <div style="width: 300px;display: flex; flex-direction: row; justify-content: space-evenly; align-items: center">
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 15px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + samDash(toString(estadoGlobal), props.NOME) + 
                            `</h1>
                            <h4  class="text-center" style="color: white; padding-top: 25px">
                                Casos confirmados
                            </h4>
                        </div> 
                        <div style="display: flex; flex-direction: column;">
                            <h1 class="text-center" style="padding-top: 15px;color: white; font-family: Barlow, sans-serif;font-weight: 800">`
                                + samDashObitos(toString(estadoGlobal), props.NOME) + 
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
        L.geoJson(eval(this.estado), {style: style, onEachFeature: onEachFeature}).addTo(map);
    },
    computed: {
        
    },
    
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
    right: 0vw;
    top: 10px;
    width: 89% !important;
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
© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
