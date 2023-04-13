#!/usr/bin/env python3

import argparse
import yaml
import subprocess
import os


def read_yaml():
    if os.path.exists('multipass.yaml'):
        with open(r'multipass.yaml') as file:
            instances = yaml.load(file, Loader=yaml.FullLoader)

        return instances['instances']

    else:
        print("Can't find multipass.yaml in current directory. Please run msl init")


def current_instance():
    return list(yaml.safe_load(subprocess.check_output("multipass list --format yaml", shell=True)).keys())


def virtual_instance(virtual_machines, config):
    if len(virtual_machines) > 0:
        virtual_machines = virtual_machines
    else:
        virtual_machines = list(config.keys())

    return virtual_machines


def launch(current, config, virtual_machines):
    launch_instances = []
    for vm in virtual_machines:
        if vm not in current and vm in config.keys():
            cmd = f"multipass launch --name {vm} {' '.join([f'--{key} {value}' for key, value in config[vm].items() if key != 'mounts'])}"
            if 'mounts' in config.keys():
                mount_cmd = f"  {' '.join([f'--mount {key}:{value}' for key, value in config[vm]['mounts'].items()])}"
                launch_instances.append(cmd + mount_cmd)
            else:
                launch_instances.append(cmd)
        else:
            print(f'{vm} is not defined in multipass.yaml or exists already')

    procs = [subprocess.Popen(instance, shell=True) for instance in launch_instances]
    for p in procs:
        p.wait()


def current_mounts(vm):
    current = yaml.safe_load(subprocess.check_output("multipass info --format yaml --all", shell=True))
    return {v['source_path']: k for k, v in current[vm][0]['mounts'].items()}


def config_mounts(vm, config):
    if 'mounts' in config.keys():
        return config[vm]['mounts']
    else:
        return {}


def mount(virtual_machines, config, current):
    for vm in virtual_machines:
        if vm in current:
            mounted = current_mounts(vm)
            mounts = config_mounts(vm, config)
            for key, value in mounts.items():
                if key in list(mounted.keys()):
                    if mounted[key] != value:
                        print(f'umount {mounted[key]} from {vm}')
                        subprocess.Popen(f'multipass umount {vm}:{mounted[key]}', shell=True)
                        print(f'mount {key} to {value} in to {vm}')
                        subprocess.Popen(f'multipass mount {key} {vm}:{value}', shell=True)
                else:
                    if os.path.exists(key):
                        print(f'mount {key} to {value} in to {vm}')
                        subprocess.Popen(f'multipass mount {key} {vm}:{value}', shell=True)
                    else:
                        print(f'host directory {key} does not exists')


def init():
    init_config = {"instances": {"primary": {"cpus": 1, "memory": "1G", "disk": "10G"}}}

    if not os.path.exists('multipass.yaml'):
        with open('multipass.yaml', 'w') as file:
            yaml.dump(init_config, file)
    else:
        print('multipass.yaml already exists')


def stop(virtual_machines, current, stop_all):
    if stop_all:
        cmd = f"multipass stop --all"
    else:
        cmd = f"multipass stop {' '.join([f'{vm}' for vm in virtual_machines if vm in current])}"
    subprocess.Popen(cmd, shell=True)


def delete(virtual_machines, current, delete_all):
    if delete_all:
        cmd = f"multipass delete --all"
    else:
        cmd = f"multipass delete {' '.join([f'{vm}' for vm in virtual_machines if vm in current])}"

    subprocess.Popen(cmd, shell=True)


def parser():
    arg_parser = argparse.ArgumentParser(description='msl: Multipass Subsystem Linux')
    command_parser = arg_parser.add_subparsers(dest='command', help='sub-command help')

    launch_parser = command_parser.add_parser('launch', help='Launch multiple Multipass Instances')
    launch_parser.add_argument('launch', nargs='*', help='Instances to launch')

    delete_parser = command_parser.add_parser('delete', help='Delete multiple Multipass Instances')
    delete_parser.add_argument('--all', action='store_true', default=False,
                               help='switch to delete all virtual machines')
    delete_parser.add_argument('delete', nargs='*', help='Instances to delete')

    stop_parser = command_parser.add_parser('stop', help='Stop multiple Multipass Instances')
    stop_parser.add_argument('--all', action='store_true', default=False, help='switch to stop all virtual machines')
    stop_parser.add_argument('stop', nargs='*', help='Instances to stop')

    mount_parser = command_parser.add_parser('mount', help='mount dictionaries to configured Multipass Instances')
    mount_parser.add_argument('mount', nargs='*', help='Instances to stop')

    init_parser = command_parser.add_parser('init', help='create multipass.yaml file in current directory')

    args = arg_parser.parse_args()

    return args


def main():
    args = parser()

    if args.command == "launch":
        vms = virtual_instance(config=read_yaml(), virtual_machines=args.launch)
        print(vms)
        launch(current=current_instance(), config=read_yaml(), virtual_machines=vms)
    elif args.command == "stop":
        vms = virtual_instance(config=read_yaml(), virtual_machines=args.stop)
        stop(virtual_machines=vms, current=current_instance(), stop_all=args.all)
    elif args.command == "delete":
        vms = virtual_instance(config=read_yaml(), virtual_machines=args.delete)
        delete(virtual_machines=vms, current=current_instance(), delete_all=args.all)
    elif args.command == "mount":
        vms = virtual_instance(config=read_yaml(), virtual_machines=args.mount)
        mount(current=current_instance(), config=read_yaml(), virtual_machines=vms)
    elif args.command == "init":
        init()
    else:
        print('Invalid command')


if __name__ == '__main__':
    main()
