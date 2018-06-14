#include "datalayout.h"
#include "mrperf.h"

namespace MRPerf {

const int CHUNK_SIZE=16*1024*1024;

static class NodeClass: public TclClass {
public:
	NodeClass() : TclClass("MRPerf/Node") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new Node);
	}
} node_class;

Node::Node()
{
	//this->chunks = new set<Chunk *>;
	this->working_on = NULL;
}

Node::~Node()
{
}

int Node::command(int argc, const char*const* argv)
{
	Tcl& tcl = Tcl::instance();

	if (argc == 3) {
		if (strcmp(argv[1], "setnodename") == 0) {
			TMSN& msn = DataLayout::instance().string_to_node;

			this->string_ = argv[2];
			// n_rg0_0_ng0_1
			const char * const s = argv[2];
			const char* first = strchr(s, '_');
			const char* second = strchr(first+1, '_');
			const char* third = strchr(second+1, '_');

			//*third = NULL;
			third = NULL;
			this->rack_ = first+1;
			msn.insert(pair<std::string, Node*>(this->string_, this));

			return TCL_OK;
		}
#if 0
		else if (strcmp(argv[1], "has") == 0) {
			Chunk *chunk = get_chunk(const_cast<char*>(argv[2]));
			if (chunk == NULL) {
				tcl.add_errorf("Wrong chunk name %s", argv[2]);
				return TCL_ERROR;
			}
			// Here I search for node in chunk's hosts, I can also search
			// for chunk in node's chunks. should give the same result.
			if (chunk->get_hosts().find(this) != chunk->get_hosts().end())
				tcl.result("true");
			else
				tcl.result("false");
			return TCL_OK;
		}
#endif
		else if (strcmp(argv[1], "print") == 0) {
			fprintf(stderr, "%s %s\n", string_.c_str(), argv[2]);

#if 1
			DataLayout& inst = DataLayout::instance();
			TMSN& msn = inst.string_to_node;
			TSN snit;
			for (snit = msn.begin(); snit != msn.end(); snit++)
			{
				Node *n = const_cast<Node *>(snit->second);

				//fprintf(stderr, "%s\n", snit->first.c_str());
				n->dump();
			}

			TMSC& msc = inst.string_to_chunk;
			TSC scit;
			for (scit = msc.begin(); scit != msc.end(); scit++)
			{
				Chunk *c = const_cast<Chunk *>(scit->second);
				fprintf(stderr, "%s-----", c->string());
				set<Disk*>::iterator dit;
				for (dit = c->get_host_disks().begin(); dit != c->get_host_disks().end(); dit++)
				{
					Disk *d = (*dit);
					fprintf(stderr, " %s:%d", d->host->string(), d->id);
				}
				fprintf(stderr, "\n");
			}

			snit = msn.find(string_);
			//fprintf(stderr, "%p %p\n", this, (snit->second));
#endif
			return TCL_OK;
		}
		else if (strcmp(argv[1], "add-disk") == 0) {
			Disk *d = (Disk *)TclObject::lookup(argv[2]);
			d->id = disks.size();
			this->disks.push_back(d);
			d->host = this;
			return TCL_OK;
		}
	}
	else if (argc == 2) {
		if (strcmp(argv[1], "nodename") == 0) {
			tcl.result(this->string_.c_str());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "choosedisk") == 0) {
			tcl.result(disks[0]->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "rack") == 0) {
			tcl.result(rack_.c_str());
			return TCL_OK;
		}
	}

	//fprintf(stderr, "%d %s\n", argc, argv[1]);

	return (TclObject::command(argc, argv));
}

void Node::dump()
{
	fprintf(stderr, "%s:\n", this->string_.c_str());
	vector<Disk *>::iterator dit;
	set<Chunk *>::iterator it;
	for (dit = disks.begin(); dit != disks.end(); dit++)
	{
		fprintf(stderr, "\t");
		for (it = (*dit)->chunks.begin(); it != (*dit)->chunks.end(); it++)
			fprintf(stderr, "%s ", (*it)->string());
		fprintf(stderr, "\n");
	}
	//fprintf(stderr, "\n");
}

