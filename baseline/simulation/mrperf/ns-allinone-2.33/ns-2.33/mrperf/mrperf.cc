#include <assert.h>
#include <stdlib.h>

#include "agent.h"
#include "app.h"
#include "mrperf.h"
#include "datalayout.h"
#include "thread.h"

namespace MRPerf {


static class MapTaskClass: public TclClass {
public:
	MapTaskClass() : TclClass("MRPerf/MapTask") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new MapTask);
	}
} maptask_class;
 
int MapTask::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "worker") == 0) {
			tcl.result(worker->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "chunk") == 0) {
			tcl.result(chunk->string());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "disk") == 0) {
			tcl.result(disk->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "finish") == 0) {
			chunk->finished = 1;
#if 0
			// seems to cause segmentation fault
			TMSC& msc = DataLayout::instance().string_to_chunk;
			msc.erase(chunk->string_);
			delete chunk;
#endif

			//for worker in chunk->workers(), ...

			return TCL_OK;
		}
		else if (strcmp(argv[1], "cpp_fail") == 0) {
			chunk->finished = 0;
			chunk->get_workers().erase(worker);
			//printf("number of workers: %d\n", chunk->get_workers().size());
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "def-schedule") == 0) {
			Node *node = (Node *)(TclObject::lookup(argv[2]));
			Scheduler *sched = &Scheduler::instance();
			if (node == NULL) {
				tcl.add_errorf("Wrong node name %s", argv[2]);
				return TCL_ERROR;
			}
			MapTask *ret = sched->schedule(this, node);
			if (ret == NULL)
				tcl.result("");
			else
				tcl.result(this->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "remote-schedule") == 0) {
			Node *node = (Node *)(TclObject::lookup(argv[2]));
			Scheduler *sched = &Scheduler::instance();
			if (node == NULL) {
				tcl.add_errorf("Wrong node name %s", argv[2]);
				return TCL_ERROR;
			}
			MapTask *ret = sched->remote_schedule(this, node);
			if (ret == NULL)
				tcl.result("");
			else
				tcl.result(this->name());
			return TCL_OK;
		}
	}
	else if (argc == 4) {
		if (strcmp(argv[1], "fixed-schedule") == 0) {
			Node *worker = (Node *)(TclObject::lookup(argv[2]));
			Node *host = (Node *)(TclObject::lookup(argv[3]));
			if (worker == NULL || host == NULL) {
				tcl.add_errorf("Wrong node name %s or %s", \
						argv[2], argv[3]);
				return TCL_ERROR;
			}
			Scheduler *sched = &Scheduler::instance();
			MapTask *ret = sched->fixed_schedule(this,worker,host);
			if (ret == NULL)
				tcl.result("");
			else
				tcl.result(this->name());
			return TCL_OK;
		}
	}
#if 0
	if (argc == 3) {
		if (strcmp(argv[1], "schedule") == 0) {
			Node *node = (Node *)(TclObject::lookup(argv[2]));
			Chunk *chunk;
			if (node == NULL) {
				tcl.add_errorf("Wrong node name %s", argv[2]);
				return TCL_ERROR;
			}
			task = schedule(node);
			if (chunk == NULL)
				tcl.result("");
			else
				tcl.result(task->string());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "find") == 0) {
			// TODO: this is not correct for multiple replicas.
			Chunk* chunk = get_chunk(argv[2]);
			set<Node *>& s = chunk->get_hosts();
			Node * first = *(s.begin());
			tcl.result(first->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "finish") == 0) {
			Chunk* chunk = get_chunk(argv[2]);
			chunk->finished = 1;

			//for worker in chunk->workers(), ...

			return TCL_OK;
		}
	}
#endif

	return (TclObject::command(argc, argv));
}

void MapTask::dispatch(Node *n, Chunk *c, Disk *d)
{
	c->get_workers().insert(n);
	//n->working_on = c;
	worker = n;
	chunk = c;
	disk = d;
}

static class ReduceTaskClass: public TclClass {
public:
	ReduceTaskClass() : TclClass("MRPerf/ReduceTask") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new ReduceTask);
	}
} reducetask_class;
 
