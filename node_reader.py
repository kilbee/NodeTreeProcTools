bl_info = {
    "name": "kb Nodetree Proc Tools",
    "description": "Processing and Recreating Node Tree",
    "author": "kilbeeu",
    "version": (0, 2),
    "blender": (2, 76, 0),
    "location": "Node Editor Toolbar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Node Editor"}

import bpy
from mathutils import Vector
import time
import os, sys

class CopyNodeTreeToTextPy(bpy.types.Operator):
    'Copy Node Tree'
    bl_idname = 'kb.kb_copy_node_tree'
    bl_label = 'Copy Node Tree'
    operation = bpy.props.StringProperty()


    def invoke(self, context, event):
        obj = bpy.context.scene.objects.active
       
        if self.operation == 'BACKUP':
            node_groups = self.read_node_tree(obj)  # backup active material node tree
            self.write_node_tree(obj, node_groups)  # generate script for recreating node tree
        return {'FINISHED'}


    def read_node_tree(self, obj):
        node_tree = bpy.data.objects[obj.name].material_slots[0].material.node_tree
        nt_path = 'bpy.data.objects[obj.name].material_slots[0].material.node_tree'  # hardcoded for testing purposes - todo: rework later for any node tree
        group_list = []
        mat_group = ["Material NodeTree", nt_path, node_tree] # highest level group - material node tree
        group_list.append(mat_group)    # append to node group list
        node_groups = self.read_node_groups(node_tree, nt_path, group_list) # append all node groups in node tree
        return node_groups
               

    def read_node_groups(self, node_tree, nt_path, group_list):        
        for node in node_tree.nodes:
            if node.type == 'GROUP':
                node_path_from_id = str(node.path_from_id())
                group_ntree_id_data = node.node_tree.id_data.name
                group_nt = node.node_tree
                group_nt_path = nt_path + "." + node_path_from_id + ".node_tree" # construct node group data path

                duplicate_group = False
                for group in group_list:
                    for item in group:
                        if group_nt.name == item:
                            duplicate_group = True # check if current node group is not yet listed
                            
                if duplicate_group == False:
                    current_group = [group_nt.name, group_nt_path, group_nt]
                    group_list.append(current_group)    # if node group is not yet listed, then append to node group list
                    group_list_deeper = self.read_node_groups(group_nt, group_nt_path, group_list) # if there is a node group in current node group, then call self to append to node group list
        return group_list


    def write_node_tree(self, obj, node_groups):
        text_name = obj.name + " mat[0] Node Tree"
        bpy.data.texts.new(text_name)
        text = bpy.data.texts[text_name]
        text.clear()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        template = open(os.path.join(script_dir, "node_writer.py"),"r")
        template_string = template.read()
        template.close()
        text.write(template_string)
        text.write('obj = bpy.context.scene.objects.active\n\n')
        
        # Generating nodes and node groups with inputs and outputs
        for node_group in node_groups:
            # node_group[0] = data block
            # node_group[1] = str( node_tree path)
            # node_group[2] = node_tree path
            
            node_tree_str = node_group[1]
            text.write('\n# Node Tree of ['+ str(node_group[0]) +']\n')
            text.write("node_tree = " + node_tree_str + "\n")            
            
            node_tree = node_group[2]
            for node_num, node in enumerate(node_tree.nodes):
                node_num = str(node_num)
                loc_x = str(node.location.x)
                loc_y = str(node.location.y)
                dim_x = str(node.width)
                dim_y = str(node.height)
                is_muted = str(node.mute)
                is_hidden = str(node.hide)

                node_color = 'None'
                if node.use_custom_color is True:
                    node_color = str(self.create_array(node.color))

                operation = 'None'
                if node.type == 'MATH':
                    operation = "'"+str(node.operation)+"'"
                
                blend_type = 'None'
                if node.type == 'MIX_RGB':
                    blend_type = "'"+str(node.blend_type)+"'"
                
                # create node (node_tree, node_number, node_name, node_type, operation_type=None, blend_type=None)
                text.write("node = create_node(node_tree, "+node_num+", '"+node.name+"', '"+str(node.bl_idname)+"', "+operation+", "+blend_type+")\n")
                # config node (node_tree, node_number, location_x, location_y, dimension_x, dimension_y, is_muted, is_hidden, custom_color=None)
                text.write("config_node(node_tree, "+node_num+", "+loc_x+", "+loc_y+", "+dim_x+", "+dim_y+", "+is_muted+", "+is_hidden+", "+node_color+")\n")                

                # special check for group node
                if node.type == 'GROUP':
                    data_block = node.node_tree.name
                    text.write("group_data_name = create_node_group('"+data_block+"')\n")
                    text.write("node.node_tree = group_data_name\n")

                # special check for group input node
                if node.type == 'GROUP_INPUT':                
                    for node_output in node.outputs:
                        node_type = node_output.bl_idname
                        node_name = node_output.name
                        text.write("add_group_input(node_tree, '"+node_type+"', '"+node_name+"')\n")
                    
                    # configure group inputs
                    inputs = node_tree.id_data.inputs
                    for num, group_input in enumerate(inputs):
                        # check if input has default value
                        if hasattr(group_input, 'default_value'):
                            if group_input.type == 'VALUE':
                                default_value = str(group_input.default_value)
                            else:
                                default_value = str(self.create_array(group_input.default_value))
                        else:
                            default_value = 'None'

                        # check if input has min value
                        if hasattr(group_input, 'min_value'):
                            if group_input.type == 'VALUE' or group_input.type == 'VECTOR':
                                min_value = str(group_input.min_value)
                            else:
                                min_value = str(self.create_array(group_input.min_value))
                        else:
                            min_value = 'None'

                        # check if input has max value
                        if hasattr(group_input, 'max_value'):
                            if group_input.type == 'VALUE' or group_input.type == 'VECTOR':
                                max_value = str(group_input.max_value)
                            else:
                                max_value = str(self.create_array(group_input.max_value))
                        else:
                            max_value = 'None'
                        # note: 'VECTOR' type input default value is an array, but min and max values are floats - bug?
                        text.write("config_group_node_input(node_tree, "+str(num)+", "+default_value+", "+min_value+", "+max_value+")\n")

                # configure group outputs
                if node.type == 'GROUP_OUTPUT':
                    for node_input in node.inputs:
                        node_type = node_input.bl_idname
                        node_name = node_input.name
                        text.write("add_group_output(node_tree, '"+node_type+"', '"+node_name+"')\n")

        # configure node inputs
        text.write('\n# Node inputs defaults\n')
        for node_group in node_groups:            
            node_tree_str = node_group[1]
            text.write('\n# Inputs for nodes of Node Tree ['+ str(node_group[0]) +']\n')
            text.write("node_tree = " + node_tree_str + "\n")            
            node_tree = node_group[2]
            for node_num, node in enumerate(node_tree.nodes):
                for input_num, node_input in enumerate(node.inputs):                
                    if node.type != 'REROUTE' and node.type != 'OUTPUT_MATERIAL':
                        if hasattr(node_input, 'default_value'):    # need this check - shader inputs dont have default_value properties:
                            if node_input.type == 'VALUE':
                                input_value = str(node_input.default_value)
                            else:   # replaced: elif node_input.type == 'RGBA' or  node_input.type == 'VECTOR':
                                input_value = str(self.create_array(node_input.default_value))
                            text.write("config_node_inputs(node_tree, '"+node.name+"', "+str(input_num)+", "+input_value+")\n")


        # Generating links for node groups
        text.write('\n# Links\n')
        for node_group in node_groups:            
            node_tree_str = node_group[1]
            text.write('\n# Links for Node Tree of ['+ str(node_group[0]) +']\n')
            text.write("node_tree = " + node_tree_str + "\n")            
            node_tree = node_group[2]
            for link in node_tree.links:
                #print(link.from_node.name)
                node_from = "node_tree.nodes['"+ link.from_node.name+"']"
                try:
                    ls, rs = str(link.from_socket.path_from_id()[-3:-1]).split('[') # parse number out of strin
                except:
                    rs = str(link.from_socket.path_from_id()[-3:-1])
                link_from = node_from + ".outputs["+rs+"]"

                node_to = "node_tree.nodes['"+ link.to_node.name+"']"
                try:
                    ls, rs = str(link.to_socket.path_from_id()[-3:-1]).split("[")  # parse number out of strin
                except:
                    rs = str(link.to_socket.path_from_id()[-3:-1])
                link_to = node_to + ".inputs["+rs+"]"
                #output_socket = link.path_resolve('from_socket')
                #input_socket = link.path_resolve('to_socket')
                text.write("node_tree.links.new("+link_from+", "+link_to+")")   # write link to file
                text.write('\n')


                
            

    def create_array(self, input_array):
        output_array = []
        for f in enumerate(input_array):
            output_array.append(f[1])
        return output_array


 

