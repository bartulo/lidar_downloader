import json 
import requests
from channels.generic.websocket import WebsocketConsumer
from django.contrib.gis.geos import Polygon
from .models import Lida2
from webapp import mapas
from os.path import exists
from os import path

class AppConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data = json.dumps({
            'type':'conexion_establecida',
            'message': 'conectado'
            }))


    def checkDownloaded(self, nombre):
        return exists(path.join('las', nombre))

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
                    'tam': i['tam'],
                    'descargado': self.checkDownloaded(i['nombre']),
                    'coords': list(map(lambda x: [x[1], x[0]], coords))
                    })
            self.send(text_data = json.dumps({
                'type':'products',
                'products': p,
                'bounds': bounds
                }))

        elif json.loads(text_data)['type'] == 'download':
            products = json.loads(text_data)['products']
            print(len(products))
            url = 'https://centrodedescargas.cnig.es/CentroDescargas/descargaDir'

            for n, product in enumerate(products):
                print(product)
                numFiles = sum(x.get('descargado') == False for x in products)
                if product['descargado'] is False:
                    with requests.post( url, data={'secuencialDescDir': product['id']}, stream=True ) as r:
            
                        with open(path.join('las', product['nombre']), 'wb') as f:
                            for i, chunk in enumerate(r.iter_content(chunk_size=1024)):
                                f.write(chunk)
                                self.send( text_data = json.dumps({
                                    'type': 'chunk',
                                    'tam': product['tam'],
                                    'chunk': i,
                                    'numFiles': numFiles
                                    }))

                    self.send( text_data = json.dumps({
                        'type': 'file_downloaded',
                        'file_number': n + 1,
                        'total_files': numFiles
                        }))

            self.send( text_data = json.dumps({
                'type': 'downloaded',
                'products': products
                }))

        elif json.loads(text_data)['type'] == 'fuelmap':
            products = json.loads(text_data)['products']
            for product in products:
                fm = mapas.FuelMap( product['nombre'] )
                fm.createHeightMap('matorral')
                fm.createHeightMap('arbolado')
                fm.createFuelMap()
