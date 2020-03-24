class IngotResource(object):
    id = 0
    image_name = "none"
    resource_name = "none"

    def __init__(self):
        self.image_location = "mineindustry_sprites/machines/{}.png".format(self.image_name)


class ContainerResource(object):  # contains multiple ingot resources
    id = 0
    image_name = "none"
    resource_name = "none"

    inventory_size = 0

    def __init__(self):
        self.image_location = "mineindustry_sprites/machines/{}.png".format(self.image_name)
