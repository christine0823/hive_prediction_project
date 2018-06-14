#ifndef MRPERF_MRPERF_H
#define MRPERF_MRPERF_H

#include <set>
#include <map>
#include <string>
#include <vector>
#include <list>
#include <deque>
#include <iostream>

//#include "datalayout.h"

using namespace std;


namespace MRPerf {

class Node;
class Chunk;
class Disk;

typedef map<std::string, Node*> TMSN;
typedef map<std::string, Chunk*> TMSC;
typedef map<std::string, Node*>::iterator TSN;
typedef map<std::string, Chunk*>::iterator TSC;

class MapTask: public TclObject {
public:
	MapTask() {}
	MapTask(Node *n, Chunk *c, Disk *d) : worker(n), chunk(c), disk(d) {}
	~MapTask() {}

	void dispatch(Node *n, Chunk *c, Disk *d);
	const char * string();

	Node *worker;	// which node will work on it
	Chunk *chunk;	// which chunk to work on
	Disk * disk;	// where the chunk is supposed to be fetched
	std::string string_;

protected:
	virtual int command(int argc, const char*const* argv);
};

class ReduceTask: public TclObject {
public:
	ReduceTask() {}
	~ReduceTask() {}

	Node *worker;
	Disk *disk;

protected:
	virtual int command(int argc, const char*const* argv);
};

class DataLayout;

class Scheduler: public TclObject {
public:
	Scheduler() {}
	~Scheduler() {}
	static Scheduler& instance() {
		if (instance_ == NULL)
			instance_ = new Scheduler;
		return (*instance_);
	}

	MapTask* schedule(MapTask*, Node *);
	MapTask* remote_schedule(MapTask*, Node *);
	MapTask * fixed_schedule(MapTask *task, Node *worker, Node *host);
	Disk *replica_selector(Node *n, Chunk *c);
	Disk *remote_replica_selector(Node *n, Chunk *c);

	ReduceTask* reducer_schedule(ReduceTask*, Node *);

	DataLayout* dl;

protected:
	virtual int command(int argc, const char*const* argv);
	//void _parse(char *meta_xml);
	static Scheduler* instance_;
	Chunk *chunk_;
};

class Deque: public TclObject {
public:
	Deque() {}
	~Deque() {}

	std::deque<std::string> str_deque;
	std::deque<TclObject *> obj_deque;

protected:
	virtual int command(int argc, const char*const* argv);
};

} // namespace MRPerf

#endif // ifndef MRPERF_MRPERF_H
