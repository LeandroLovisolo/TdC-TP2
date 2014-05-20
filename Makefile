GEO_LITE_CITY_URL=http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

.PHONY: all clean informe.pdf graficos graficos-oxford graficos-sydney graficos-must download-geolocation-db

all: graficos informe.pdf

clean:
	rm -f informe.pdf tex/*.aux tex/*.log tex/*.toc

informe.pdf: tex/informe.tex
	cd tex; pdflatex -interaction=nonstopmode -halt-on-error informe.tex && \
	        pdflatex -interaction=nonstopmode -halt-on-error informe.tex
	mv tex/informe.pdf .

graficos: graficos-oxford graficos-sydney graficos-must

graficos-oxford:
	cat traces/www.ox.ac.uk | ./rttchart -o tex/rtt-www.ox.ac.uk.pdf
	cat traces/www.ox.ac.uk | ./zrttchart -o tex/zrtt-www.ox.ac.uk.pdf

graficos-sydney:
	cat traces/www.sydney.edu.au | ./rttchart -o tex/rtt-www.sydney.edu.au.pdf
	cat traces/www.sydney.edu.au | ./zrttchart -o tex/zrtt-www.sydney.edu.au.pdf

graficos-must:
	cat traces/www.must.edu.my | ./rttchart -o tex/rtt-www.must.edu.my.pdf
	cat traces/www.must.edu.my | ./zrttchart -o tex/zrtt-www.must.edu.my.pdf

download-geolocation-db:
	wget -P data/ -N $(GEO_LITE_CITY_URL)
	gunzip data/GeoLiteCity.dat.gz