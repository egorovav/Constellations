from flask import Flask, render_template, request
from markupsafe import Markup
import json
import os
import constellation_repository as repo

constellation_controller = Flask(__name__)

repository = repo.ConstellationRepository()

@constellation_controller.route("/constellation")
def home():
   return render_template("index.html")

@constellation_controller.route("/constellation/map")
def map():
  constellations = repository.get_all_constellations_geojson()
  constellations_geojson = {"type": "FeatureCollection", "features": constellations}

  stars = repository.get_hygastra_by_magnitude_less_than(3.0)
  stars_geojson = {"type": "FeatureCollection", "features": stars}

  script_dir = os.path.dirname(os.path.abspath(__file__))
  with open(os.path.join(script_dir, "json", "constellation_borders.json"), "r") as f:
     poligon_borders = json.load(f)
  with open(os.path.join(script_dir, "json", "multipoligon_borders.json"), "r") as f:
     multipoligon_borders = json.load(f)

  return render_template("worldmap.html",
                            multiLineStringConstellations=constellations_geojson,
                            polygonBorders=poligon_borders,
                            multiPolygonBorders=multipoligon_borders,
                            astra=stars_geojson)

@constellation_controller.route("/constellation/list")
def list():
  constellations = repository.get_all_constellations()
  row_count = len(constellations) // 3
  constellations = [constellations[:row_count], constellations[row_count:row_count * 2], constellations[row_count * 2:]]
  return render_template("constellations.html", constellationsList=constellations)

@constellation_controller.route("/constellation/<abbr>")
def constellation(abbr):
   constellation_stars = sorted(repository.get_hygdata_by_abbr(abbr), key=lambda x: x.mag)
   constellation_links = repository.get_constellation_links(abbr)
   constellation = repository.get_constellation_by_abbr(abbr)
   return render_template("constellation.html", 
                          astraList=constellation_stars, 
                          links=constellation_links, 
                          constellationFigure=constellation)

@constellation_controller.route("/constellation/hygastra/<sort_column>/<page_number>")
def hygastra(sort_column, page_number):
   sort_column = sort_column if sort_column else "mag"
   page_number = int(page_number) if page_number else 1
   pagination = repository.get_hygastra_by_page(page=page_number, order_by=sort_column)
   page_numbers = []
   total_pages = pagination["pages"]
   page_numbers.append(1)
   first_page = max(page_number - 2, 2)
   if (first_page > 2):
      page_numbers.append(0)
   last_page = min(page_number + 2, total_pages - 1)
   for i in range(first_page, last_page + 1):
      page_numbers.append(i)
   if last_page < total_pages - 1:
      page_numbers.append(0)
   page_numbers.append(total_pages)
   return render_template("hygastra.html", 
                          page_content=pagination["items"], 
                          sort_column=sort_column, 
                          page_number=page_number, 
                          page_numbers=page_numbers)



if __name__ == "__main__":
    constellation_controller.run(debug=True)