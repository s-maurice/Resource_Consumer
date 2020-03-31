from RCResourceTypes import IngotResource


class EmptyIngotResource(IngotResource):
    id = 0
    image_name = "none"
    resource_name = "none"


class Titanium(IngotResource):
    id = 1
    image_name = "titanium"
    resource_name = "Titanium"


class Copper(IngotResource):
    id = 2
    image_name = "copper"
    resource_name = "copper"


class Sand(IngotResource):
    id = 3
    image_name = "sand"
    resource_name = "Sand"


class Glass(IngotResource):
    id = 4
    image_name = "glass"
    resource_name = "Glass"


class Thorium(IngotResource):
    id = 5
    image_name = "thorium"
    resource_name = "Thorium"


resource_id_lookup = {EmptyIngotResource.id: EmptyIngotResource,
                      Titanium.id: Titanium,
                      Copper.id: Copper,
                      Sand.id: Sand,
                      Glass.id: Glass,
                      Thorium.id: Thorium,
                      }


def inventory_from_json(inventory_dict):
    # rebuilds an inventory from json
    inventory = {}
    for key, item in inventory_dict.items():
        res = resource_id_lookup.get(int(key))
        inventory[res] = item
    return inventory
