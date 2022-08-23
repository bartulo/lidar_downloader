let url = `ws://${window.location.host}/ws/socket-server/`
socket = new WebSocket( url );

var mapcenter = [40.47132109359731, -3.907624901567564];
var map = L.map('map', {zoomControl: false}).setView(mapcenter, 6);

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '1652310'}).addTo(map);

var layerGroup = L.layerGroup().addTo(map);
var rectGroup = L.layerGroup().addTo(map);

var drawControl = new L.Control.Draw({
    draw: {
        circle: false,
        circlemarker: false,
        polygon: {
            allowIntersection: false
        }
    }
});

map.addControl(drawControl);

map.on(L.Draw.Event.CREATED, function (event) {
  rectGroup.clearLayers();
  c = event.layer._latlngs[0];
  bounds = [[c[0].lat, c[0].lng], [c[2].lat, c[2].lng]];
  console.log(bounds);
  socket.send(JSON.stringify({
    'type': 'coords',
    'coords': event.layer._latlngs[0],
    'bounds': bounds
  }));
  var layer = event.layer;
  rectGroup.addLayer(layer);
});

class Lidar {
  constructor() {

    this.modal = new bootstrap.Modal( document.getElementById('modal'), {backdrop: false})
    this.colorsDiv = document.getElementById('radioColors');
    this.sridDiv = document.getElementById('radioSRID');
    this.anhoDiv = document.getElementById('radioAnho');
    this.numItems = document.getElementById('numItems');
    this.noProducts = document.getElementById('noProducts');
    this.download = document.getElementById('download');

    this.download.addEventListener('click', () => {
      socket.send(JSON.stringify({
        'type': 'download',
        'products': this.items
      }));

    })

    socket.onmessage = (e) => {
      this.data = JSON.parse(e.data);
      if (this.data.type == 'products') {
        this.clean();
        map.fitBounds( this.data.bounds );
        if ( this.data.products.length == 0 ) {
          this.showNoProducts();
          this.numItems.innerHTML = '0';
        } else {
          this.colors = [...new Set(this.data.products.map(item => item.color))]
          this.srid = [...new Set(this.data.products.map(item => item.sridOrig))]
          this.anho = [...new Set(this.data.products.map(item => item.anho))]
          this.populateCheckboxes( this.colorsDiv, this.colors );
          this.populateCheckboxes( this.sridDiv, this.srid );
          this.populateCheckboxes( this.anhoDiv, this.anho );
          this.items = this.data.products;
          this.mostrarLAZ();
          this.numItems.innerHTML = this.items.length;
        }
        this.modal.show();
      } else if (this.data.type == 'downloaded') {
        console.log( this.data );
        socket.send(JSON.stringify({
          'type': 'fuelmap',
          'products': this.data.products
        }));
      }
    }

 }

  showNoProducts() {
    if ( this.noProducts.classList.contains('hidden') ) {
      this.noProducts.classList.remove('hidden');
    }
  }

  populateCheckboxes( div, ob ) {

    ob.forEach( elem => {
      this.form = document.createElement('DIV');
      this.form.classList.add('form-check');
      this.form.classList.add('form-check-inline');
      this.form.classList.add( div.id );
      div.appendChild(this.form);

      let i = document.createElement('INPUT');
      i.setAttribute('type', 'checkbox');
      i.setAttribute('name', 'inlineRadioOptions');
      i.setAttribute('checked', true);
      i.setAttribute('value', elem);
      i.classList.add('form-check-input');
      this.form.appendChild(i);

      let l = document.createElement('LABEL');
      l.classList.add('form-check-label');
      l.innerHTML = elem;
      this.form.appendChild(l);
      
    });

    document.querySelectorAll('input[type=checkbox]').forEach( item => {
      item.addEventListener('change', event => {
        const col = this.colorsDiv.querySelectorAll('input[type="checkbox"]:checked');
        const srid = this.sridDiv.querySelectorAll('input[type="checkbox"]:checked');
        const anhos = this.anhoDiv.querySelectorAll('input[type="checkbox"]:checked');
        const items = []
        col.forEach( item => {
          items.push(...this.data.products.filter( elem => {
            return elem.color == item.value
          }))
        });
        const items2 = []
        anhos.forEach( item => {
          items2.push(...items.filter( elem => {
            return elem.anho == item.value
          }))
        });
        this.items = []
        srid.forEach( item => {
          this.items.push(...items2.filter( elem => {
            return elem.sridOrig == item.value
          }))
        });
        layerGroup.clearLayers();
        this.mostrarLAZ();
        this.numItems.innerHTML = this.items.length;

      });
    });
 
  }
  
  clean() {
    this.noProducts.classList.add('hidden');
    layerGroup.clearLayers();
    this.colorsDiv.innerHTML = '';
    this.sridDiv.innerHTML = '';
    this.anhoDiv.innerHTML = '';
    this.numItems.innerHTML = '';

  }

  mostrarLAZ() {
    this.items.forEach( elem => {
      let polygon = L.polygon( elem.coords, {color: 'red'} ).addTo(layerGroup);
    });
  }
}

const lidar = new Lidar();
