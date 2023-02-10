# Object with relations to other objects.
# id:        The object.
# name:      The name of the object (derived from id)
# objects:   Other objects.
# stuff      Other objects(stuff)(wall celling etc..)
class StuffObjectNode:
    def __init__(self, id, name, objects, stuff):
        # Remove self fromgiven list (You are in one of them))
        self.id = id
        self.name = name
        self.otherStuffObjects = {}
        # Adding stuff and objects to map{<object[i]>: 0}
        for i in objects:
            if id == i:
                continue
            self.otherStuffObjects[i] = 0

        for i in stuff:
            if id == i:
                continue
            self.otherStuffObjects[i] = 0