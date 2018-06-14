#include <set>
#include <list>
#include <iostream>

#include <stdlib.h>

#include "scheduler.h"
#include "thread.h"

using namespace std;

namespace MRPerf {

double g_epsilon=10000;

static class TMultiChainClass: public TclClass {
public:
	TMultiChainClass() : TclClass("MRPerf/Thread/MultiChain") {}
	TclObject* create(int argc, const char*const* argv) {
		if (argc != 5)
			return NULL;
		int depth = atoi(argv[4]);
		return (new TMultiChain(depth));
	}
} tmultichain_class;

int TMultiChain::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "next-task") == 0) {
			running -= 1;
			//printf("before next, %d running, %d waiting\n", running, chlist.size());
			next_task();
			//printf("after next, %d running, %d waiting\n", running, chlist.size());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "size") == 0) {
			tcl.resultf("%d", chlist.size());
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "attach") == 0) {
			std::string * task = new std::string(argv[2]);
			//printf("attach %s, %d running, %d waiting\n", argv[2], running, chlist.size());
			attach(task);
			//printf("after attach %s, %d running, %d waiting\n", argv[2], running, chlist.size());
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

void TMultiChain::run_first()
{
}

void TMultiChain::next_task()
{
	if (chlist.empty())
		return;
	if (running >= depth)
		return;

	Tcl& tcl = Tcl::instance();
	std::string *task = chlist.front();
	if (task == NULL)
		return;
	chlist.pop_front();
	running += 1;
	tcl.evalf("%s run", task->c_str());
	delete task;
}

void TMultiChain::attach(std::string *task)
{
	bool open = (running < depth);
	chlist.push_back(task);

	if (open == 1)
		next_task();
}

static class TChainClass: public TclClass {
public:
	TChainClass() : TclClass("MRPerf/Thread/Chain") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new TChain);
	}
} tchain_class;

