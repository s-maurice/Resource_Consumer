class IngotResource(object):
    image_name = "none"
    resource_name = "none"

    def __init__(self):
        self.image_location = "mineindustry_sprites/foreground/{}.png".format(self.image_name)


class ContainerResource(object):  # contains multiple ingot resources
    image_name = "none"
    resource_name = "none"

    inventory_size = 0

    def __init__(self):
        self.image_location = "mineindustry_sprites/foreground/{}.png".format(self.image_name)
