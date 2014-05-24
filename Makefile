GEO_LITE_CITY_URL=http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

.PHONY: all clean informe.pdf graphics graphics-oxford graphics-sydney graphics-must \
	    statistics traces trace-oxford trace-sydney trace-must \
            download-geolocation-db

all: graphics statistics informe.pdf

clean:
	rm -f informe.pdf tex/*.aux tex/*.log tex/*.toc tex/*.out

traces: trace-oxford trace-sydney trace-must
	
trace-oxford:
	./traceroute www.ox.ac.uk -t 3600 -o traces/www.ox.ac.uk

trace-sydney:
	./traceroute www.sydney.edu.au -t 3600 -o traces/www.sydney.edu.au

trace-must:
	./traceroute www.must.edu.my -t 3600 -o traces/www.must.edu.my

graphics: graphics-oxford graphics-sydney graphics-must

graphics-oxford:
	cat traces/www.ox.ac.uk | ./map -o tex/map-www.ox.ac.uk.pdf
	cat traces/www.ox.ac.uk | ./rttchart -o tex/rtt-www.ox.ac.uk.pdf
	cat traces/www.ox.ac.uk | ./zrttchart -o tex/zrtt-www.ox.ac.uk.pdf

graphics-sydney:
	cat traces/www.sydney.edu.au | ./map -o tex/map-www.sydney.edu.au.pdf
	cat traces/www.sydney.edu.au | ./rttchart -o tex/rtt-www.sydney.edu.au.pdf
	cat traces/www.sydney.edu.au | ./zrttchart -o tex/zrtt-www.sydney.edu.au.pdf

graphics-must:
	cat traces/www.must.edu.my | ./map -o tex/map-www.must.edu.my.pdf
	cat traces/www.must.edu.my | ./rttchart -o tex/rtt-www.must.edu.my.pdf
	cat traces/www.must.edu.my | ./zrttchart -o tex/zrtt-www.must.edu.my.pdf

statistics:
	cat traces/www.ox.ac.uk      | ./statistics > tex/statistics-www.ox.ac.uk.txt
	cat traces/www.sydney.edu.au | ./statistics > tex/statistics-www.sydney.edu.au.txt
	cat traces/www.must.edu.my   | ./statistics > tex/statistics-www.must.edu.my.txt

informe.pdf: tex/informe.tex
	cd tex; pdflatex -interaction=nonstopmode -halt-on-error informe.tex && \
	        pdflatex -interaction=nonstopmode -halt-on-error informe.tex
	mv tex/informe.pdf .

download-geolocation-db:
	wget -P data/ -N $(GEO_LITE_CITY_URL)
	gunzip data/GeoLiteCity.dat.gz
