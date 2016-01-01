import unittest
import bcrypt
import alg
import binascii
import hmac
import hashlib

class TestHashPassAlg(unittest.TestCase):
    def setUp(self):
        self.intermediates = [
            "$2b$13$X5A4.IjQghzyTGwc0wgRrebu3hlW/WFyN5GnvrTKvYsJtdsr5DXC6",
            "$2b$13$X5A4.IjQghzyTGwc0wgRrejiTwszgBLaN3PTew0gRtIrzb5EHsZB2",]

    def test_make_intermediate(self):
        self.assertEqual(alg.make_intermediate("1234"),
          "$2b$13$X5A4.IjQghzyTGwc0wgRrecUMeNiIgapq6zxM07dr3UDDdHUYWLTC")
        self.assertEqual(alg.make_intermediate("super secret"),
          "$2b$13$X5A4.IjQghzyTGwc0wgRrejDmecj5/NNmPPb5ok4tXNuhs/rdP5zy")
        self.assertEqual(alg.make_intermediate("blowfish"),
          "$2b$13$X5A4.IjQghzyTGwc0wgRrezL8JE8j/mpXN/V6YXoldoca002NMb0a")

    def test_make_intermediate_too_long(self):
        with self.assertRaises(Exception):
            alg.make_intermediate("x" * 73)

    def test_is_good_pass(self):
        self.assertTrue(alg.is_good_pass("a4#aaaaaaaaaaaaaaaaa"))
        self.assertTrue(alg.is_good_pass("oooo6o#ooaaaaaaaaaaa"))
        self.assertFalse(alg.is_good_pass(""))
        self.assertFalse(alg.is_good_pass("oeuoeuOOO2343"))

    def test_make_storeable(self):
        secret = "abcdef"
        stored = alg.make_storeable(secret)
        self.assertTrue(bcrypt.hashpw(secret, stored) == stored)

    def test_check_stored(self):
        # Test with an 11 round bcrypt.
        secret = "blowfish"
        stored = "$2b$11$Gzhmkebfiz2OapRqu/zWSOH2Wa9uAsbb4Vd5q3iKBILsMRX8MBpQa"
        self.assertTrue(alg.check_stored(secret, stored))
        self.assertFalse(alg.check_stored(secret[:-1], stored))

    def test_bytes_to_pw_chars(self):
        self.assertEqual(alg._bytes_to_pw_chars([0, 0, 0]), "aaaa")
        self.assertEqual(alg._bytes_to_pw_chars([255, 255, 255]), "????")
        self.assertEqual(alg._bytes_to_pw_chars([4,32,196]), "bcde")

    def test_hmac(self):
        secret = binascii.a2b_hex("4a656665")
        data = binascii.a2b_hex("7768617420646f2079612077616e7420666f72206e6f7468696e673f")
        expected = binascii.a2b_hex("5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843")
        out = hmac.new(key=secret, msg=data, digestmod=hashlib.sha256).digest()
        self.assertEqual(expected, out)

    def test_hash(self):
        expected_hex = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
        hashres = alg._new_hash("Jefe", "what do ya want for nothing?")
        self.assertEqual(binascii.a2b_hex(expected_hex), hashres)

    def _test_site(self, rerolls, intermediate, slug, result):
        """Test one site password, ignores the reroll parameter."""
        self.assertEqual(result,
                alg.make_site_password(intermediate, slug, old=False))

    def test_make_site_password(self):
        # reroll 0 times
        self.assertEqual("?T7}LNgNP)KkEYRATQ6m",
                alg.make_site_password(self.intermediates[0], "b", old=False))
        self.assertEqual("DuR49nd4W7@fEyH)M?Xk",
                alg.make_site_password(self.intermediates[1], "b", old=False))

        # reroll 1 time
        self.assertEqual("frP}JsfQXxjp5FTt}y{k",
                alg.make_site_password(self.intermediates[0], "blunderbus40", old=False))
        self.assertEqual("NquDtLpKUhSRS7TgBY}f",
                alg.make_site_password(self.intermediates[1], "sportsball", old=False))


    def test_make_site_password_more(self):
        self._test_site(3, self.intermediates[0],
                        "blunderbus67555", "q7=s(}5nFgQEr8}JXoxv")
        self._test_site(4, self.intermediates[0],
                        "blunderbus67679", "3dfdqnu@YfBGx)}*ByQ3")
        self._test_site(6, self.intermediates[0],
                        "blunderbus403936", "V5Wuv?4kG*(?X)bpw?}V")
        self._test_site(6, self.intermediates[0],
                        "blunderbus463867", "TDpxs?Fs#5SQ5*rCX#=z")

