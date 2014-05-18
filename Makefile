GEO_LITE_CITY_URL=http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

.PHONY: download-geolocation-db

download-geolocation-db:
	wget -P data/ -N $(GEO_LITE_CITY_URL)
	gunzip data/GeoLiteCity.dat.gz