jQuery(document).ready(function($){
  var astraStyle = new ol.style.Style({
    image: new ol.style.Circle({
      radius: 5,
      fill: new ol.style.Fill({
        color: 'orange'
      })
    }),
    text: new ol.style.Text({
        font: '12px Calibri,sans-serif',
        textBaseline: 'bottom',
        fill: new ol.style.Fill({
            color: 'rgba(100,100,100,1)'
        }),
        stroke: new ol.style.Stroke({
            color: 'rgba(255,255,255,1)',
            width: 3
        }),
        text: ''
    })
  });

  var constellationStyle = new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: 'red',
        width: 2
      }),
      text: new ol.style.Text({
          font: '18px Calibri,sans-serif',
          textBaseline: 'middle',
          fill: new ol.style.Fill({
              color: 'rgba(0,0,0,1)'
          }),
          stroke: new ol.style.Stroke({
               color: 'rgba(255,255,255,1)',
               width: 3
          }),
          text: ''
      })
  });

  var selectStyle = new ol.style.Style({
     stroke: new ol.style.Stroke({
          color: 'rgba(255,255,255,1)',
          width: 1
     }),
  });

  let borderStyle = new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: 'rgba(0, 0, 255, 0.1)',
      width: 1
    }),
    text: new ol.style.Text({
        font: '18px Calibri,sans-serif',
        textBaseline: 'middle',
        fill: new ol.style.Fill({
            color: 'rgba(0,0,0,1)'
        }),
        stroke: new ol.style.Stroke({
            color: 'rgba(255,255,255,1)',
            width: 3
        }),
        text: ''
    })
  });

  var format = new ol.format.GeoJSON();

  var astraSource = new ol.source.Vector({
        features: format.readFeatures(astra)
  });

   let astraStyleFunction = function (feature, resolution) {
        let str = feature.get("name") + '\n(' + feature.get("bayer") + '-' + feature.get("constellation") +')';
        astraStyle.getText().setText(str);
        return astraStyle;
   }


   var astraLayer = new ol.layer.Vector({
          source: astraSource,
          style: astraStyleFunction
   });

  let styleFunction = function (feature, resolution) {
        let str = feature.get("name") + '\n(' + feature.get("nameLat") + ')';
        //borderStyle.getText().setText(str);
        return borderStyle;
  }

  var constellationBorderSource = new ol.source.Vector({
      /* projection: 'EPSG:4326', */
      features: format.readFeatures(polygonBorders)
  });

  constellationBorderSource.addFeatures(format.readFeatures(multiPolygonBorders));

  var constellationBordersLayer = new ol.layer.Vector({
        source: constellationBorderSource,
        style: styleFunction
  });

  var constellationSource = new ol.source.Vector({
      features: format.readFeatures(lineStringConstellations)
  });

  let constellationStyleFunction = function (feature, resolution) {
      let geometry = feature.getGeometry();
      let str = feature.get("name") + '\n(' + feature.get("nameLat") + ')';
      
      if (geometry.getType() === 'MultiLineString') {
          let extent = geometry.getExtent();
          let centerPoint = [(extent[0] + extent[2]) / 2, (extent[1] + extent[3]) / 2];
          
          // Находим линию ближайшую к центру
          let coordinates = geometry.getCoordinates();
          let closestLine = null;
          let minDistance = Infinity;
          
          coordinates.forEach(line => {
              let lineMid = [(line[0][0] + line[1][0]) / 2, (line[0][1] + line[1][1]) / 2];
              let distance = Math.sqrt(Math.pow(lineMid[0] - centerPoint[0], 2) + Math.pow(lineMid[1] - centerPoint[1], 2));
              if (distance < minDistance) {
                  minDistance = distance;
                  closestLine = line;
              }
          });
          
          let textPoint = [(closestLine[0][0] + closestLine[1][0]) / 2, (closestLine[0][1] + closestLine[1][1]) / 2];
          
          let textStyle = constellationStyle.clone();
          textStyle.setGeometry(new ol.geom.Point(textPoint));
          textStyle.getText().setText(str);
          return [constellationStyle, textStyle];
      }
      
      constellationStyle.getText().setText('');
      return constellationStyle;
  }

  constellationSource.addFeatures(format.readFeatures(multiLineStringConstellations));

    var constellationLayer = new ol.layer.Vector({
        source: constellationSource,
        style: constellationStyleFunction
  });

  var map = new ol.Map({
        target: 'map',
        layers: [
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                }),
                constellationLayer,
                constellationBordersLayer,
                astraLayer
        ],
        view: new ol.View({
          /* projection: 'EPSG:4326', */
          center: [62, 13],
          zoom: 4
        })
  });

  map.on('click', function(event) {
     map.forEachFeatureAtPixel(event.pixel, function(feature, layer) {
         /* feature.setStyle(selectStyle); */
         let id = feature.getId();
         document.location.href="/constellation/" + id;
     });
  });
});