# Multipass Wrapper

This repository contains a simple wrapper written in Python3.

### Why was it created?

Vagrant is not native on Apple Silicon, so I had to switch to a different solution.
Multipass was this solution, but I didn't like that there was no support for a configuration file, simular to the Vagrantfile in Vagrant.
Which is also currently sadly not planed.
So I decided to create simple a Python Wrapper, so I can configure my development environment in Multipass using a configfile.

### How to use it?

```bash 
msl.py init
```
Initialize the current directory and create a file named `multipass.yaml`

```bash
msl.py launch
```
Launch all instances defined in `multipass.yaml`.


```bash
msl.py stop
```
Stop all defined currently running Multipass instances.


```bash
msl.py delete
```
Delete all defined currently running Multipass instances.

```bash
msl.py mount
```
Mount all directories defined under the key `mounts` for each instance in `multipass.yaml`.

The subcommands `launch`,`mount`,`stop` and `delete` also accept, defined machines as arguments to limit.
e.g:
```bash
msl.py launch primary
```
This launch command would create the instance primary, as long as she is defined in `multipass.yaml`
Also `delete` and `stop` accept a argument called `--all`, when this is used the wrapper will attempt to 
`stop` or `delete` all machines currently running.

### `Multipass.yaml` example

```yaml
instances:
  primary:
     cpus: 2
     disk: 20G
     memory: 4G
     cloud-init: ./cloud-init.yaml
     mounts:
       path/on/the/host: path/where/to/mount/in/vm
       path/on/the/host2: path2/where/to/mount/in/vm
```



## ToDo

-[ ] Write Tests 