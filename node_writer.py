import bpy
#obj = bpy.context.scene.objects.active
#node_tree = '+ntree_path+'
#nodes = node_tree.nodes

def config_node(node_tree, name, node_type, posx, posy, prop = None, prop_default = None):
	node = node_tree.nodes.new(type=node_type)  # create puff node\n")
    node.location = (posx, posy)
    node.name = name
    tnode.label = name
    return node

def create_node_group(node_tree, name, node_type, posx, posy):
	group_data = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    node = config_node(node_tree, name, 'ShaderNodeGroup', posx, posy)
    node.node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    return node

def add_group_output(node_tree, group_node_output, input_type, input_name):
	if input_type is not 'NodeSocketVirtual':
    	#text.write("\t\tnode = node_tree.nodes[group_node_output]
        node_tree.outputs.new(input_type, input_name)

def add_group_input(node_tree, group_node_input, output_type, output_name):
	if output_type is not 'NodeSocketVirtual':
    	node = node_tree.nodes[group_node_output]
    	node_tree.inputs.new(output_type, output_name)
