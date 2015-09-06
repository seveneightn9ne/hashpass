import unittest
import hashpasslib


class TestToChars(unittest.TestCase):
    def test_to_chars(self):
        self.assertEqual(hashpasslib._to_chars([0, 0, 0]), "aaaa")
        self.assertEqual(hashpasslib._to_chars([255, 255, 255]), "????")
        self.assertEqual(hashpasslib._to_chars([4,32,196]), "bcde")

    def test_is_good_pass(self):
        self.assertTrue(hashpasslib.is_good_pass("a4#"))
        self.assertTrue(hashpasslib.is_good_pass("oooo6o#oo"))
        self.assertFalse(hashpasslib.is_good_pass(""))
        self.assertFalse(hashpasslib.is_good_pass("oeuoeuOOO2343"))

    def test_make_password(self):
        self.assertEqual("P4{tRc6X3q}5)bCw}su=",
                hashpasslib.make_password_inner("a", "b"))
        self.assertEqual("C}Kzk*)6(CbR}sM5PxuK",
                hashpasslib.make_password_inner("a", "sportsball"))
        self.assertEqual("4D*y7}fP646v3rdWEMz6",
                hashpasslib.make_password_inner("batterystapler", "sportsball"))


if __name__ == '__main__':
    unittest.main()
