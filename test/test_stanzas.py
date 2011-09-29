import unittest

from twisted.words.protocols.jabber.jid import JID

from twilix import stanzas, base
from twilix.test import dispatcherEmul, hostEmul


class TestStanza(unittest.TestCase):
    
    def setUp(self):
        self.from_=JID('from')
        self.to=JID('to')
        self.stanza = stanzas.Stanza(to=self.to, from_=self.from_)
    
    def testMakeError(self):
        res = self.stanza.makeError('error')
        self.assertEqual(res.type_, 'error')
        self.assertEqual(res.to, self.from_)
        self.assertEqual(res.from_, self.to)
        self.assertTrue(isinstance(res, stanzas.ErrorStanza))
    
    def test_unicode(self):
        res = unicode(self.stanza)
        self.assertEqual(res, u"<None to='to' from='from'/>")
        
    def test_repr(self):
        res = repr(self.stanza)
        self.assertEqual(res, u"<None to='to' from='from'/>")
    
    def test_get_reply(self):
        res = self.stanza.get_reply()
        self.assertEqual(res.to, self.from_)
        self.assertEqual(res.from_, self.to)
        self.assertTrue(isinstance(res, stanzas.Stanza))
        

class TestIq(unittest.TestCase):
    
    def setUp(self):
        self.to = JID('to')
        self.from_ = JID('from')
        self.iq = stanzas.Iq(type_='get', to=self.to, from_=self.from_)
    
    def test_clean_type_(self):
        self.assertRaises(base.ElementParseError, self.iq.clean_type_, 'something')
        values = ['set', 'get', 'result', 'error']
        for value in values:
            self.assertEqual(self.iq.clean_type_(value), value)
    
    def test_clean_id(self):
        value = 'id'
        self.assertEqual(self.iq.clean_id(value), value)
        self.assertEqual(self.iq.clean_id(None), 'H_2')
    
    def test_makeResult(self):
        res = self.iq.makeResult()
        self.assertEqual(res.type_, 'result')
        self.assertEqual(res.from_, self.to)
        self.assertEqual(res.to, self.from_)
        self.assertTrue(isinstance(res, stanzas.Iq))
        
        
class TestMyValidator(unittest.TestCase):
    def test_clean_to(self):
        Validator = stanzas.MyValidator()
        disp = dispatcherEmul('myjid')
        Validator.host = hostEmul(dispatcher=disp)
        self.assertEqual(Validator.clean_to(JID('myjid')), disp.myjid)
        self.assertRaises(base.WrongElement, Validator.clean_to, 'some_jid')

class TestMessage(unittest.TestCase):
    
    def test_clean_type_(self):
        msg = stanzas.Message(to='jid', from_='some_jid')
        self.assertEqual(msg.clean_type_('something'), 'normal')
        values = ('normal', 'chat', 'groupchat', 'headline', 'error')
        for value in values:
            self.assertEqual(msg.clean_type_(value), value)


class TestPresence(unittest.TestCase):
    
    def test_clean_type_(self):
        prs = stanzas.Presence(to='jid', from_='some_jid')
        self.assertEqual(prs.clean_type_('something'), None)
        values = ('subscribe', 'subscribed', 'unsubscribe',
                  'unsubscribed', 'available', 'unavailable',
                  'probe', 'error')
        for value in values:
            self.assertEqual(prs.clean_type_(value), value)
    
    def test_type_(self):
        values = ('subscribe', 'subscribed', 'unsubscribe',
                  'unsubscribed', 'available', 'unavailable',
                  'probe', 'error')
        for value in values:
            prs = stanzas.Presence(to='jid', from_='some_jid', type_=value)
            self.assertEqual(prs.type_, value)
        prs = stanzas.Presence(to='jid', from_='some_jid')
        self.assertEqual(prs.type_, 'available')
       
        
class TestQuery(unittest.TestCase):
    
    def setUp(self):
        self.query = stanzas.Query()
            
    def test_createFromElement(self):
        func = self.query.createFromElement
        
        el = stanzas.Iq(type_='result')
        self.assertRaises(base.WrongElement, func, el)
        
        el.addChild(stanzas.Query())
        res = func(el)
        self.assertTrue(isinstance(res, stanzas.Query))
        self.assertEqual(res.parent, el)
                
        el = stanzas.Iq(type_='result')
        el.addChild(base.VElement())
        self.assertRaises(base.WrongElement, func, el)
    
    def test_iq(self):
        res = self.query.iq
        self.assertTrue(isinstance(res, stanzas.Query))

