package mapreduce

import (
	"log"
)

// RPC - Register
// Procedure that will be called by workers to register within this master.
func (master *Master) Register(args *RegisterArgs, reply *RegisterReply) error {
	var (
		newWorker *RemoteWorker
	)
	log.Printf("Registering worker '%v' with hostname '%v'", master.totalWorkers, args.WorkerHostname)

	master.workersMutex.Lock()

	newWorker = &RemoteWorker{master.totalWorkers, args.WorkerHostname, WORKER_IDLE}
	master.workers[newWorker.id] = newWorker
	master.totalWorkers++

	master.workersMutex.Unlock()

	master.idleWorkerChan <- newWorker

	*reply = RegisterReply{newWorker.id, master.task.NumReduceJobs}
	return nil
}