Disk * Node::rack_local(Chunk *c)
{
	set<Disk*> *disks = &c->get_host_disks();
	set<Disk*>::iterator dit;
	for ( dit = disks->begin(); dit != disks->end(); dit++)
	{
		Disk *d = *dit;
		if (rack_.compare(d->host->rack_) == 0)
			return d;
	}

	return NULL;
}

static class DiskClass: public TclClass {
public:
	DiskClass() : TclClass("MRPerf/Node/Disk") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new Disk);
	}
} disk_class;

int Disk::command(int argc, const char*const* argv)
{
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "host") == 0) {
			tcl.result(this->host->name());
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

const char * Disk::string()
{
	// TODO: this is not correct. string_ is never assigned a value.
	return string_.c_str();
}

static class ChunkClass: public TclClass {
public:
	ChunkClass() : TclClass("MRPerf/Chunk") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new Chunk);
	}
} chunk_class;

Chunk::Chunk()
{
	/* how large a buffer should be? a better string type may be needed */
	filename = new char[10];
	memcpy(filename, "filename", 9);
	chunk = 0;
	offset = 0;
	length = 128 * 1024 * 1024;

	//workers_ = new set<Node *>;
	//hosts_ = new set<Node *>;
	string_ = filename;
	char s[100];
	sprintf(s, ":%d:%d:%d", chunk, offset, length);
	string_ += s;
	finished = 0;
}

Chunk::Chunk(char *f, int c, int o, int l)
{
	this->filename = new char[strlen(f)+1];
	strcpy(this->filename, f);
	this->chunk = c;
	this->offset = o;
	this->length = l;

	//workers_ = new set<Node *>;
	//hosts_ = new set<Node *>;
	string_ = filename;
	char s[100];
	sprintf(s, ":%d:%d:%d", chunk, offset, length);
	string_ += s;
	finished = 0;

	TMSC& msc = DataLayout::instance().string_to_chunk;
	msc.insert(pair<std::string, Chunk*>(this->string_, this));
}

Chunk::~Chunk()
{
	delete this->filename;
}

Chunk * get_chunk(const char * string)
{
	TMSC& msc = DataLayout::instance().string_to_chunk;
	TSC scit = msc.find(string);

	if (scit == msc.end())
	{
		fprintf(stderr, "Warning: nonexist chunk %s\n", string);
		return NULL;
	}

	Chunk* c = const_cast<Chunk*>(scit->second);
	return c;
}

Node * get_node(const char * string)
{
	TMSN &msn = DataLayout::instance().string_to_node;
	TSN snit = msn.find(string);

	if (snit == msn.end())
	{
		fprintf(stderr, "Warning: nonexist node %s\n", string);
		return NULL;
	}

	Node* n = const_cast<Node*>(snit->second);
	return n;
}

