import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import numpy as np

def create_simple_bim():
    """Cria um arquivo IFC simples com paredes e vigas"""
    
    # Cria um novo arquivo IFC
    ifc_file = ifcopenshell.file()
    
    # Define o projeto
    project = ifc_file.createIfcProject(
        GlobalId=ifcopenshell.guid.new(),
        Name="Projeto Metro SP",
        Description="Projeto de exemplo para integração BIM + YOLO"
    )
    
    # Define o contexto do projeto
    context = ifc_file.createIfcGeometricRepresentationContext(
        ContextIdentifier="Model",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=0.001,
        WorldCoordinateSystem=ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0., 0., 0.))
        ),
        TrueNorth=ifc_file.createIfcDirection((0., 1., 0.))
    )
    
    # Define a representação do projeto
    project.RepresentationContexts = (context,)
    
    # Cria um site
    site = ifc_file.createIfcSite(
        GlobalId=ifcopenshell.guid.new(),
        Name="Site",
        ObjectPlacement=ifc_file.createIfcLocalPlacement(
            RelativePlacement=ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint((0., 0., 0.))
            )
        )
    )
    
    # Cria um building
    building = ifc_file.createIfcBuilding(
        GlobalId=ifcopenshell.guid.new(),
        Name="Edifício",
        ObjectPlacement=ifc_file.createIfcLocalPlacement(
            RelativePlacement=ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint((0., 0., 0.))
            )
        )
    )
    
    # Cria um storey
    storey = ifc_file.createIfcBuildingStorey(
        GlobalId=ifcopenshell.guid.new(),
        Name="Piso 1",
        ObjectPlacement=ifc_file.createIfcLocalPlacement(
            RelativePlacement=ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint((0., 0., 0.))
            )
        )
    )
    
    # Lista para armazenar elementos
    elements = []
    
    # Cria paredes
    wall_data = [
        {"start": (0, 0, 0), "end": (5, 0, 0), "height": 3, "thickness": 0.2},
        {"start": (5, 0, 0), "end": (5, 5, 0), "height": 3, "thickness": 0.2},
        {"start": (5, 5, 0), "end": (0, 5, 0), "height": 3, "thickness": 0.2},
        {"start": (0, 5, 0), "end": (0, 0, 0), "height": 3, "thickness": 0.2},
    ]
    
    for i, wall_info in enumerate(wall_data):
        wall = create_wall(ifc_file, wall_info, f"Parede_{i+1}")
        elements.append(wall)
    
    # Cria vigas
    beam_data = [
        {"start": (0, 0, 3), "end": (5, 0, 3), "width": 0.3, "height": 0.4},
        {"start": (0, 2.5, 3), "end": (5, 2.5, 3), "width": 0.3, "height": 0.4},
        {"start": (0, 5, 3), "end": (5, 5, 3), "width": 0.3, "height": 0.4},
    ]
    
    for i, beam_info in enumerate(beam_data):
        beam = create_beam(ifc_file, beam_info, f"Viga_{i+1}")
        elements.append(beam)
    
    # Organiza a hierarquia
    storey.ContainsElements = ifc_file.createIfcRelContainedInSpatialStructure(
        GlobalId=ifcopenshell.guid.new(),
        RelatingStructure=storey,
        RelatedElements=elements
    )
    
    building.BuildingStoreys = (storey,)
    site.Buildings = (building,)
    project.Sites = (site,)
    
    # Salva o arquivo
    ifc_file.write("metro_sp.ifc")
    print("Arquivo IFC criado com sucesso: metro_sp.ifc")
    print(f"Total de elementos: {len(elements)}")
    
    return ifc_file

def create_wall(ifc_file, wall_info, name):
    """Cria uma parede"""
    start = wall_info["start"]
    end = wall_info["end"]
    height = wall_info["height"]
    thickness = wall_info["thickness"]
    
    # Calcula as dimensões
    length = np.linalg.norm(np.array(end) - np.array(start))
    
    # Cria a geometria da parede
    wall_profile = ifc_file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        ProfileName="WallProfile",
        XDim=thickness,
        YDim=length
    )
    
    wall_solid = ifc_file.createIfcExtrudedAreaSolid(
        SweptArea=wall_profile,
        Position=ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0., 0., 0.))
        ),
        ExtrudedDirection=ifc_file.createIfcDirection((0., 0., 1.)),
        Depth=height
    )
    
    wall_shape = ifc_file.createIfcShapeRepresentation(
        ContextOfItems=ifc_file.by_type("IfcGeometricRepresentationContext")[0],
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[wall_solid]
    )
    
    wall_definition = ifc_file.createIfcProductDefinitionShape(
        Name=name,
        Representations=[wall_shape]
    )
    
    # Calcula a rotação para alinhar a parede
    direction = np.array(end) - np.array(start)
    angle = np.arctan2(direction[1], direction[0])
    
    wall = ifc_file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
        ObjectPlacement=ifc_file.createIfcLocalPlacement(
            RelativePlacement=ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint(start),
                ifc_file.createIfcDirection((0., 0., 1.)),
                ifc_file.createIfcDirection((np.cos(angle), np.sin(angle), 0.))
            )
        ),
        Representation=wall_definition
    )
    
    return wall

def create_beam(ifc_file, beam_info, name):
    """Cria uma viga"""
    start = beam_info["start"]
    end = beam_info["end"]
    width = beam_info["width"]
    height = beam_info["height"]
    
    # Calcula as dimensões
    length = np.linalg.norm(np.array(end) - np.array(start))
    
    # Cria a geometria da viga
    beam_profile = ifc_file.createIfcRectangleProfileDef(
        ProfileType="AREA",
        ProfileName="BeamProfile",
        XDim=width,
        YDim=height
    )
    
    beam_solid = ifc_file.createIfcExtrudedAreaSolid(
        SweptArea=beam_profile,
        Position=ifc_file.createIfcAxis2Placement3D(
            ifc_file.createIfcCartesianPoint((0., 0., 0.))
        ),
        ExtrudedDirection=ifc_file.createIfcDirection((1., 0., 0.)),
        Depth=length
    )
    
    beam_shape = ifc_file.createIfcShapeRepresentation(
        ContextOfItems=ifc_file.by_type("IfcGeometricRepresentationContext")[0],
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[beam_solid]
    )
    
    beam_definition = ifc_file.createIfcProductDefinitionShape(
        Name=name,
        Representations=[beam_shape]
    )
    
    # Calcula a rotação para alinhar a viga
    direction = np.array(end) - np.array(start)
    angle = np.arctan2(direction[1], direction[0])
    
    beam = ifc_file.createIfcBeam(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
        ObjectPlacement=ifc_file.createIfcLocalPlacement(
            RelativePlacement=ifc_file.createIfcAxis2Placement3D(
                ifc_file.createIfcCartesianPoint(start),
                ifc_file.createIfcDirection((0., 0., 1.)),
                ifc_file.createIfcDirection((np.cos(angle), np.sin(angle), 0.))
            )
        ),
        Representation=beam_definition
    )
    
    return beam

if __name__ == "__main__":
    create_simple_bim() 