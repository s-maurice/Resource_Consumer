from RCResourceTypes import IngotResource


class EmptyIngotResource(IngotResource):
    id = 0
    image_name = "none"
    resource_name = "none"


class Titanium(IngotResource):
    id = 1
    image_name = "titanium"
    resource_name = "Titanium"


class Lead(IngotResource):
    id = 2
    image_name = "lead"
    resource_name = "Lead"


class Sand(IngotResource):
    id = 3
    image_name = "sand"
    resource_name = "Sand"


class Glass(IngotResource):
    id = 4
    image_name = "glass"
    resource_name = "Glass"


resource_id_lookup = {EmptyIngotResource.id: EmptyIngotResource,
                      Titanium.id: Titanium,
                      Lead.id: Lead,
                      Sand.id: Sand,
                      Glass.id: Glass
                      }
