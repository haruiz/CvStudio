class GalleryAction():
    def __init__(self, icon, name, tooltip=None):
        self._icon = icon
        self._name = name
        self._tooltip = tooltip

    @property
    def tooltip(self):
        return self._tooltip

    @tooltip.setter
    def tooltip(self, value):
        self._tooltip = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
