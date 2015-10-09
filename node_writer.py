### just a template, not to be run alone

import bpy
obj = bpy.context.scene.objects.active
node_tree = '+ntree_path+'
nodes = node_tree.nodes

def create_node(node_tree, name, node_type, posx, posy, operation = None, prop = None, prop_default = None):
    node = node_tree.nodes.new(type=node_type)  # create puff node\n")
    node.location = (posx, posy)
    node.name = name
    node.label = name
    if operation is not None:
        node.operation = operation
        return node

def create_node_group(node_tree, name, node_type, posx, posy):
    group_data = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    node = create_node(node_tree, name, 'ShaderNodeGroup', posx, posy)
    node.node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    return node

def add_group_output(node_tree, group_node_output, input_type, input_name):
    if input_type is not 'NodeSocketVirtual':
        #node = node_tree.nodes[group_node_output]
        node_tree.outputs.new(input_type, input_name)

def add_group_input(node_tree, group_node_input, output_type, output_name):
    if output_type is not 'NodeSocketVirtual':
        #node = node_tree.nodes[group_node_output]
        node_tree.inputs.new(output_type, output_name)

def config_node_inputs(node_tree, node_name, input_socket, input_value):
    node = node_tree.nodes[node_name]
    node.inputs[input_socket].default_value = input_value