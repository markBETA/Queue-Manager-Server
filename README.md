# Queue-Manager-Server
This server manages a queue for one printer and allow the registered users to send directly files to the queue.
The printer, if is connected and the hot ends and materials configuration meets the files in the queue, will automatically pull the files from the queue and print them.

## How to clone this repository
This repository has submodules. That means that you need to fetch the submodules too.
  - git clone https://github.com/markBETA/Queue-Manager-Server.git
  - git submodule update --init --recursive


## Configuring the server
To configure the server edit the file **instance/config.py**

## Running the server
You have basically two options to run the server
  - Executing the batch file **run_prod.sh**
  - Running the python script **run.py**
