
all: hsim

hsim: random.xml
	ns hsim.tcl

meta: random.xml

gen:
	# create random.xml as Data Layout (metadata)
	./gen.py -t topology1.xml -g metadata_gen1.xml -m random.xml

topo:
	# create hadoop.topo.tcl and mapnodes.tcl (topology)
	./conv.py -t topology1.xml -m random.xml -j job1.xml

job:
	# create hadoop.job.tcl (job characteristics)
	# now hadoop.job.tcl is modified manually - Guanying 2008.11.20
	#cp bak.job.tcl hadoop.job.tcl

sim: hsim

random.xml: topology1.xml metadata_gen1.xml gen.py
	make gen

hadoop.topo.tcl: topology1.xml conv.py
	./conv.py -t topology1.xml -m random.xml -j job1.xml

clean:
	rm -rf out.*

dist-clean:
	rm -rf out.* *.pyc stat* random.xml mapnodes.tcl hadoop.topo.tcl

temp.svg: stats
	cat stats | python spyros/stats2xml.py | python spyros/xml2svg.py > temp.svg

svg: temp.svg

view: temp.svg
	inkscape temp.svg &

small:
	cp ../exp/t-small.xml topology1.xml
	cp ../exp/mg-small.xml metadata_gen1.xml
	cp ../exp/job-small.tcl hadoop.job.tcl

test: small topo gen all

