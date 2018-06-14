#ifndef NS_DATALAYOUT_H
#define NS_DATALAYOUT_H

#include <vector>
#include <set>
#include <string>
#include <map>

#include <libxml/tree.h>
#include <libxml/parser.h>

#include <tclcl.h>
//#include "agent.h"
//#include "app.h"

using namespace std;

namespace MRPerf {

extern const int CHUNK_SIZE;

class Chunk;
class Disk;

class Node: public TclObject {
public:
	Node();
	~Node();

	bool operator< (Node&);
	void dump();
//	virtual void process_data(int size, AppData* data);
	char * schedule(Node *node);
	const char * string() {return string_.c_str();}
	Disk * rack_local(Chunk *c);

	vector<Disk *> disks;
	set<Chunk *> chunks;
	Chunk * working_on;
	double cycles_per_second;
	std::string string_;
	std::string rack_;

protected:
	virtual int command(int argc, const char*const* argv);

};

class Disk: public TclObject {
public:
	Disk() {};
	~Disk() {};
	const char * string();

	set<Chunk *> chunks;
	Node * host;
	int id;
	double read_bw;	//in MB/s
	double write_bw; // in MB/s
	std::string string_;

protected:
	virtual int command(int argc, const char*const* argv);
};

template <class T>
struct addrcomp {
	bool operator() (const T& lhs, const T& rhs) const
	{ return &lhs < &rhs; }
};

class Chunk: public TclObject {
public:
	Chunk();
	Chunk(char *filename, int chunk, int offset, int length);
	Chunk(char *);
	~Chunk();

	bool operator< (Chunk&);
	void dump();

	char * filename;
	int chunk;
	int offset;
	int length;
	set<Disk *>& get_host_disks() {return host_disks_;}
	set<Node *>& get_hosts() {return hosts_;}
	set<Node *>& get_workers() {return workers_;}
	const char * string() {return string_.c_str();}

	set<Disk *> host_disks_;
	set<Node *> hosts_;
	set<Node *> workers_;
	std::string string_;
	// It is possible to read _workers to determine status
	//int status; /* todo, doing, done */
	int finished;

protected:
	virtual int command(int argc, const char*const* argv);
};

Disk * get_disk(const char *string);
Chunk * get_chunk(const char * string);
Node * get_node(const char * string);

class DataLayout {
public:
	DataLayout();
	~DataLayout();
	static DataLayout& instance()
	{
		if (instance_ == NULL)
			instance_ = new DataLayout();
		return (*instance_);
	}
	int read_xml(const char * meta_xml);

	void insert(Chunk&, Node&);

	//multimap<Chunk, Node, addrcomp<Chunk> > *chunk_to_nodes;
	//multimap<Node, Chunk, addrcomp<Node> > *node_to_chunks;
	map<std::string, Node*> string_to_node;
	map<std::string, Chunk*> string_to_chunk;

protected:
	int _parse(const char *meta_xml);
	static DataLayout* instance_;
	xmlDocPtr doc; /* the resulting document tree */

};

} // namespace MRPerf

#endif // ifndef NS_DATALAYOUT_H

