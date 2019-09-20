from itertools import islice


class MiscUtilities:
    @staticmethod
    def chunk(it, size):
        if it is None:
            return []
        it = iter(it)

        return iter(lambda: tuple(islice(it, size)), ())