int Chunk::command(int argc, const char*const* argv)
{
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "name") == 0) {
			tcl.resultf("%s:%d:%d:%d", filename, chunk, offset, length);
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

void Chunk::dump()
{
	fprintf(stderr, "%s\n", string());
}

DataLayout* DataLayout::instance_;

DataLayout::DataLayout()
{
	//string_to_chunk = new TMSC;
	//string_to_node = new TMSN;
#if 0
	Tcl& tcl = Tcl::instance();
	tcl.eval("set epsilon");
	g_epsilon = atof(tcl.result());

	if (g_epsilon <= 0)
	{
		cout << "g_epsilon < 0: " << g_epsilon << \
			", setting it to 0.01" << endl;
		g_epsilon = 0.01;
	}
#endif
}

int DataLayout::read_xml(const char *meta_xml)
{

	/*
	 * this initialize the library and check potential ABI mismatches
	 * between the version it was compiled for and the actual shared
	 * library used.
	 */
	LIBXML_TEST_VERSION

	return _parse(meta_xml);

}

DataLayout::~DataLayout()
{
	xmlFreeDoc(doc);

	/*
	 * Cleanup function for the XML library.
	 */
	xmlCleanupParser();
	/*
	 * this is to debug memory for regression tests
	 */
	xmlMemoryDump();
}

int DataLayout::_parse(const char *meta_xml)
{
	xmlNodePtr nfile, nchunk, nreplica;
	xmlChar *dir, *file, *chunk, *rep, *name_node;
	int chunk_size;

	doc = xmlReadFile(meta_xml, NULL, 0);
	if (doc == NULL) {
		fprintf(stderr, "Failed to parse %s\n", meta_xml);
		return -1;
	}

	xmlNodePtr cur = xmlDocGetRootElement(doc);
	cur = cur->xmlChildrenNode;

	for ( ; cur && (xmlStrcmp(cur->name, (const xmlChar *)"chunk_size") != 0); cur = cur->next);
	if (cur != NULL) {
		chunk_size = atoi(reinterpret_cast<char *>(xmlNodeListGetString(doc, cur->xmlChildrenNode, 1))) * 1024 * 1024;
		//printf("chunk_size from xml: %d\n", chunk_size);
	} else {
		chunk_size = CHUNK_SIZE;
		cur = xmlDocGetRootElement(doc);
	}
	for ( ; cur && (xmlStrcmp(cur->name, (const xmlChar *)"name_node") != 0); cur = cur->next);
	name_node = xmlNodeListGetString(doc, cur->xmlChildrenNode, 1);
	//printf("name node from xml: %s\n", name_node);
	Tcl& tcl = Tcl::instance();
	tcl.evalf("set nn $%s\n", name_node);

	while ( cur && (xmlIsBlankNode(cur) \
					|| xmlStrcmp(cur->name, (const xmlChar *) "dir") != 0)) {
		cur = cur->next;
	}
	if (cur == NULL) {
		xmlFreeDoc(doc);
		return -1;
	}

	dir = xmlGetProp(cur, (const xmlChar *) "name");

	for (nfile = cur->xmlChildrenNode; nfile != NULL; nfile = nfile->next)
	{
		if (xmlStrcmp(nfile->name, (const xmlChar *) "file") != 0)
			continue;
		file = xmlGetProp(nfile, (const xmlChar *) "name");

		for (nchunk = nfile->xmlChildrenNode; nchunk != NULL; nchunk = nchunk->next)
		{
			if (xmlStrcmp(nchunk->name, (const xmlChar *) "chunk") != 0)
				continue;
			chunk = xmlGetProp(nchunk, (const xmlChar *) "id");
			Chunk *c = new Chunk(reinterpret_cast<char *>(file),
						atoi(reinterpret_cast<char *>(chunk)), 0, chunk_size);

			for (nreplica = nchunk->xmlChildrenNode; nreplica != NULL;
				nreplica = nreplica->next)
			{
				if (xmlStrcmp(nreplica->name, (const xmlChar *) "rep") != 0)
					continue;
				rep = xmlNodeListGetString(doc, nreplica->xmlChildrenNode, 1);

				std::string str (reinterpret_cast<char *>(rep));
				size_t underscore = str.rfind('_');
				str[0] = 'n';

				Node *n = get_node(str.substr(0, underscore).c_str());
				int disk_id = atoi(str.substr(underscore+strlen("_disk")).c_str());
				if (n == NULL)
				{
					fprintf(stderr, "warning: nonexist node: %s\n", str.c_str());

					// TODO: maybe other operations
					//return;
				}

#if 0
				// replicas guaranteed on disk level, not node level.
				// see comments in gen.py.
				if (c->get_hosts().find(n) != c->get_hosts().end())
					fprintf(stderr, "error!!!! %s %s\n", n->string(), c->string());
				if (n->chunks.find(c) != n->chunks.end())
					fprintf(stderr, "error!!!!!!!\n");
#endif
				Disk *d = n->disks[disk_id];
				c->get_host_disks().insert(d);
				d->chunks.insert(c);

				//c->get_hosts().insert(n);
				//n->chunks.insert(c);

#if 0
				DataLayout& inst = DataLayout::instance();
				inst.chunk_to_nodes.insert(pair<Chunk,Node>(*c, *n));
				inst.node_to_chunks.insert(pair<Node,Chunk>(*n, *c));
#endif
			}
		}
	}

	DataLayout& inst = DataLayout::instance();
	TMSC& msc = inst.string_to_chunk;
	fprintf(stderr, "done parsing, totally %d chunks\n", msc.size());
#if 0
	TSC scit;
	for (scit = msc.begin(); scit != msc.end(); scit++)
	{
		Chunk *c = const_cast<Chunk *>((*scit).second);

		if (c->get_hosts().size() != 3)
			fprintf(stderr, "replicas error!\n");
		//c->dump();
	}

#endif

	return msc.size();
}

} // namespace MRPerf

