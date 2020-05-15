

class Anchor:
    def __init__(self):
        pass

    @staticmethod
    def _get_anchor_string_from_element(element):
        return element.get('name', element.get('id'))

    @staticmethod
    def _is_valid_anchor(anchor):
        return anchor is not None and not anchor.startswith('__') and anchor != ''

    @staticmethod
    def get_anchor(element):
        """
        Return a possible anchor for that element.
        Looks for name and id, and if not found will look in children
        """
        if isinstance(element, str):
            return None

        # Check the name or id on the element
        anchor = Anchor._get_anchor_string_from_element(element)
        if Anchor._is_valid_anchor(anchor):
            return anchor

        # Check on child
        children = element.cssselect('[name],[id]')
        if len(children) > 0:
            anchor = Anchor._get_anchor_string_from_element(children[-1])
            if Anchor._is_valid_anchor(anchor):
                return anchor

        el = element

        while el is not None:
            # go back
            while el.getprevious() is not None:
                el = el.getprevious()

                if el is not None:
                    anchor = Anchor._get_anchor_string_from_element(el)

                    if Anchor._is_valid_anchor(anchor):
                        return anchor

            # check last previous
            if el is not None:
                anchor = Anchor._get_anchor_string_from_element(el)

                if Anchor._is_valid_anchor(anchor):
                    return anchor

            # go up
            el = el.getparent()

            if el is not None:
                anchor = Anchor._get_anchor_string_from_element(el)

                # check parent
                if Anchor._is_valid_anchor(anchor):
                    return anchor

        # No more parent, we have no anchor
        return None