#   ooooooooo.         .o.       ooooo      ooo oooooooooooo ooooo         .oooooo..o 
#   `888   `Y88.      .888.      `888b.     `8' `888'     `8 `888'        d8P'    `Y8 
#    888   .d88'     .8"888.      8 `88b.    8   888          888         Y88bo.      
#    888ooo88P'     .8' `888.     8   `88b.  8   888oooo8     888          `"Y8888o.  
#    888           .88ooo8888.    8     `88b.8   888    "     888              `"Y88b 
#    888          .8'     `888.   8       `888   888       o  888       o oo     .d8P 
#   o888o        o88o     o8888o o8o        `8  o888ooooood8 o888ooooood8 8""88888P'  
#

class CopyNodeTreeToTextPyPanel(bpy.types.Panel):
    bl_idname = "NODE_PT_kb"
    bl_space_type = 'NODE_EDITOR'
    bl_label = "kb"
    bl_region_type = "TOOLS"
    bl_category = "kb"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        
        maincol = layout.column()
        box = maincol.box()
        sub = box.column(align=True)
        col = sub.column(align = True)
        col.enabled = True
        col.operator("kb.kb_copy_node_tree", text="Backup Puff! Cloud Domain Material", icon='NODE').operation = 'BACKUP'

    
    
#   ooooooooo.   oooooooooooo   .oooooo.    ooooo  .oooooo..o ooooooooooooo oooooooooooo ooooooooo.   
#   `888   `Y88. `888'     `8  d8P'  `Y8b   `888' d8P'    `Y8 8'   888   `8 `888'     `8 `888   `Y88. 
#    888   .d88'  888         888            888  Y88bo.           888       888          888   .d88' 
#    888ooo88P'   888oooo8    888            888   `"Y8888o.       888       888oooo8     888ooo88P'  
#    888`88b.     888    "    888     ooooo  888       `"Y88b      888       888    "     888`88b.    
#    888  `88b.   888       o `88.    .88'   888  oo     .d8P      888       888       o  888  `88b.  
#   o888o  o888o o888ooooood8  `Y8bood8P'   o888o 8""88888P'      o888o     o888ooooood8 o888o  o888o 

def register():
    # settings classes
    bpy.utils.register_class(CopyNodeTreeToTextPy)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(CopyNodeTreeToTextPy)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

    # debugging:
    bpy.app.debug = False
    debug_txt = "\n\n\n--------------------------------------------------------------------------------------\n----------------------------------------------------------------- run@  "+str(time.localtime().tm_hour) +":"+ str(time.localtime().tm_min) +":"+ str(time.localtime().tm_sec) +" -----\n"
    print(debug_txt)
    
