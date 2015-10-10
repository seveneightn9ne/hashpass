import unittest
import hashpasslib

class TestToChars(unittest.TestCase):
    def test_bytes_to_pw_chars(self):
        self.assertEqual(hashpasslib._bytes_to_pw_chars([0, 0, 0]), "aaaa")
        self.assertEqual(hashpasslib._bytes_to_pw_chars([255, 255, 255]), "????")
        self.assertEqual(hashpasslib._bytes_to_pw_chars([4,32,196]), "bcde")

    def test_is_good_pass(self):
        self.assertTrue(hashpasslib.is_good_pass("a4#aaaaaaaaaaaaaaaaa"))
        self.assertTrue(hashpasslib.is_good_pass("oooo6o#ooaaaaaaaaaaa"))
        self.assertFalse(hashpasslib.is_good_pass(""))
        self.assertFalse(hashpasslib.is_good_pass("oeuoeuOOO2343"))

    def test_make_password(self):
        # reroll 0 times
        self.assertEqual("P4{tRc6X3q}5)bCw}su=",
                hashpasslib.make_password_inner("a", "b"))
        self.assertEqual("4D*y7}fP646v3rdWEMz6",
                hashpasslib.make_password_inner("batterystapler", "sportsball"))

        # reroll 1 time
        self.assertEqual("C}Kzk*)6(CbR}sM5PxuK",
                hashpasslib.make_password_inner("a", "sportsball"))

    def _test_one(self, rerolls, master, slug, result):
        """Test one password, ignores rerolls parameter."""
        self.assertEqual(result,
                hashpasslib.make_password_inner(master, slug))

    def test_make_password_more(self):
        self._test_one(0, "wwsx6kolKO", "Ckf2oCe18I", "jzebYcmJ}+8b5rye{9Dn")
        self._test_one(0, "ld55r6WDwQ", "GC5S79GqSO", "6xMrd#LETG{HX7R=4T#m")
        self._test_one(0, "efc2IqOijl", "aPu9wXGvAP", "uU9mbYPb7cewS?@9d*9B")
        self._test_one(1, "B3u9mDOEeS", "nEi2IWIV0w", "bL?Y9#+{)CB#o5AX}SVf")
        self._test_one(1, "JP8EUAzBnR", "zrSqXm2mGG", "LpgTEhsU9Bg*kt3YY9ca")
        self._test_one(1, "FpJSv3ihkH", "TgaTRyIkDe", "9GwcXw?c8zU4}kaFvyzT")
        self._test_one(2, "vFWLes9UiF", "PuVVQfm2po", "T3eq+=#c(mqvvyTkjUxh")
        self._test_one(2, "rl7XJ8BAGN", "5RMHUhtPwC", "ksTEMD@SQda3y8j@raxn")
        self._test_one(2, "p6SMCnGvk7", "CNY4p2xRzE", "w(4nDC6N9#Mz#Qk=rRTo")
        self._test_one(3, "PXDeRAprND", "PWk8Z4l11M", "TKV64o#AuNw6g)3hNEf@")
        self._test_one(3, "cpp4BigYOS", "iQ0b5dpaK7", "WkC=365S7kLPe6=}UTGw")
        self._test_one(3, "lALmhk7BUd", "KVSVshAKnT", "jF6UnKgp94e)j6mnuB@#")
        self._test_one(4, "fPmAEDLRb5", "jvnsGGw6sJ", "NfS44cMKPr)3LJJjs@7q")
        self._test_one(4, "O4MhHSyaKo", "5Jf9O2SK0E", "8Hv+k=k)ox5BurM8jou7")
        self._test_one(4, "EnVAR9wmHZ", "IRztX5yKim", "7Q=SKQ3a{=pHk4UH)N6g")
        self._test_one(5, "Dqwz1XXJjf", "1b5Uaj47jx", "TS9KtB)RWcPoRd#GY@@x")
        self._test_one(5, "L7UnQr4EgO", "necPJcqE6e", "3?JsK#brB=SNRcrhDX#=")
        self._test_one(6, "nVoKbxmzuA", "lmOMsSXZ5A", "{Q=}Aew(u8U)+*unehdM")
        self._test_one(5, "iSqlhru8op", "gJiWkK4JcO", "8wTU=am6g{=3BfoL}fuY")
        self._test_one(6, "d9bqrOq7mN", "0ZSK8Ij1RT", "CgK9{jp=8vVgt=8)fJgU")
        self._test_one(7, "S1R1yyV1i0", "ZKyePZecAO", "o}JgLvJv*4cmw{rcAXBo")


if __name__ == '__main__':
    unittest.main()
