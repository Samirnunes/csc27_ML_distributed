// common_rpc.go defined all the parameters used in RPC between
// master and workers
package mapreduce

type RegisterArgs struct {
	WorkerHostname string
}

type RegisterReply struct {
	WorkerId   int
	ReduceJobs int
}

type RunArgs struct {
	Id       int
	FilePath string
}
