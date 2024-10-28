package mapreduce

import (
	"log"
	"sync"
)

const (
	OPERATION_BUFFER = 100
)

// Schedules map operations on remote workers. This will run until InputFilePathChan
// is closed. If there is no worker available, it'll block.

func (master *Master) schedule(task *Task, proc string, filePathChan chan string) int {
	var wg sync.WaitGroup
	var totalOps int
	var counter int

	log.Printf("Scheduling %v operations\n", proc)

	operationChan := make(chan *Operation, OPERATION_BUFFER)
	doneCreatingOps := make(chan struct{})

	go func() {
		for filePath := range filePathChan {
			operation := &Operation{proc, counter, filePath}
			counter++
			wg.Add(1)
			operationChan <- operation
		}
		totalOps = counter
		close(operationChan)
		close(doneCreatingOps)
	}()

	for {
		select {
		case op, ok := <-operationChan:
			if ok {
				worker := <-master.idleWorkerChan

				go func(op *Operation) {
					master.runOperation(worker, op, &wg)
				}(op)
			}

		case op := <-master.retryOperationChan:
			wg.Add(1)
			worker := <-master.idleWorkerChan

			go func(op *Operation) {
				master.runOperation(worker, op, &wg)
			}(op)

		case <-doneCreatingOps:
			if len(operationChan) == 0 && len(master.retryOperationChan) == 0 {
				wg.Wait()
				log.Printf("%vx %v operations completed\n", totalOps, proc)

				return totalOps
			}
		}
	}
}

// runOperation start a single operation on a RemoteWorker and wait for it to return or fail.
func (master *Master) runOperation(remoteWorker *RemoteWorker, operation *Operation, wg *sync.WaitGroup) {

	var (
		err  error
		args *RunArgs
	)

	log.Printf("Running %v (ID: '%v' File: '%v' Worker: '%v')\n",
		operation.proc, operation.id, operation.filePath, remoteWorker.id)

	args = &RunArgs{operation.id, operation.filePath}
	err = remoteWorker.callRemoteWorker(operation.proc, args, new(struct{}))

	if err != nil {
		log.Printf("Operation %v '%v' Failed. Error: %v\n",
			operation.proc, operation.id, err)

		master.retryOperationChan <- operation
		master.failedWorkerChan <- remoteWorker
		wg.Done()
	} else {
		master.idleWorkerChan <- remoteWorker
		wg.Done()
	}
}
