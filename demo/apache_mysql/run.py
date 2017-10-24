import os
import yaml

from demo import Run

if __name__ == '__main__':
    # load yaml input
    with open('input.yml', 'r') as fh:
        config1 = yaml.load(fh)

    # tower config exist
    tower_cfg = '/etc/tower/tower_cli.cfg'
    if not os.path.isfile(tower_cfg):
        raise Exception('Req. configuration file %s is missing!' % tower_cfg)

    # load tower configuration file
    config2 = dict()
    with open(tower_cfg, 'r') as fh:
        for item in fh.readlines():
            val = item.split(':', 1)
            config2[val[0]] = val[1].strip()

    # create run object
    run = Run(config1, config2)

    # start
    run.go()
