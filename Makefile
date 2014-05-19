GEO_LITE_CITY_URL=http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

.PHONY: all clean informe.pdf download-geolocation-db

all: informe.pdf

clean:
	rm -f informe.pdf tex/*.pdf tex/*.aux tex/*.log tex/*.toc

informe.pdf: tex/informe.tex
	cd tex; pdflatex -interaction=nonstopmode -halt-on-error informe.tex && \
	        pdflatex -interaction=nonstopmode -halt-on-error informe.tex
	cp tex/informe.pdf .

download-geolocation-db:
	wget -P data/ -N $(GEO_LITE_CITY_URL)
	gunzip data/GeoLiteCity.dat.gz