int ReduceTask::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (argc == 2) {
		if (strcmp(argv[1], "worker") == 0) {
			tcl.result(worker->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "disk") == 0) {
			tcl.result(disk->name());

		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "def-schedule") == 0) {
			Node *node = (Node *)(TclObject::lookup(argv[2]));
			Scheduler *sched = &Scheduler::instance();
			if (node == NULL) {
				tcl.add_errorf("Wrong node name %s", argv[2]);
				return TCL_ERROR;
			}
			ReduceTask *ret = sched->reducer_schedule(this, node);
			if (ret == NULL)
				tcl.result("");
			else
				tcl.result(this->name());
			return TCL_OK;
		}
	}

	return (TclObject::command(argc, argv));
}


static class SchedulerClass: public TclClass {
public:
	SchedulerClass() : TclClass("MRPerf/Scheduler") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new Scheduler);
	}
} scheduler_class;

Scheduler * Scheduler::instance_;

int Scheduler::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();
	if ((instance_ == 0) || (instance_ != this))
		instance_ = this;

	//fprintf(stderr, "in scheduler command()\n");
	//fprintf(stderr, "%d, %s, %s\n", argc, argv[1], argv[2]);

	if (argc == 3) {
		if (strcmp(argv[1], "read-metadata") == 0) {
			int chunks = DataLayout::instance().read_xml(argv[2]);
			if (chunks < 0) {
				tcl.add_errorf("Data Layout parse error");
				return TCL_ERROR;
			}
			char buf[16];
			sprintf(buf, "%d", chunks);
			tcl.result(buf);
			return TCL_OK;
		}
#if 0
		else if (strcmp(argv[1], "schedule") == 0) {
			// deprecated on 2008.7.11, use MapTask schedule instead
			Node *node = (Node *)(TclObject::lookup(argv[2]));
			MapTask *task;
			if (node == NULL) {
				tcl.add_errorf("Wrong node name %s", argv[2]);
				return TCL_ERROR;
			}
			MapTask *ret = schedule(task, node);
			if (ret == NULL)
				tcl.result("");
			else
				tcl.result(task->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "find") == 0) {
			// TODO: this is not correct for multiple replicas.
			Chunk* chunk = get_chunk(argv[2]);
			set<Node *>& s = chunk->get_hosts();
			Node * first = *(s.begin());
			tcl.result(first->name());
			return TCL_OK;
		}
		else if (strcmp(argv[1], "finish") == 0) {
			// obseleted on 2008.7.11. use MapTask finish instead.
			Chunk* chunk = get_chunk(argv[2]);
			chunk->finished = 1;

			//for worker in chunk->workers(), ...

			return TCL_OK;
		}
#endif
	}

	return (TclObject::command(argc, argv));
}

MapTask * Scheduler::remote_schedule(MapTask *task, Node *node)
{
	TSC scit;
	TMSC& msc = DataLayout::instance().string_to_chunk;
	//fprintf(stderr, "%p %p\n", msc.begin(), msc.end());
	Disk *d = *(node->disks.begin());
	for (scit = msc.begin(); scit != msc.end(); scit++)
	{
		Chunk* c = const_cast<Chunk *>((*scit).second);
		if (c == NULL)
			fprintf(stderr, "Error: NULL on %s\n", scit->first.c_str());

		if (c->get_host_disks().find(d) != c->get_host_disks().end())
			continue;

		if (c->finished == 0 && c->get_workers().empty())
		{
			Disk * d = replica_selector(node, c);
			task->dispatch(node, c, d);
			fprintf(stderr, "%s: scheduled to %s, on %s\n", c->string(),
						node->string_.c_str(),
						d->host->string_.c_str());
			return task;
		}
	}

	set<Chunk *>::iterator cit;
	vector<Disk *>::iterator dit;
	for (dit = node->disks.begin(); dit != node->disks.end(); dit++)
	for (cit = (*dit)->chunks.begin(); cit != (*dit)->chunks.end(); cit++)
	{
		Chunk *c = *cit;

		if (c->finished == 0 && c->get_workers().empty())
		{
			Disk * d = remote_replica_selector(node, c);
			task->dispatch(node, c, d);
			fprintf(stderr, "%s: scheduled to %s, on %s (could be local)\n", \
						c->string(), node->string_.c_str(), \
						d->host->string_.c_str());
			//fprintf(stderr, "task %p. chunk %p\n", task, c);
			return task;
		}
	}

	// all chunks finished.
	return NULL;
}

