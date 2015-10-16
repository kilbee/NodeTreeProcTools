import bpy

def create_node(node_tree, node_num, name, node_type, operation = None, blend_type = None):
    node = node_tree.nodes.new(type=node_type)    
    node.name = name
    node.label = name
    if operation is not None:
        node.operation = operation
    if blend_type is not None:
        node.blend_type = blend_type
    return node

def config_node(node_tree, node_num, posx, posy, dim_x, dim_y, is_muted, is_hidden, custom_color = None):
    node = node_tree.nodes[node_num]
    node.location = (posx, posy)
    node.mute = is_muted
    node.hide = is_hidden
    try:
        node.width = dim_x
        node.height = dim_y
    except:
        pass
    if custom_color is not None:
        node.use_custom_color = True
        node.color = custom_color

def create_node_group(name):
    group_data = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    return group_data

def add_group_output(node_tree, input_type, input_name):
    if input_type is not 'NodeSocketVirtual':
        node_output = node_tree.outputs.new(input_type, input_name)

def add_group_input(node_tree, output_type, output_name):
    if output_type is not 'NodeSocketVirtual':
        node_input = node_tree.inputs.new(output_type, output_name)
    return node_tree.id_data.name

def config_node_inputs(node_tree, node_name, input_socket, input_value):
    node = node_tree.nodes[node_name]
    node.inputs[input_socket].default_value = input_value

def config_group_node_input(node_group, input_socket, input_value, input_min=None, input_max=None):
    node_group.inputs[input_socket].default_value = input_value
    if input_min is not None:
        node_group.inputs[input_socket].min_value = input_min
    if input_max is not None:
        node_group.inputs[input_socket].max_value = input_max


