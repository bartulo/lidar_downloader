import json 
import requests
from channels.generic.websocket import WebsocketConsumer
from django.contrib.gis.geos import Polygon
from .models import Lida2
from webapp import mapas

class AppConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data = json.dumps({
            'type':'conexion_establecida',
            'message': 'conectado'
            }))

    def receive(self, text_data):
        if json.loads(text_data)['type'] == 'coords':
            data = json.loads(text_data)['coords']
            bounds = json.loads(text_data)['bounds']
            rect = list(map(lambda x: (x['lng'], x['lat']), data))
            rect.append((data[0]['lng'], data[0]['lat']))
            poly = Polygon(tuple(rect), srid=4326)
            products = Lida2.objects.filter(geom__intersects=poly)
            p = []
            for i in products.values():
                print(i)
                c = i['geom']
                c.transform(4326)
                coords = c.coords[0]
                p.append({
                    'id': i['num'],
                    'nombre': i['nombre'], 
                    'color': i['color'],
                    'sridOrig': i['orig_srid'],
                    'anho': i['anho'],
                    'lat': i['lat'],
                    'long': i['long'],
                    'coords': list(map(lambda x: [x[1], x[0]], coords))
                    })
            self.send(text_data = json.dumps({
                'type':'products',
                'products': p,
                'bounds': bounds
                }))

        elif json.loads(text_data)['type'] == 'download':
            products = json.loads(text_data)['products']
            url = 'https://centrodedescargas.cnig.es/CentroDescargas/descargaDir'

            for product in products:
                print(product['nombre'])
                r = requests.post( url, data={'secuencialDescDir': product['id']} )

                with open(product['nombre'], 'wb') as f:
                    f.write(r.content)

            self.send( text_data = json.dumps({
                'type': 'downloaded',
                'products': products
                }))

        elif json.loads(text_data)['type'] == 'fuelmap':
            products = json.loads(text_data)['products']
            for product in products:
                matorral = mapas.HeightMap( product['nombre'], 'matorral', product['long'], product['lat'] )
                arbolado = mapas.HeightMap( product['nombre'], 'arbolado', product['long'], product['lat'] )
                matorral.create()
                arbolado.create()
                fm = mapas.FuelMap( product['long'], product['lat'] )
                fm.calculate()
                fm.create_image()
