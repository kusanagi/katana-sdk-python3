"""
Python 3 SDK for the KATANA(tm) Framework (http://katana.kusanagi.io)

Copyright (c) 2016-2018 KUSANAGI S.L. All rights reserved.

Distributed under the MIT license.

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

"""
__license__ = "MIT"
__copyright__ = "Copyright (c) 2016-2018 KUSANAGI S.L. (http://kusanagi.io)"


class Relation(object):
    """Represents a relation object in the Transport."""

    def __init__(self, address, name, primary_key, foreign_services):
        self.__address = address
        self.__name = name
        self.__primary_key = primary_key
        self.__foreign_services = foreign_services

    def get_address(self):
        """
        Get the Gateway address of the Service.

        :rtype: str

        """

        return self.__address

    def get_name(self):
        """
        Get the name of the Service.

        :rtype: str

        """

        return self.__name

    def get_primary_key(self):
        """
        Get the value of the primary key for the relation.

        :rtype: str

        """

        return self.__primary_key

    def get_foreign_relations(self):
        """
        Get the foreign key values for the relation.

        :returns: A list of `ForeignRelation`.
        :rtype: list

        """

        relations = []
        for address, services in self.__foreign_services.items():
            for name, foreign_keys in services.items():
                relations.append(ForeignRelation(address, name, foreign_keys))

        return relations


class ForeignRelation(object):
    """Represents a foreign relation object in the Transport."""

    def __init__(self, address, name, foreign_keys):
        self.__address = address
        self.__name = name
        self.__foreign_keys = foreign_keys

    def get_address(self):
        """
        Get the Gateway address of the "foreign" Service.

        :rtype: str

        """

        return self.__address

    def get_name(self):
        """
        Get the name of the "foreign" Service.

        :rtype: str

        """

        return self.__name

    def get_type(self):
        """
        Get the type of the relation.

        The relation type can be either "one" or "many".

        :rtype: str

        """

        return "many" if isinstance(self.__foreign_keys[0], list) else "one"

    def get_foreign_keys(self):
        """
        Get the foreign key values for the relation.

        :returns: A list of str.
        :rtype: list

        """

        return self.__foreign_keys
