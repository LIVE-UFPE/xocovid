<template>
    <div id="map">
    </div>
</template>
<script>

module.exports ={
    name: 'state-map',
    data: function (){
        return{
            test: null,
            request: null,
            casos: [],
            map: null,
            geojson: null,
            style: null,
        } 
    },
    // ? como props aq é um objeto, não é possível dar watch diretamente nas propriedades de prop, para isso, usamos uma computed property e damos watch nela. vale citar também que as props são acessadas por "this.pins", por exemplo, diretamente em qualquer porção de código no script
    props: {
        datedb: Date,
    },
    methods: {
        getCasos(){
            console.log(`datedb é ${this.datedb}`)
            if (this.request != null) {
                this.request.abort();
            }
            //pede a quantidade de óbitos acumulados de cada estado do dia
            this.request = $.ajax({
                context: this,
                type: 'GET',
                url: "graphs/get_data",
                data: {"informacao": 'Casos Confirmados', "keyBusca": 'estadosdia', "dia": this.datedb.toISOString().substring(0,10), "estado": '', "cidade": '', "bairro": ''},
                success: function (response) {
                    this.casos = JSON.parse(response)
                    this.geojson.setStyle(this.style)
                }
            })
        }
    },
    mounted() {
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
        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature.bind(this),
                mouseout: resetHighlight.bind(this),
                click: zoomToFeature.bind(this)
            });
        }
        // TODO automatizar intensidade das cores com base na maior quantidade de óbitos??
        function getColor(estado,that) {
            if(that.casos.length == 0) return '#800026'
            // DEBUG lista os casos
            console.log(that.casos)
            let d = that.casos.find( elem => elem['estado_residencia'] === estado)['quantidade_casos']
            return d > 1000 ? '#800026' :
                d > 15  ? '#BD0026' :
                d > 12  ? '#E31A1C' :
                d > 10  ? '#FC4E2A' :
                d > 3   ? '#FD8D3C' :
                d > 2   ? '#FEB24C' :
                d > 1   ? '#FED976' :
                          '#FFEDA0'
        }
        function style(feature) {
            return {
                // TODO mudar esse parametro p um pego pelo ajax
                fillColor: getColor(feature.properties.name,this),
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

        // TODO mudar props.id pra um método que realmente pegue o numero de casos acumulados
        //this.casos.find( elem => elem['estado_residencia'] === props.name)['quantidade_casos']
        info.update = function (props, that) {
            this._div.innerHTML = '<h4>Número de casos confirmados</h4>' +  (props ?
                 '<br /> <h1 class="text-center" style="color: white; font-weight: bold;font-size: x-large !important">' + that.casos.find( elem => elem['estado_residencia'] === props.name)['quantidade_casos'] + '</h1> <br /> <h4  class="text-center" style="color: white">casos confirmados</h4> <h5 class="text-center" style="color: white">'+ props.name + '</h5>'
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
    margin-top: 80px
}
.leaflet-control-container{
     margin-left: 200px;
}
</style>