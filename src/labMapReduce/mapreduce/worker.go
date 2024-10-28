package mapreduce

import (
	"log"
	"net"
	"net/rpc"
)

type Worker struct {
	id int

	// Network
	hostname       string
	masterHostname string
	listener       net.Listener
	rpcServer      *rpc.Server

	// Operation
	task *Task
	done chan bool

	// Induced failures
	taskCounter int
	nOps        int
}

// Call RPC Register on Master to notify that this worker is ready to receive operations.
func (worker *Worker) register() error {
	var (
		err   error
		args  *RegisterArgs
		reply *RegisterReply
	)

	log.Println("Registering with Master")

	args = new(RegisterArgs)
	args.WorkerHostname = worker.hostname

	reply = new(RegisterReply)

	err = worker.callMaster("Master.Register", args, reply)

	if err == nil {
		worker.id = reply.WorkerId
		worker.task.NumReduceJobs = reply.ReduceJobs
		log.Printf("Registered. WorkerId: %v (Settings = (ReduceJobs: %v))\n", worker.id, worker.task.NumReduceJobs)
	}

	return err
}

// acceptMultipleConnections will handle the connections from multiple workers.
func (worker *Worker) acceptMultipleConnections() error {
	var (
		err     error
		newConn net.Conn
	)

	log.Printf("Accepting connections on %v\n", worker.listener.Addr())

	for {
		newConn, err = worker.listener.Accept()

		if err == nil {
			go worker.handleConnection(&newConn)
		} else {
			log.Println("Failed to accept connection. Error: ", err)
			break
		}
	}

	log.Println("Stopped accepting connections.")
	return nil
}

// Handle a single connection until it's done, then closes it.
func (worker *Worker) handleConnection(conn *net.Conn) error {
	worker.rpcServer.ServeConn(*conn)
	(*conn).Close()
	return nil
}

// Connect to Master and call remote procedure.
func (worker *Worker) callMaster(proc string, args interface{}, reply interface{}) error {
	var (
		err    error
		client *rpc.Client
	)

	client, err = rpc.Dial("tcp", worker.masterHostname)
	if err != nil {
		return err
	}

	defer client.Close()

	err = client.Call(proc, args, reply)
	if err != nil {
		return err
	}

	return nil
}

// shouldFail will keep track of executed operations and return true when nOps operations
// have been executed (before or during operation)
func (worker *Worker) shouldFail(during bool) bool {
	if worker.nOps == 0 {
		return false
	}

	worker.taskCounter++
	return worker.taskCounter == worker.nOps
}
