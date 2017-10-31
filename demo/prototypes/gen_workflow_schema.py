import yaml
import sys
TESTFILE = "descriptor_test1.yaml"


def create_schema(tasklist, filename="filename-uuid.yaml", finalcleanup=None):
    data = []
    tasklen = len(tasklist)
    for index, task in enumerate(tasklist):
        mydict = {}
        mydict["job_template"] = task["task"]
        notatlastitem = index < tasklen - 1
        if notatlastitem:
            mydict["success"] = []
        if finalcleanup:
            mydict["failure"] = [finalcleanup]
        if "failure" in task:
            if "failure" in mydict and mydict["failure"]:
                mydict["failure"].append(task["failure"])
            else:
                mydict["failure"] = [task["failure"]]
        if index == 0:
            data.append(mydict)
            last_ref = data[0]["success"]
        else:
            last_ref.append(mydict)
            if notatlastitem:
                last_ref = last_ref[0]["success"]

    # remove the last "success"
    tasklen = len(tasklist)
    print tasklen

    with open(filename, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


# Desc: -name t1
#        host h1, h2
#       -name t2
#        host h2
#         after t3
#       - name t3
#          host: h2, h3
#

# convert to schema

# - job_template: SYS_RELEASE_common
#   failure:
#   - job_template: SYS_RELEASE_vipatel
#   success:
#   - job_template: force_failure
#     failure:
#     - job_template: SYS_RELEASE_vipatel
#
#

# Read in the data
stream = open(TESTFILE, "r")
descriptor_data = yaml.load(stream)
orchestrate_list = descriptor_data["orchestrate"]
finalcleanup = None
# Step 1: -> get a list of the templates and hosts it can execute on.
# [{"task":"t1", "hosts":["h1", "h2"]},
#  {"task":"t2", "hosts":["h2"]},
#  {"task":"t3", "hosts": ["h2","h3"]

task_list = []
# get the task list
for orchestrate_data in orchestrate_list:
    task_dict = {}
    task_dict["task"] = orchestrate_data["name"]
    task_dict["hosts"] = orchestrate_data["hosts"].strip().split(",")
    if "on_failure" in orchestrate_data:
        task_dict["failure"] = orchestrate_data["on_failure"]
    if "cleanup" in orchestrate_data:
        task_dict["cleanup"] = orchestrate_data["cleanup"]
    if "cleanup_task" in orchestrate_data and orchestrate_data["cleanup_task"]:
        continue
    task_list.append(task_dict)

print "Simple unfinished task list"
print task_list

taskitems = len(task_list)
current_order = list(range(taskitems))
print "Current Order"
print current_order

#
# Step 2: Reorder based on "after"
# task "t2" must happen after "t3" for "h2"  index 2 must happen after index 4
# look for index of t3 for h2 and if index is > t2 for h2 remove t2
#
# [{"task":"t1", "hosts":["h1", "h2"]},
#  {"task":"t3", "hosts": ["h2","h3"]
#
# and add t2 after t3
# [{"task":"t1", "hosts":["h1", "h2"]},
#  {"task":"t3", "hosts": ["h2","h3"],
#  {"task":"t2", "hosts":["h2"]}

after_list = []
# look for after
for orchestrate_data in orchestrate_list:
    if "after" in orchestrate_data and orchestrate_data["after"]:
        after_dict = {}
        after_dict["before"] = orchestrate_data["after"]
        after_dict["after"] = orchestrate_data["name"]
        after_list.append(after_dict)

print after_list

if after_list:
    for order in after_list:
        beforeindex = 0
        afterindex = 0
        # check index of list items
        for index, task in enumerate(task_list):
            if task["task"] == order["before"]:
                beforeindex = index
            if task["task"] == order["after"]:
                afterindex = index
        if beforeindex and afterindex:
            if int(afterindex) > int(beforeindex):
                print "order is correct, doing nothing"
            else:
                print "need to modify the order."
                order = current_order.remove(afterindex)
                position = current_order.index(beforeindex) + 1
                current_order.insert(position, afterindex)
                print "new order"
                print current_order
        else:
            print "Error defining your order: {}".format(order)
            sys.exit(0)

# update the tasklist
task_list = [task_list[i] for i in current_order]
print "updated task list"
print task_list

# Step 3: Reorder based on "before"
# didn't see this as being needed

# Step 4: Remove cleanup task and send pass it to schema creation fn separately
for task in task_list:
    if "cleanup" in task and task["cleanup"]:
        task_list.remove(task)
        finalcleanup = task["task"]

# default is serial as the list is defined, w/on_success implied.
create_schema(task_list,
              filename="filename-uuid.yaml",
              finalcleanup=finalcleanup)

# Following is automaton research:
# Step 1: translate to a list of actions hosts and tasks
# [{host: h1, task: t1},
#  {host: h2, task: t1},
#  {host: h2, task: t2},
#  {host: h2, task: t3}
#  {host: h3, task: t3}]

# Step through before, after, and always and order [after t3]
# [{host: h1, task: t1},
#  {host: h2, task: t1},
#  {host: h2, task: t3},
#  {host: h3, task: t3},
#  {host: h2, task: t2},
#  ]

# class HostTasks(Automaton):
#     states = "t1h1", "t1h2", "t2h2", "t3h2", "t3h3"
#     on_success = Event("t3h2","t2h2")
#
# stategraph(HostTasks, fmt=None)

# def gen_schema():
#     """
#     function that will take a descriptor file, and create a schema file,
#     which determines the order of execution
#     :return:
#     """

# fsm = Fysom({'initial':'t1',
#             'events':[
#                 {'name':'register', 'src':]})
# print fsm.current
# print fsm.__doc__