MapTask * Scheduler::fixed_schedule(MapTask *task, Node *worker, Node *host)
{
	TSC scit;
	TMSC& msc = DataLayout::instance().string_to_chunk;
	//fprintf(stderr, "%p %p\n", msc.begin(), msc.end());
	Disk *d = *(host->disks.begin());
	for (scit = msc.begin(); scit != msc.end(); scit++)
	{
		Chunk* c = const_cast<Chunk *>((*scit).second);
		if (c == NULL)
			fprintf(stderr, "Error: NULL on %s\n", scit->first.c_str());

		if (c->finished != 0 || !c->get_workers().empty() )
			continue;

		// put chunk on host
		set<Disk *> *disks = &c->get_host_disks();
		if (disks->find(d) == disks->end())
		{
			disks->insert(d);
			d->chunks.insert(c);
		}

		task->dispatch(worker, c, d);
		fprintf(stderr, "%s: fixed scheduled to %s, on %s\n", \
			c->string(), worker->string_.c_str(), \
			host->string_.c_str());
		return task;
	}

	// all chunks finished.
	return NULL;
}

MapTask * Scheduler::schedule(MapTask *task, Node *node)
{
	//fprintf(stderr, "in schedule(), node %s\n", node->string_.c_str());

	//node->dump();

	set<Chunk *>::iterator cit;
	vector<Disk *>::iterator dit;
	for (dit = node->disks.begin(); dit != node->disks.end(); dit++)
	for (cit = (*dit)->chunks.begin(); cit != (*dit)->chunks.end(); cit++)
	{
		Chunk *c = *cit;

#if 0
		//if (strcmp(c->string(), "file_00000000:0:0:131072") == 0)
		{
			TMSC& msc = DataLayout::instance().string_to_chunk;
			TSC scit;
			scit = msc.find(c->string());
			//fprintf(stderr, "0:0 again, %p, in msc %p\n", c, scit->second);
			if (c != scit->second)
			{
				fprintf(stderr, "chunk %s, node %s, disk %d\n", c->string(), node->string(), (*dit)->id);
			}
		}
#endif
		if (c->finished == 0 && c->get_workers().empty())
		{
			task->dispatch(node, c, *dit);
			fprintf(stderr, "%s: scheduled to %s locally\n", c->string(),
						node->string_.c_str());
			//fprintf(stderr, "task %p. chunk %p\n", task, c);
			return task;
		}
	}

	// we reach here because node cannot find a local chunk to work on.
	// do a scan on msc, and find any available chunk.
	TSC scit;
	TMSC& msc = DataLayout::instance().string_to_chunk;
	//fprintf(stderr, "%p %p\n", msc.begin(), msc.end());

	//TODO: clearly I can skip all finished chunks. Maybe managing them
	//	in a separate structure would be better/faster.
	//search for rack-local chunks
	for (scit = msc.begin(); scit != msc.end(); scit++)
	{
		Chunk* c = const_cast<Chunk *>((*scit).second);
		if (c == NULL)
			fprintf(stderr, "Error: NULL on %s\n", \
					scit->first.c_str());

		if (c->finished == 0 && c->get_workers().empty())
		{
			//Disk * d = replica_selector(node, c);
			Disk * d = node->rack_local(c);
			if (d == NULL)
				continue;
			task->dispatch(node, c, d);
			fprintf(stderr, "%s: rack local to %s, on %s\n", \
					c->string(),
					node->string_.c_str(),
					d->host->string_.c_str());
			return task;
		}
	}

	// rack-local not found. any chunk would be fine.
	for (scit = msc.begin(); scit != msc.end(); scit++)
	{
		Chunk* c = const_cast<Chunk *>((*scit).second);
		if (c == NULL)
			fprintf(stderr, "Error: NULL on %s\n", \
					scit->first.c_str());

		if (c->finished == 0 && c->get_workers().empty())
		{
			Disk * d = replica_selector(node, c);
			task->dispatch(node, c, d);
			fprintf(stderr, "%s: rack remote to %s, on %s\n", \
					c->string(),
					node->string_.c_str(),
					d->host->string_.c_str());
			return task;
		}
	}

	// all chunks finished.
	return NULL;
}

