#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {"name": "AddObject Helper",
           "author": "CDMJ",
           "version": (1, 00, 0),
           "blender": (3, 10, 0),
           "location": "Toolbar > Item",
           "description": "Add primitives with measurements and assign names",
           "warning": "",
           "category": "Object"}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


class MyAddProps(bpy.types.PropertyGroup):
    
    my_string : bpy.props.StringProperty(name= "Name", description = "Name for Generated Object and Collection")
    
    my_float_vector : bpy.props.FloatVectorProperty(name= "Scale", soft_min= 0, soft_max= 1000, default= (1,1,1), precision = 16)
    
    my_enum : bpy.props.EnumProperty(
        name= "Add",
        description= "Primitives to Add",
        items= [('OP1', "Cube", ""),
                ('OP2', "Plane", ""),
                ('OP3', "Cylinder", ""),
                ('OP4', "UV Sphere", ""),
                ('OP5', "Torus", ""),
                ('OP6', "Monkey", ""),
                ('OP7', "Cone", ""),
                ('OP8', "Circle", "")
        ]
    )
    my_enum_unit : bpy.props.EnumProperty(
        name= "Units",
        description= "Measurements for Use in Scene and Object",
        items= [('UN1', "Millimeters mm", ""),
                ('UN2', "Inches IN", "")
                
        ]
    )

class ADDOBJECT_PT_main_panel(bpy.types.Panel):
    bl_label = "AddObject Panel"
    bl_idname = "addObject_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        layout.prop(mytool, "my_enum_unit")
        layout.prop(mytool, "my_float_vector")
        layout.prop(mytool, "my_string")
        layout.prop(mytool, "my_enum")

        layout.operator("addobject.myop_operator")
        layout.operator("addobject.my_collection")



class ADDOBJECT_OT_my_op(bpy.types.Operator):
    bl_label = "Add Object"
    bl_idname = "addobject.myop_operator"

    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        if mytool.my_enum == 'OP1':
            bpy.ops.mesh.primitive_cube_add()
        if mytool.my_enum == 'OP2':    
            bpy.ops.mesh.primitive_plane_add()
        if mytool.my_enum == 'OP3':    
            bpy.ops.mesh.primitive_cylinder_add()            
        if mytool.my_enum == 'OP4':    
            bpy.ops.mesh.primitive_uv_sphere_add()
        if mytool.my_enum == 'OP5':    
            bpy.ops.mesh.primitive_torus_add()            
        if mytool.my_enum == 'OP6':    
            bpy.ops.mesh.primitive_monkey_add()
        if mytool.my_enum == 'OP7':    
            bpy.ops.mesh.primitive_cone_add()            
        if mytool.my_enum == 'OP8':    
            bpy.ops.mesh.primitive_circle_add()           
            
        
        if mytool.my_enum_unit == 'UN1':
        
            bpy.context.object.name = mytool.my_string + " " +str(mytool.my_float_vector[0]) +"mm x" +str(mytool.my_float_vector[1]) +"mm x" +str(mytool.my_float_vector[2]) +"mm"
        
        elif mytool.my_enum_unit == 'UN2':
            
            bpy.context.object.name = mytool.my_string + " " +str(mytool.my_float_vector[0]) +"IN x" +str(mytool.my_float_vector[1]) +"IN x" +str(mytool.my_float_vector[2]) +"IN"
            

        ########### if statements for mm or IN
        if mytool.my_enum_unit == 'UN1':
            #then do this stuff
            bpy.context.scene.unit_settings.system = 'METRIC'
            bpy.context.scene.unit_settings.length_unit = 'MILLIMETERS'
        
            ###new code
            x = mytool.my_float_vector[0] * 0.001
            y = mytool.my_float_vector[1] * 0.001
            z = mytool.my_float_vector[2] * 0.001
        
            bpy.context.object.dimensions = [x,y,z]
            
        elif mytool.my_enum_unit == 'UN2':
            #then do this instead
            bpy.context.scene.unit_settings.system = 'IMPERIAL'
            bpy.context.scene.unit_settings.length_unit = 'INCHES'
            # 276 / 7.00 = 39.42857142857143
            # 187 / 4.75 = 39.36842105263158
            # 197 / 5.00 = 39.4
            # 
            ###new code
            x = mytool.my_float_vector[0] / 39.38
            y = mytool.my_float_vector[1] / 39.38
            z = mytool.my_float_vector[2] / 39.38
        
            bpy.context.object.dimensions = [x,y,z]
                         

        
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        return {'FINISHED'}

class ADDOBJECT_OT_my_collection(bpy.types.Operator):
    bl_label = "Add to Collection"
    bl_idname = "addobject.my_collection"
    bl_options = { 'REGISTER', 'UNDO' }
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None      
    
    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        bpy.context.selected_objects
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name= mytool.my_string)
        return {'FINISHED'}    



classes = [MyAddProps, ADDOBJECT_PT_main_panel, ADDOBJECT_OT_my_op,ADDOBJECT_OT_my_collection]
 
 
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
        bpy.types.Scene.my_tool = bpy.props.PointerProperty(type= MyAddProps)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        del bpy.types.Scene.my_tool
 
 
 
if __name__ == "__main__":
    register()
