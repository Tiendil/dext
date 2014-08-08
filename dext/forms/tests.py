# coding: utf-8

from dext.common.utils import testcase

from dext.forms.fields import EmailField


class EmailFieldTest(testcase.TestCase):

    def setUp(self):
        super(EmailFieldTest, self).setUp()
        self.field = EmailField()

    def test_clean__right_dog(self):
        self.assertEqual(self.field.clean('Bla@Bla.blA'), 'Bla@bla.bla')
