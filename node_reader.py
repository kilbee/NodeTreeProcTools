bl_info = {
    "name": "kb Nodetree Proc Tools",
    "description": "Processing and Recreating Node Tree",
    "author": "kilbeeu",
    "version": (0, 1),
    "blender": (2, 76, 0),
    "location": "Node Editor Toolbar",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Node Editor"}

import bpy
from mathutils import Vector
import time

class CopyNodeTreeToTextPy(bpy.types.Operator):
    'Copy Node Tree'
    bl_idname = 'kb.kb_copy_node_tree'
    bl_label = 'Copy Node Tree'
    operation = bpy.props.StringProperty()

    def invoke(self, context, event):
        obj = bpy.context.scene.objects.active
       
        if self.operation == 'BACKUP':
            # backup active material node tree
            self.backup_node_tree(obj)
        return {'FINISHED'}

    def backup_node_tree(self, obj):
        node_tree = bpy.data.objects[obj.name].material_slots[0].material.node_tree
        nodes = node_tree.nodes
        ntree_path = 'bpy.data.objects[obj.name].material_slots[0].material.node_tree'  # hardcoded for testing purposes - todo: rework later for any node tree
        text_name = obj.name + " material[0] node tree backup"
        
        # creating script file - when run, it will recreate node tree
        bpy.data.texts.new(text_name)
        text = bpy.data.texts[text_name]
        text.clear()
        text.write("import bpy\n")
        text.write('obj = bpy.context.scene.objects.active\n')
        text.write('node_tree = '+ntree_path+'\n')
        text.write('nodes = node_tree.nodes\n\n')
        text.write("def create_node(node_tree, node_num, name, node_type, posx, posy, operation = None, blend_type = None, prop = None, prop_default = None):\n")
        text.write("\tnode = node_tree.nodes.new(type=node_type)  # create puff node\n")
        text.write("\tnode.location = (posx, posy)\n")
        text.write("\tnode.name = name\n")
        text.write("\tnode.label = name\n")
        text.write("\tif operation is not None:\n")
        text.write("\t\tnode.operation = operation\n")
        text.write("\tif blend_type is not None:\n")
        text.write("\t\tnode.blend_type = blend_type\n")
        text.write("\treturn node\n\n")

        text.write("def config_node(node_tree, node_num, is_muted, is_hidden, dim_x, dim_y):\n")
        text.write("\tnode = node_tree.nodes[node_num]\n")
        text.write("\tnode.mute = is_muted\n")
        text.write("\tnode.hide = is_hidden\n")
        text.write("\ttry:\n")
        text.write("\t\tnode.width = dim_x\n")
        text.write("\t\tnode.height = dim_y\n")
        text.write("\texcept:\n")
        text.write("\t\tpass\n\n")

        text.write("def create_node_group(node_tree, node_num, name, node_type, posx, posy):\n")
        text.write("\tgroup_data = bpy.data.node_groups.new(name, 'ShaderNodeTree')\n")
        text.write("\tnode = create_node(node_tree, node_num, name, 'ShaderNodeGroup', posx, posy)\n")        
        text.write("\tnode.node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')\n")
        text.write("\treturn node\n\n")

        text.write("def add_group_output(node_tree, group_node_output, input_type, input_name):\n")
        text.write("\tif input_type is not 'NodeSocketVirtual':\n")
        text.write("\t\tnode_tree.outputs.new(input_type, input_name)\n\n")

        text.write("def add_group_input(node_tree, group_node_input, output_type, output_name):\n")
        text.write("\tif output_type is not 'NodeSocketVirtual':\n")
        text.write("\t\tnode_tree.inputs.new(output_type, output_name)\n\n")

        text.write("def xonfig_node_inputs(node_tree, node_name, input_socket, input_value):\n")
        text.write("\tnode = node_tree.nodes[node_name]\n")
        text.write("\tnode.inputs[input_socket].default_value = input_value\n\n")


        self.process_node_tree(node_tree, text, ntree_path) # start processing node tree
        

    def process_node_tree(self, node_tree, text_object, nt_path):        
        nodes = node_tree.nodes
        
        for node_num, node in enumerate(nodes):
            text_object.write('\n# Node ['+ node.name +'] of ['+ node_tree.name+']\n')
            text_object.write('node_tree = '+nt_path+'\n')
            node_num = str(node_num)
            is_muted = str(node.mute)
            is_hidden = str(node.hide)
            dim_x = str(node.width)
            dim_y = str(node.height)
            if node.type == 'GROUP':
                #self.report({'INFO'}, "Group: "+ node.name)
                group_ntree_path = nt_path +".nodes['"+node.name+"'].node_tree"
                #create_node_group(node_tree, name, node_type, posx, posy):
                text_object.write("create_node_group(node_tree, "+node_num+", '"+node.name+"', '"+str(node.bl_idname)+"', "+str(node.location.x)+", "+str(node.location.y)+")\n")
                text_object.write("config_node(node_tree, "+node_num+", "+is_muted+", "+is_hidden+", "+dim_x+", "+dim_y+")\n")
                self.process_node_tree(node.node_tree, text_object, group_ntree_path)   # call self to iterate through node group node_tree
            else:
                if node.type == 'MATH':
                    operation = node.operation
                    text_object.write("create_node(node_tree, "+node_num+", '"+node.name+"', '"+str(node.bl_idname)+"', "+str(node.location.x)+", "+str(node.location.y)+", '"+str(node.operation)+"')\n")
                    text_object.write("config_node(node_tree, "+node_num+", "+is_muted+", "+is_hidden+", "+dim_x+", "+dim_y+")\n")
                elif node.type == 'MIX_RGB':
                    text_object.write("create_node(node_tree, "+node_num+", '"+node.name+"', '"+str(node.bl_idname)+"', "+str(node.location.x)+", "+str(node.location.y)+", None,'"+str(node.blend_type)+"')\n")
                    text_object.write("config_node(node_tree, "+node_num+", "+is_muted+", "+is_hidden+", "+dim_x+", "+dim_y+")\n")
                else:
                    text_object.write("create_node(node_tree, "+node_num+", '"+node.name+"', '"+str(node.bl_idname)+"', "+str(node.location.x)+", "+str(node.location.y)+")\n")
                    text_object.write("config_node(node_tree, "+node_num+", "+is_muted+", "+is_hidden+", "+dim_x+", "+dim_y+")\n")

            if node.type == 'GROUP_INPUT':
                for node_output in node.outputs:
                    #print("inputs["+node_input.path_from_id()[-2:-1]+"]")
                    #inputs[0].bl_idname
                    #add_group_output(node_out, node_out.inputs[0].bl_idname, node_out.inputs[0].name)
                    node_num = node_output.path_from_id()[-2:-1]
                    node_type = node_output.bl_idname
                    node_name = node_output.name
                    text_object.write("add_group_input(node_tree, '"+node.name+"', '"+node_type+"', '"+node_name+"')\n")
            if node.type == 'GROUP_OUTPUT':
                #self.report({'INFO'}, "Group Output Node - "+ node.name)
                #text_object.write("create_node(node_tree, '"+node.name+"', '"+str(node.bl_idname)+"', "+str(node.location.x)+", "+str(node.location.y)+")\n")
                for node_input in node.inputs:
                    #print("inputs["+node_input.path_from_id()[-2:-1]+"]")
                    #inputs[0].bl_idname
                    #add_group_output(node_out, node_out.inputs[0].bl_idname, node_out.inputs[0].name)
                    node_num = node_input.path_from_id()[-2:-1]
                    node_type = node_input.bl_idname
                    node_name = node_input.name
                    text_object.write("add_group_output(node_tree, '"+node.name+"', '"+node_type+"', '"+node_name+"')\n")

            for input_num, node_input in enumerate(node.inputs):
                
                if node.type != 'REROUTE' and node.type != 'OUTPUT_MATERIAL':
                    # need this check - shader inputs dont have default_value properties:
                    if hasattr(node_input, 'default_value'):
                        if node_input.type == 'VALUE':
                            input_value = str(node_input.default_value)
                        #elif node_input.type == 'RGBA' or  node_input.type == 'VECTOR':
                        else:
                            input_value = str(self.create_array(node_input.default_value))
                        text_object.write('node_tree = '+nt_path+'\n')
                        text_object.write("xonfig_node_inputs(node_tree, '"+node.name+"', "+str(input_num)+", "+input_value+")\n")

    
                
        text_object.write('\n# Links:\n')
        text_object.write('node_tree = '+nt_path+'\n')
        for link in node_tree.links:
            # self.report({'INFO'}, link.from_node.name)
            # self.report({'INFO'}, link.from_socket.name)
            # self.report({'INFO'}, link.to_node.name)
            # self.report({'INFO'}, link.to_socket.name)
            node_from = nt_path +".nodes['"+ str(node_tree.nodes[link.from_node.name].name)+"']"
            nd_link_from = node_from + ".outputs["+str(link.from_socket.path_from_id()[-2:-1])+"]"
            node_to = nt_path +".nodes['"+ str(node_tree.nodes[link.to_node.name].name)+"']"
            nd_link_to = node_to + ".inputs["+str(link.to_socket.path_from_id()[-2:-1])+"]"

            text_object.write("node_tree.links.new("+nd_link_from+", "+nd_link_to+")")
            text_object.write('\n')

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
    
