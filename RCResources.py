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


def inventory_from_json(inventory_dict):
    # rebuilds an inventory from json
    inventory = {}
    print(inventory_dict)
    for key, item in inventory_dict.items():
        print(key, item)
        res = resource_id_lookup.get(int(key))
        print(res)
        inventory[res] = item
    return inventory
