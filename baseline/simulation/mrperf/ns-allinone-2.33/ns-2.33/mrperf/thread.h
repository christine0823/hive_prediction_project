#ifndef MRPERF_THREAD_H
#define MRPERF_THREAD_H

#include <string>
#include <list>

#include <tclcl.h>

using namespace std;

namespace MRPerf {

extern double g_epsilon;

class TChain;
class TTask: public TclObject {
public:
	TTask() {}
	~TTask() {}

	double units;
	std::string _command;
	std::string _self;
	TChain *chain;
	int type;

protected:
	virtual int command(int argc, const char*const* argv);
};

class TChain: public TclObject {
public:
	TChain() {}
	~TChain() {}

	void run_first();
	void attach(TTask *);
	void insert(TTask *);
	void next_task();
	void o1(TTask *task = NULL);

	list<TTask *> chlist;
	std::list<TTask *>::iterator insert_it;

protected:
	virtual int command(int argc, const char*const* argv);
};

class TMultiChain: public TclObject {
public:
	TMultiChain(int d) : depth(d), running(0) {}
	~TMultiChain() {}

	void run_first();
	void attach(std::string *);
	void next_task();

	list<std::string *> chlist;
	int depth;
	int running;

protected:
	virtual int command(int argc, const char*const* argv);
};

class TTaskList: public TclObject {
public:
	TTaskList(double b, int n): bw(b), num(n), share(1.0) {}
	~TTaskList() {}

	list<TTask *> lst;
	double bw;
	int num;
	double share;
	double last;
	char self[256];
	char last_uid[256];

	void update_share();
	void recalculate();
	void schedule_first();
	void next_task();

protected:
	virtual int command(int argc, const char*const* argv);
};

} // namespace MRPerf

#endif // ifndef MRPERF_THREAD_H