Disk *Scheduler::replica_selector(Node *n, Chunk *c)
{
	static int i = 0;
	(void)n;

	int r = i % (c->get_host_disks().size());
	i++;
	set<Disk*>::iterator dit = c->get_host_disks().begin();
	for (int j = 0; j < r; j++)
		dit ++;

	return *dit;

}

Disk *Scheduler::remote_replica_selector(Node *n, Chunk *c)
{
	set<Disk*>::iterator dit;
	for (dit = c->get_host_disks().begin(); dit != c->get_host_disks().end(); dit++) {
		if (*dit != *(n->disks.begin()))
			break;
	}
	return *dit;
}

ReduceTask * Scheduler::reducer_schedule(ReduceTask *task, Node *node)
{
	Disk *d = *(node->disks.begin());
	task->worker = node;
	task->disk = d;
	return task;
}


static class DequeClass: public TclClass {
public:
	DequeClass() : TclClass("MRPerf/Deque") {}
	TclObject* create(int argc, const char*const* argv) {
		return (new Deque);
	}
} deque_class;
 
int Deque::command(int argc, const char*const* argv) {
	Tcl& tcl = Tcl::instance();

	if (1) {
	// put pointers to TclObject in std::deque
	if (argc == 2) {
		if (strcmp(argv[1], "pop_back") == 0) {
			TclObject *obj = obj_deque.back();
			if (obj == NULL) {
				tcl.resultf("pop obj from an empty deque\n");
				return TCL_ERROR;
			}
			obj_deque.pop_back();
			tcl.result(obj->name());
			return TCL_OK;
		} else if (strcmp(argv[1], "pop_front") == 0) {
			TclObject *obj = obj_deque.front();
			if (obj == NULL) {
				tcl.resultf("pop obj from an empty deque\n");
				return TCL_ERROR;
			}
			obj_deque.pop_front();
			tcl.result(obj->name());
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "push_back") == 0) {
			TclObject *obj = TclObject::lookup(argv[2]);
			if (obj == NULL) {
				tcl.add_errorf("Wrong object name %s", argv[2]);
				return TCL_ERROR;
			}
			obj_deque.push_back(obj);
			return TCL_OK;
		} else if (strcmp(argv[1], "push_front") == 0) {
			TclObject *obj = TclObject::lookup(argv[2]);
			if (obj == NULL) {
				tcl.add_errorf("Wrong object name %s", argv[2]);
				return TCL_ERROR;
			}
			obj_deque.push_front(obj);
			return TCL_OK;
		}
	}
	} else {
	// put std::string in std::deque
	if (argc == 2) {
		if (strcmp(argv[1], "pop_back") == 0) {
			std::string &obj = str_deque.back();
#if 0
			if (obj == NULL) {
				tcl.resultf("pop obj from an empty deque\n");
				return TCL_ERROR;
			}
#endif
			str_deque.pop_back();
			tcl.result(obj.c_str());
			delete &obj;
			return TCL_OK;
		} else if (strcmp(argv[1], "pop_front") == 0) {
			std::string &obj = str_deque.front();
#if 0
			if (obj == NULL) {
				tcl.resultf("pop obj from an empty deque\n");
				return TCL_ERROR;
			}
#endif
			str_deque.pop_front();
			tcl.result(obj.c_str());
			delete &obj;
			return TCL_OK;
		}
	}
	else if (argc == 3) {
		if (strcmp(argv[1], "push_back") == 0) {
			std::string *obj = new std::string(argv[2]);
			str_deque.push_back(*obj);
			return TCL_OK;
		} else if (strcmp(argv[1], "push_front") == 0) {
			std::string *obj = new std::string(argv[2]);
			str_deque.push_front(*obj);
			return TCL_OK;
		}
	}
	} // end if-else std::string or TclObject*

	return (TclObject::command(argc, argv));
}


} // namespace MRPerf

