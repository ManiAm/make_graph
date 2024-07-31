#!/usr/bin/env python3

""" Plotting make dependencies """

__author__  = "Mani Amoozadeh"

import os
import sys
import pydot
import networkx as nx

class Target:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.children = []
        self.level = 0
        self.must_remake = False


class Graph:
    def __init__(self):
        self.root = None
        self.targets = []
        self.target_count = 0
        self.id_generator = 0


def read_line(file):
    line = file.readline()
    if not line:
        return None, 0
    line = line.strip()
    level = len(line) - len(line.lstrip())
    return line, level


def target_name(line):
    b = line.find('`')
    if b == -1:
        b = line.find("'")
    e = line.find("'", b + 1)
    if b == -1 or e == -1:
        raise ValueError(f"Cannot get target name in '{line}'")
    return line[b + 1:e]


def get_target(graph, name):
    # return the target if exists
    for target in graph.targets:
        if target.name == name:
            return target
    # otherwise, create it
    target = Target(graph.id_generator + 1, name)
    graph.id_generator += 1
    graph.targets.append(target)
    graph.targets.sort(key=lambda t: t.name)
    graph.target_count += 1
    return target


def add_child(target, child):
    if child not in target.children:
        target.children.append(child)
        target.children.sort(key=lambda t: t.name)


def scan_graph(graph, root, file, level):
    while True:
        line, i_level = read_line(file)
        if line is None: # EOF
            break
        if line.startswith("Considering target file"):
            t_name = target_name(line)
            child = get_target(graph, t_name)
            if level + 1 >= i_level:
                add_child(root, child)
                scan_graph(graph, child, file, i_level + 1)
        elif line.startswith("Must remake target "):
            t_name = target_name(line)
            get_target(graph, t_name).must_remake = True
        elif line.startswith("Pruning file "):
            t_name = target_name(line)
            child = get_target(graph, t_name)
            add_child(root, child)
        elif ( (line.startswith("Finished prerequisites of target file ") or line.endswith("was considered already.")) and (level + 1 >= i_level) ):
            t_name = target_name(line)
            if t_name != root.name:
                raise ValueError(f"expected {root.name} got {line}")
            break


def create_graph(graph_root):

    G = nx.DiGraph()

    def add_edges(target):
        for child in target.children:
            G.add_edge(target.name, child.name)
            add_edges(child)

    add_edges(graph_root)

    mapping = {node: f'"{node}"' for node in G.nodes()}
    G = nx.relabel_nodes(G, mapping)

    return G


def plot_graph(G, plot_dir):

    filename = "make"
    file_dot = os.path.join(plot_dir, f"{filename}.dot")
    file_png = os.path.join(plot_dir, f"{filename}.png")

    nx.drawing.nx_pydot.write_dot(G, file_dot)

    (graph,) = pydot.graph_from_dot_file(file_dot)
    graph.write_png(file_png)


def main():

    graph = Graph()

    graph.root = get_target(graph, "<ROOT>")

    num_args = len(sys.argv) - 1

    if num_args == 0:
        scan_graph(graph, graph.root, sys.stdin, 0)
    elif num_args == 1:
        with open(sys.argv[1], 'r') as f:
            scan_graph(graph, graph.root, f, 0)
    else:
        print("Invalid number of arguments.")
        sys.exit(2)

    cwd = os.getcwd()
    G = create_graph(graph.root)
    plot_graph(G, cwd)


if __name__ == "__main__":

    main()