int TChain::command(int argc, const char*const* argv) {
	//Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "next-task") == 0) {
			next_task();
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "attach") == 0) {
			TTask *task = (TTask *)(TclObject::lookup(argv[2]));
			attach(task);
			return TCL_OK;
		}
		else if (strcmp(argv[1], "insert") == 0) {
			TTask *task = (TTask *)(TclObject::lookup(argv[2]));
			insert(task);
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

void TChain::run_first()
{
	Tcl& tcl = Tcl::instance();
	TTask *task = chlist.front();
	task->chain = this;
	insert_it = chlist.begin();
	insert_it++;
	//printf("insert_it=%d\n", distance(insert_it, chlist.begin()));
	tcl.evalf("%s", task->_command.c_str());
	if (task->type == 0)
		next_task();
	else if (task->type == 1 && task->units < g_epsilon)
	{
		printf("command='%s'\n", task->_command.c_str());
		printf("chain=%s units=%lf epsilon=%lf\n", this->name(), task->units, g_epsilon);
	}
}

void TChain::next_task()
{
	if (chlist.size() > 0)
	{
		TTask *task = chlist.front();
		Tcl& tcl = Tcl::instance();
		chlist.pop_front();
		//printf("self %s\n", task->_self.c_str());
		//tcl.evalf("puts [%s units]", task->_self.c_str());
		tcl.evalf("delete %s", task->_self.c_str());
	}
	else {
		printf ("error, chlist.size == %d, chain %s\n", chlist.size(), this->name());
	}
	if (!chlist.empty())
		run_first();
}

void TChain::attach(TTask *task)
{
	bool empty = chlist.empty();
	chlist.push_back(task);

	if (empty)
		run_first();
}

void TChain::insert(TTask *task)
{
	if (chlist.empty())
		attach(task);
	else {
		//printf("before insert\n");
		//printf("size=%d\n", chlist.size());
		//printf("insert_it=%d\n", distance(insert_it, chlist.begin()));
		chlist.insert(insert_it, task);
		//printf("insert done\n");
	}
}

static class TaskListClass: public TclClass {
public:
	TaskListClass() : TclClass("MRPerf/Thread/TaskList") {}
	TclObject* create(int argc, const char*const* argv) {
		if (argc != 6)
			return NULL;
		double bw = atof(argv[4]);
		int num = atoi(argv[5]);
		if (num <= 0 || bw <= 0)
			return NULL;
		TTaskList *tl = new TTaskList(bw, num);

		//printf("%s %s %s %s\n", argv[0], argv[1], argv[2], argv[3]);
		if (strcmp(argv[0], argv[1]) != 0) {
			cout << "argv[0] != argv[1], " << argv[0] << " != " \
				<< argv[1] << endl;
		}
		strcpy(tl->self, argv[1]);
		return tl;
	}
} chain_class;

int TTaskList::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "next1task") == 0) {
			next_task();
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "insert") == 0) {
			TTask *newtask = (TTask *)(TclObject::lookup(argv[2]));
			if (!lst.empty())
			{
				//cout << "last_uid: " << last_uid << endl;
				tcl.evalf("$ns cancel %s", last_uid);
			}

			recalculate();

			list<TTask *>::iterator it;
			for (it = lst.begin(); it != lst.end(); it ++) {
				TTask *task = *it;
				if (task->units > newtask->units)
					break;
			}
			lst.insert(it, newtask);

			schedule_first();

			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

void TTaskList::update_share()
{
	int count = lst.size();
	if (count > num)
		share = 1.0 * num / count;
	else
		share = 1.0;

}

void TTaskList::recalculate()
{
	double now = ::Scheduler::instance().clock();
	if (now == last)
		return;

	update_share();

	list<TTask *>::iterator it;
	for (it = lst.begin(); it != lst.end(); it++)
	{
		TTask * task = *it;
		if (task->units < bw*share*(now-last) - g_epsilon)
		{
			cout << "+++++++++ error" << endl;
			cout << task->units << ", " << task->_command << endl;
			cout << task->units << " < " << bw << " * " << share \
				<< " * " << (now-last) << endl;
			cout << now << "     " << last << endl;
			cout << last_uid << endl;
		}
		task->units = task->units - bw*share*(now-last);
	}
}

void TTaskList::schedule_first()
{
	Tcl& tcl = Tcl::instance();
	TTask * task = lst.front();
	update_share();
	double delay = (task->units/share) / bw;

	last = ::Scheduler::instance().clock();
	//cout << delay << ", " << last << endl;
	if (delay <= 0) {
		if (delay < -g_epsilon)
			cout << "delay < 0: " << delay << endl;
		next_task();
	}
	else {
		tcl.evalf("$ns after %lf \"%s next1task\"", delay, self);
		strcpy(last_uid, tcl.result());
		//cout << tcl.result() << endl;
		//cout << last_uid << endl;
	}
}

void TTaskList::next_task()
{
	if (!lst.empty()) {
		recalculate();

		TTask * task = lst.front();
		if (task->units > g_epsilon || task->units < -g_epsilon) {
			cout << "******* " << task->units << ", should be 0" \
				<< endl;
			cout << "task " << task->units << ", " \
				<< task->_command << endl;
			cout << num << ", " << lst.size() << ", " << share \
				<< ", " << bw << endl;
		}

		lst.pop_front();

		if (!lst.empty())
			schedule_first();

		task->chain->next_task();
	}
	else
		cout << "------- error: run from an empty tasklist" << endl;
}

static class TTaskClass: public TclClass {
public:
	TTaskClass() : TclClass("MRPerf/Thread/Task") {}
	TclObject* create(int argc, const char*const* argv) {
		TTask *t = new TTask();
		t->_self = argv[1];
		return (t);
	}
} ttask_class;

int TTask::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (argc == 5) {
		if (strcmp(argv[1], "conf") == 0) {
			units = atof(argv[2]);
			_command = argv[3];
			type = atoi(argv[4]);

			if (units < 0 || _command.empty() ) {
				cout << "====== error" << endl;
				exit(1);
			}
			return TCL_OK;
		}
	}
	else if (argc == 2) {
		if (strcmp(argv[1], "units") == 0) {
			char buffer[256];
			sprintf(buffer, "%lg", units);
			tcl.result(buffer);
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}

} // namespace MRPerf

