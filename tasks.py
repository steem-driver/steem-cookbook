import os

from invoke import Collection, tasks
from invoke.util import LOG_FORMAT

from steem import command as steem_cmd
from action.vote import command as vote_cmd
from action.info import command as info_cmd
from recipe import command as recipe_cmd


def add_tasks_in_module(mod, ns):
    functions = [(name, val) for name, val in mod.__dict__.items() if callable(val)]
    for (name, method) in functions:
        # only add the method if it's of type invoke.tasks.Task
        if type(method) == tasks.Task:
            ns.add_task(method, name)
    return ns

steem_ns = add_tasks_in_module(steem_cmd, Collection('steem'))
vote_ns = add_tasks_in_module(vote_cmd, Collection('vote'))
info_ns = add_tasks_in_module(info_cmd, Collection('info'))
recipe_ns = add_tasks_in_module(recipe_cmd, Collection('recipe'))

ns = Collection(
    steem_ns,
    vote_ns,
    info_ns,
    recipe_ns
)

ns.configure({'conflicted': 'default value'})
