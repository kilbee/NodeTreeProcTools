# NodeTreeProcTools
(wip) Tools for backing up Blender Node Trees (and generating script for re-creating them).
----
this tool was developped for recreating some node trees. code is not pretty (just needed it asap) but works for:

* reading/writing whole node structure with links (with recursive group node structure)
* reading/writing default values for node sockets (group input outputs, node inputs)
* reading/writing 'MATH' and 'MIX_RGB' nodes operation types

script outputs a file in blender's text editor. if executed it will recreate node tree for active (context) object (in material[0] slot). hardcoded for now, will improve that later.

there is still some functionality missing (various node types contain additional data), maybe will be added if needed.


to install, just download zip file (must containt node_reader.py and node_writer.py) and install as a blender addon.
in node editor, there will be tab 'kb'