class TestHashPassAlgOld(unittest.TestCase):
    def _test_site(self, rerolls, master, slug, result):
        """Test one site password, ignores the reroll parameter."""
        self.assertEqual(result,
                alg.make_site_password(master, slug, old=True))

    def test_make_site_password(self):
        # reroll 0 times
        self.assertEqual("P4{tRc6X3q}5)bCw}su=",
                alg.make_site_password("a", "b", old=True))
        self.assertEqual("4D*y7}fP646v3rdWEMz6",
                alg.make_site_password("batterystapler", "sportsball", old=True))

        # reroll 1 time
        self.assertEqual("C}Kzk*)6(CbR}sM5PxuK",
                alg.make_site_password("a", "sportsball", old=True))

        # bcrypted input
        self.assertEqual("M9PC77h*GmdN@?(hfxcY",
                alg.make_site_password(
                    "$2b$13$X5A4.IjQghzyTGwc0wgRrecUMeNiIgapq6zxM07dr3UDDdHUYWLTC",
                    "xyz", old=True))

    def test_make_site_password_more(self):
        self._test_site(0, "wwsx6kolKO", "Ckf2oCe18I", "jzebYcmJ}+8b5rye{9Dn")
        self._test_site(0, "ld55r6WDwQ", "GC5S79GqSO", "6xMrd#LETG{HX7R=4T#m")
        self._test_site(0, "efc2IqOijl", "aPu9wXGvAP", "uU9mbYPb7cewS?@9d*9B")
        self._test_site(1, "B3u9mDOEeS", "nEi2IWIV0w", "bL?Y9#+{)CB#o5AX}SVf")
        self._test_site(1, "JP8EUAzBnR", "zrSqXm2mGG", "LpgTEhsU9Bg*kt3YY9ca")
        self._test_site(1, "FpJSv3ihkH", "TgaTRyIkDe", "9GwcXw?c8zU4}kaFvyzT")
        self._test_site(2, "vFWLes9UiF", "PuVVQfm2po", "T3eq+=#c(mqvvyTkjUxh")
        self._test_site(2, "rl7XJ8BAGN", "5RMHUhtPwC", "ksTEMD@SQda3y8j@raxn")
        self._test_site(2, "p6SMCnGvk7", "CNY4p2xRzE", "w(4nDC6N9#Mz#Qk=rRTo")
        self._test_site(3, "PXDeRAprND", "PWk8Z4l11M", "TKV64o#AuNw6g)3hNEf@")
        self._test_site(3, "cpp4BigYOS", "iQ0b5dpaK7", "WkC=365S7kLPe6=}UTGw")
        self._test_site(3, "lALmhk7BUd", "KVSVshAKnT", "jF6UnKgp94e)j6mnuB@#")
        self._test_site(4, "fPmAEDLRb5", "jvnsGGw6sJ", "NfS44cMKPr)3LJJjs@7q")
        self._test_site(4, "O4MhHSyaKo", "5Jf9O2SK0E", "8Hv+k=k)ox5BurM8jou7")
        self._test_site(4, "EnVAR9wmHZ", "IRztX5yKim", "7Q=SKQ3a{=pHk4UH)N6g")
        self._test_site(5, "Dqwz1XXJjf", "1b5Uaj47jx", "TS9KtB)RWcPoRd#GY@@x")
        self._test_site(5, "L7UnQr4EgO", "necPJcqE6e", "3?JsK#brB=SNRcrhDX#=")
        self._test_site(6, "nVoKbxmzuA", "lmOMsSXZ5A", "{Q=}Aew(u8U)+*unehdM")
        self._test_site(5, "iSqlhru8op", "gJiWkK4JcO", "8wTU=am6g{=3BfoL}fuY")
        self._test_site(6, "d9bqrOq7mN", "0ZSK8Ij1RT", "CgK9{jp=8vVgt=8)fJgU")
        self._test_site(7, "S1R1yyV1i0", "ZKyePZecAO", "o}JgLvJv*4cmw{rcAXBo")


if __name__ == "__main__":
    unittest.main()
