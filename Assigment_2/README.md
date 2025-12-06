# Producer–Consumer Pattern with Thread Synchronization (Python)

##  Overview

This project implements the **classic Producer–Consumer concurrency pattern** using **Python threads**.  
It demonstrates how **multiple threads coordinate safely** using a **bounded blocking queue**, explicit **thread synchronization**, and the **wait/notify mechanism** implemented via `threading.Condition`.

The application simulates concurrent data transfer where:
- A **Producer thread** reads data from a source container
- A **Consumer thread** retrieves data from a shared queue
- Data is safely transferred to a destination container without race conditions

The project also includes:
- A custom blocking queue (to expose synchronization logic)
- Detailed runtime logging showing thread interaction
- Comprehensive unit tests validating concurrent behavior

### Why I implemented a custom Blocking Queue

Instead of using Python’s built-in `queue.Queue`, I implemented a **custom bounded blocking queue** to explicitly demonstrate the Producer–Consumer synchronization mechanics.

This approach allows clear visibility into:
- Mutual exclusion using `threading.Lock`
- Blocking behavior using `Condition.wait()` when the queue is full or empty
- Thread coordination using `Condition.notify()` when state changes occur

While `queue.Queue` is appropriate for production systems, implementing the queue manually provides deeper insight into concurrency primitives and makes synchronization logic transparent, which is valuable for learning, interviews, and system design discussions.

---

## Project Structure
```bash
producer-consumer-python/
│
├── blocking_queue.py          # Thread-safe bounded blocking queue
├── producer_consumer.py       # Producer & Consumer implementation
├── test_producer_consumer.py  # Unit tests (unittest framework)
├── requirements.txt           # Python version constraints
└── README.md                  # Project documentation
```

## 1. Getting Started

### Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
```
### Install dependencies

```bash
pip install -r requirements.txt
```
---

### Run Assignment 1

```bash
cd assignment1
python producer_cosumer.py
```

#### Sample Console Output

The following execution log demonstrates the real-time interaction between the Producer and Consumer threads using a custom bounded blocking queue. Timestamps and thread names are included to make the thread execution and synchronization behavior clearly observable. Due to thread scheduling, log ordering may vary between runs; however, all items are processed safely and in FIFO order.


```text
21:20:41 [MainThread] INFO - Initializing Producer-Consumer pipeline
21:20:41 [ProducerThread] INFO - Producer started
21:20:41 [ProducerThread] INFO - Producing item: 1
21:20:41 [ConsumerThread] INFO - Consumer started
21:20:41 [ProducerThread] INFO - Item 1 added to queue
21:20:41 [ConsumerThread] INFO - Consuming item: 1
21:20:41 [ProducerThread] INFO - Producing item: 2
21:20:41 [ProducerThread] INFO - Item 2 added to queue
21:20:41 [ProducerThread] INFO - Producing item: 3
21:20:41 [ProducerThread] INFO - Item 3 added to queue
21:20:41 [ProducerThread] INFO - Producing item: 4
21:20:41 [ProducerThread] INFO - Item 4 added to queue
21:20:41 [ProducerThread] INFO - Producing item: 5
21:20:41 [ConsumerThread] INFO - Consuming item: 2
21:20:41 [ConsumerThread] INFO - Consuming item: 3
21:20:41 [ConsumerThread] INFO - Consuming item: 4
21:20:41 [ProducerThread] INFO - Item 5 added to queue
21:20:41 [ProducerThread] INFO - Producer sending SENTINEL and shutting down
21:20:41 [ConsumerThread] INFO - Consuming item: 5
21:20:41 [ConsumerThread] INFO - Consumer received SENTINEL, exiting
21:20:41 [ConsumerThread] INFO - Consumer stopped cleanly
21:20:41 [MainThread] INFO - Pipeline execution completed
21:20:41 [MainThread] INFO - Final destination container: [1, 2, 3, 4, 5]
```


### Run tests

```bash
python -m unittest test_producer_consumer.py
```
