"""
Module implements vcard-temp feature
"""
# XEP-0054
import copy

from twilix.stanzas import Query, Iq
from twilix import fields
from twilix.disco import Feature
from twilix.base import WrongElement, VElement

class Name(VElement):
    """
    Extends VElement class from twilix.base.
    Used for representation name data (family name, given name and 
    middle name)
    """    
    elementName = 'N'
    
    family_name = fields.StringNode('FAMILY', required=False)
    given_name = fields.StringNode('GIVEN', required=False)
    middle_name = fields.StringNode('MIDDLE', required=False)

class Organization(VElement):
    """
    Extends VElement class from twilix.base.
    Used for representation organization data (organization name and
    organization unit)
    """
    elementName = 'ORG'

    name = fields.StringNode('ORGNAME', required=False)
    unit = fields.StringNode('ORGUNIT', required=False)

class Telephone(VElement):
    # TODO
    """
    Extends VElement class from twilix.base.
    Used for representation telephone data.
    """
    pass

class Address(VElement):
    # TODO
    """
    Extends VElement class from twilix.base.
    Used for representation adress data.
    """
    pass

class Email(VElement):
    # TODO
    """
    Extends VElement class from twilix.base.
    Used for representation e-mail data.
    """
    pass

class Photo(VElement):
    """
    Extends VElement class from twilix.base.
    Used for representation photo data (type and binary value)
    """
    elementName = 'PHOTO'

    type_ = fields.StringNode('TYPE', required=False)
    binval = fields.Base64Node('BINVAL', required=False)

class VCardQuery(Query):
    """
    Extends Query class from twilix.stanzas.
    Contains fields with nodes for personal data.
    """
    elementName = 'vCard'
    elementUri = 'vcard-temp'

    full_name = fields.StringNode('FN', required=False)
    name_ = fields.ElementNode('N', Name, required=False, listed=False)
    nickname = fields.StringNode('NICKNAME', required=False)
    url = fields.StringNode('URL', required=False)
    birthday = fields.StringNode('BDAY', required=False)
    organization = fields.ElementNode('ORG', Organization, required=False,
                                      listed=False)
    title = fields.StringNode('TITLE', required=False)
    role = fields.StringNode('ROLE', required=False)
    # telephones TODO
    # addresses TODO
    # emails TODO
    jid = fields.StringNode('JABBERID', required=False)
    description = fields.StringNode('DESC', required=False)
    photo = fields.ElementNode('PHOTO', Photo, required=False, listed=False)

class MyVCardQuery(VCardQuery):
    """
    Extends VCardQuery.
    """
    def getHandler(self):
        if self.host.myvcard and self.host.dispatcher.myjid == self.iq.to:
            iq = self.iq.makeResult()
            iq.link(self.host.myvcard)
            return iq
        elif not self.host.myvcard:
            return self.iq.makeError('cancel', 'item-not-found')

    def setHandler(self):
        return self.iq.makeError('auth', 'forbidden')

class VCard(object):
    def __init__(self, dispatcher, myvcard=None):
        self.dispatcher = dispatcher
        self.myvcard = myvcard
        self._handlers = []

    def init(self, disco=None, handlers=None):
        if handlers is None:
            handlers = ()

        self.dispatcher.registerHandler((MyVCardQuery, self))

        for handler, host in handlers:
            self.dispatcher.registerHandler((handler, host))

        if disco is not None:
            disco.root_info.addFeatures(Feature(var='vcard-temp'))

    def get(self, jid, from_=None):
        if from_ is None:
            from_ = self.dispatcher.myjid
        query = VCardQuery(parent=Iq(type_='get', to=jid, from_=from_))
        query.iq.result_class = VCardQuery
        self.dispatcher.send(query.iq)
        return query.iq.deferred

    def set(self, vcard):
        query = copy.copy(vcard)
        iq = Iq(type_='set')
        iq.link(query)
        self.dispatcher.send(query.iq)
        return query.iq.deferred

