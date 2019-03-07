from screenplay.abilities.browse_the_web import BrowseTheWeb
from screenplay.decorators import step, MINOR


class Open(object):
    @step("{0} opens their browser and loads {url}", desc_attrs=["url"], severity=MINOR)
    def perform_as(self, the_actor):
        the_actor.uses_ability_to(BrowseTheWeb).to_get(self.url)

    @staticmethod
    def browser_on(location):
        return Open(location)

    def __init__(self, location):
        if isinstance(location, str):
            self.url = location
        else:
            self.url = location.url
