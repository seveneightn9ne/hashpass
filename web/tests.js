require(["./hashpasslib"], function(hashpasslib) { // Start of module.

mocha.setup('tdd');
mocha.checkLeaks();
mocha.run();

suite("HashPassAlg", function() {
  setup(function() {
    this._test_site = function(rerolls, master, slug, result) {
      // Test one site password, ignores the reroll parameter.
      expect(hashpasslib.make_password(master, slug)).to.equal(result);
    };
  });

  test("is_good_pass", function() {
    expect(hashpasslib.is_good_pass("a4#aaaaaaaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("oooo6o#ooaaaaaaaaaaa")).to.be(true);
    expect(hashpasslib.is_good_pass("")).to.be(false);
    expect(hashpasslib.is_good_pass("oeuoeuOOO2343")).to.be(false);
  });

  test("make_password_simple", function() {
    this._test_site(0, "wwsx6kolKO", "Ckf2oCe18I", "jzebYcmJ}+8b5rye{9Dn");
    this._test_site(0, "ld55r6WDwQ", "GC5S79GqSO", "6xMrd#LETG{HX7R=4T#m");
    this._test_site(0, "efc2IqOijl", "aPu9wXGvAP", "uU9mbYPb7cewS?@9d*9B");
    this._test_site(1, "B3u9mDOEeS", "nEi2IWIV0w", "bL?Y9#+{)CB#o5AX}SVf");
    this._test_site(1, "JP8EUAzBnR", "zrSqXm2mGG", "LpgTEhsU9Bg*kt3YY9ca");
    this._test_site(1, "FpJSv3ihkH", "TgaTRyIkDe", "9GwcXw?c8zU4}kaFvyzT");
  });

  test("make_password_rerolls", function() {
    this._test_site(2, "vFWLes9UiF", "PuVVQfm2po", "T3eq+=#c(mqvvyTkjUxh");
    this._test_site(2, "rl7XJ8BAGN", "5RMHUhtPwC", "ksTEMD@SQda3y8j@raxn");
    this._test_site(2, "p6SMCnGvk7", "CNY4p2xRzE", "w(4nDC6N9#Mz#Qk=rRTo");
    this._test_site(3, "PXDeRAprND", "PWk8Z4l11M", "TKV64o#AuNw6g)3hNEf@");
    this._test_site(3, "cpp4BigYOS", "iQ0b5dpaK7", "WkC=365S7kLPe6=}UTGw");
    this._test_site(3, "lALmhk7BUd", "KVSVshAKnT", "jF6UnKgp94e)j6mnuB@#");
    this._test_site(4, "fPmAEDLRb5", "jvnsGGw6sJ", "NfS44cMKPr)3LJJjs@7q");
    this._test_site(4, "O4MhHSyaKo", "5Jf9O2SK0E", "8Hv+k=k)ox5BurM8jou7");
    this._test_site(4, "EnVAR9wmHZ", "IRztX5yKim", "7Q=SKQ3a{=pHk4UH)N6g");
    this._test_site(5, "Dqwz1XXJjf", "1b5Uaj47jx", "TS9KtB)RWcPoRd#GY@@x");
    this._test_site(5, "L7UnQr4EgO", "necPJcqE6e", "3?JsK#brB=SNRcrhDX#=");
    this._test_site(6, "nVoKbxmzuA", "lmOMsSXZ5A", "{Q=}Aew(u8U)+*unehdM");
    this._test_site(5, "iSqlhru8op", "gJiWkK4JcO", "8wTU=am6g{=3BfoL}fuY");
    this._test_site(6, "d9bqrOq7mN", "0ZSK8Ij1RT", "CgK9{jp=8vVgt=8)fJgU");
    this._test_site(7, "S1R1yyV1i0", "ZKyePZecAO", "o}JgLvJv*4cmw{rcAXBo");
  });
});

mocha.run();

}); // End of module.
