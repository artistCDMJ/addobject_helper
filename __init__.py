bl_info = {
    "name": "AddObject Helper2",
    "author": "CDMJ, Nezumi.blend",
    "version": (1, 00, 2),
    "blender": (3, 10, 0),
    "location": "Toolbar > Item",
    "description": "Add primitives with measurements and assign names",
    "warning": "",
    "category": "Object",
    "support": "TESTING"
}


import bpy
from string import Template
from mathutils import Vector


class ADDOBJECT_PG_add_object_helper(bpy.types.PropertyGroup):
    my_obj_name: bpy.props.StringProperty(
        name="Name",
        description="Name for Generated Object and Collection",
    )
    my_obj_name_flag: bpy.props.BoolProperty(
        name="Include units",
        description="Add units to name",
        default=False,
    )
    my_obj_dimensions: bpy.props.FloatVectorProperty(
        name="Dimensions",
        description="Dimensions at unit scale",
        soft_min=0,
        soft_max=1000,
        default=(1, 1, 1),
        precision=16,
    )
    my_enum_objs: bpy.props.EnumProperty(
        name="Add",
        description="Primitives to Add",
        items=[
            ("MESH_PLANE", "Plane", "primitive_plane_add"),
            ("MESH_CUBE", "Cube", "primitive_cube_add"),
            ("MESH_CIRCLE", "Circle", "primitive_circle_add"),
            ("MESH_UVSPHERE", "UV Sphere", "primitive_uv_sphere_add"),
            ("MESH_CYLINDER", "Cylinder", "primitive_cylinder_add"),
            ("MESH_CONE", "Cone", "primitive_cone_add"),
            ("MESH_TORUS", "Torus", "primitive_torus_add"),
            ("MESH_MONKEY", "Monkey", "primitive_monkey_add"),
        ],
    )
    my_enum_unit: bpy.props.EnumProperty(
        name="Units",
        description="Measurements for Use in Scene and Object",
        items=[
            ('UN1', "Millimeters mm", ""),
            ('UN2', "Inches IN", ""),
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
        col = layout.column()
        col.prop(mytool, "my_enum_unit")
        row = layout.row()
        row.prop(mytool, "my_obj_dimensions")
        row = layout.row()
        row.prop(mytool, "my_obj_name")
        row.prop(mytool, "my_obj_name_flag")
        col = layout.column()
        if not mytool.my_obj_name_flag:
            obj_name = mytool.my_obj_name
        else:
            s = Template("${obj_name} ${x_dim} ${unit} x ${y_dim} ${unit} x ${z_dim} ${unit}")
            if mytool.my_enum_unit == "UN1":
                obj_name=s.substitute(
                    obj_name=mytool.my_obj_name,
                    x_dim=mytool.my_obj_dimensions[0],
                    unit="mm",
                    y_dim=mytool.my_obj_dimensions[1],
                    z_dim=mytool.my_obj_dimensions[2])
            else:
                obj_name = s.substitute(
                    obj_name=mytool.my_obj_name,
                    x_dim=mytool.my_obj_dimensions[0],
                    unit="IN",
                    y_dim=mytool.my_obj_dimensions[1],
                    z_dim=mytool.my_obj_dimensions[2])
        col.label(text=f"ex: {obj_name}")
        items = mytool.bl_rna.properties['my_enum_objs'].enum_items
        enum = items[mytool.my_enum_objs]
        col.prop(
            mytool,
            "my_enum_objs",
            text="Object type",
            icon=enum.identifier)

        make_obj = col.operator(
            "addobject.myop_operator",
            text=enum.name,
            icon=enum.identifier)
        make_obj.item_type = enum.description

        make_obj.item_dimensions = mytool.my_obj_dimensions
        make_obj.item_name = obj_name

        make_coll = col.operator("addobject.my_collection")
        make_coll.coll_name = obj_name


def unit_conversion(context, item_dims):
    scene = context.scene
    mytool = scene.my_tool
    # divide by 2 since items are created based on radius dimensions
    # also variable for sphere is listed as radius but cube is listed as size
    item_dims = item_dims / 2

    # since the operation of bpy.ops.mesh.primitive_xx_add
    # is based on a 1 meter scale always
    # conversion is only based on the unit selection in the enumerator property

    # metric to mm conversions (1m = 1000mm)
    if mytool.my_enum_unit == 'UN1':
        item_dims = item_dims / 1000

    # imperial to IN conversions (1m = 39.36in)
    if mytool.my_enum_unit == 'UN2':
        item_dims = item_dims / 39.36
    return item_dims


class ADDOBJECT_OT_my_op(bpy.types.Operator):
    bl_label = "Add Object"
    bl_idname = "addobject.myop_operator"
    bl_options = {'REGISTER', 'UNDO'}

    item_type: bpy.props.StringProperty(
        name="Mesh Primitive",
        description="Type of mesh primitive to add",
        default="primitive_plane_add",
    )
    item_dimensions: bpy.props.FloatVectorProperty(
        name="Dimensions",
        description="Dimensions at unit scale",
        soft_min=0,
        soft_max=1000,
        default=(1, 1, 1),
        precision=16,
    )
    item_name: bpy.props.StringProperty(
        name="Name",
        description="Name for Generated Object",
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        scalable_objs = [
            "primitive_cube_add",
            "primitive_uv_sphere_add",
            "primitive_cylinder_add",
            "primitive_cone_add",
        ]
        x, y, z = unit_conversion(context, Vector(self.item_dimensions))
        if self.item_type in scalable_objs:
            cmd = f"bpy.ops.mesh.{self.item_type}(scale=({x}, {y}, {z}))"
            ob = eval(cmd)
        else:
            cmd = f"bpy.ops.mesh.{self.item_type}()"
            ob = eval(cmd)
            ob = context.view_layer.objects.active
            ob.dimensions = Vector((x, y, z)) * 2
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        context.view_layer.objects.active.name = self.item_name
        return {'FINISHED'}


class ADDOBJECT_OT_my_collection(bpy.types.Operator):
    bl_label = "Add to Collection"
    bl_idname = "addobject.my_collection"
    bl_options = {'REGISTER', 'UNDO'}

    coll_name: bpy.props.StringProperty(
        name="Name",
        description="Name for Generated Collection",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        context.selected_objects
        bpy.ops.object.move_to_collection(
            collection_index=0,
            is_new=True,
            new_collection_name=self.coll_name)
        return {'FINISHED'}


classes = [
    ADDOBJECT_PG_add_object_helper,
    ADDOBJECT_PT_main_panel,
    ADDOBJECT_OT_my_op,
    ADDOBJECT_OT_my_collection,
    ]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(
        type=ADDOBJECT_PG_add_object_helper)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
