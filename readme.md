# Password Manifesto
passgen is a utility that implements a secure scheme for generating passwords.

This is my attempt at implementing the *optimal* password scheme.

## What makes a good password?
* *High entropy.* Long passwords with a broad charset have higher entropy. Also,
  they should not contain dictionary words or personal information. This makes
  them harder to crack by brute force.
* *Unique.* A different password should be used for everything, so that revealing
  one doesn't compromise any other.
* *Non compromising.* If someone sees one of your passwords, it should not give
  them information about how to generate any other passwords. e.g. if your Amazon
  password is `amazon*i<OyfG$`, then your google password is probably
  `google*i<0yfG$`, or at least `google` followed by 8 characters. This defeats
  the purpose of having a unique password between the two sites.

Here, I use *password scheme* to mean the way you choose your passwords.

## What makes a good password scheme?
* *Produces good passwords* according to the above criteria.
* *Requires little memorization.* The more you have to remember the more likely
  you are to cut corners.
* *Follows Kerckhoff's principle.* That is, the system should be secure even if
  everything about the system, except the key, is public knowledge.
* *Available anywhere.* I don't want to have to install LastPass before I can
  even log in to my Google account on a new computer. Every linux machine should
  have the capability of telling me any of my passwords given the secret key
  I keep in my head.

## The scheme
* You have a secret key, which is a Good Password (long and random). You have
  to memorize this but this is the only thing you have to memorize. It is the
  only thing keeping your system secure so KEEP IT SECRET. Never use it anywhere
  else. If you'd like to generate one now, you can do so with the following
  command:

  ```
  $ cat /dev/urandom | tr -dc 'a-zA-Z0-9-_!@#$%^&*()_+{}|:<>?=' | fold -w 20 | head -n 1
  ```
  
  I personally would say it's safe to write it down on paper and save it in your
  wallet until you're sure you've memorized it. Some more paranoid than me might
  disagree. You may also want to write it down and put it in a safe place in case
  of emergencies or amnesia.
* There is a unique component to every password which is obvious to you. For
  example, for a password for a website, the unique component can be the domain
  name. It doesn't have to be secure, it just has to be unique and obvious (so
  you'll never wonder what you picked).
* **Your password for a given service will be the sha1 hash of the unique component
  concatenated with your secret key, with "A!" at the end.** This produces a 42
  character password, where the first 40 characters are hex digits. The first 40
  digits alone are as good as a 26-character password using a wide charset. The final
  "A!" is only there because many websites force a capital and a special character
  (since they are a publicly revealed portion of the password they do not actually
  contribute to the security).
* So to generate your password at any time, you can simply run 

  ```$ head -n 1 | head -c -1 | sha1sum```
  
  And then type in `website.comYourSecretKey` to get the hash portion of your password.
  This method keeps your secret key from being saved in your shell history or in the
  process list, but it still appears on the screen when you type it.
* On Android, you can download an app (I use HashStamp) which can similarly SHA1 your text.
  You probably want one that doesn't have internet access and allows erasing the inputs.
  Even better, find an open source one or write your own, to be sure they aren't nefarious :)

## So what does passgen do?
* It makes sure your secret key isn't stored anywhere. You type it into a
  password input so it never appears on the screen.
* It saves the sha512 hash of your secret key on your computer to check for
  typos. Otherwise, there'd be no way to tell if you had typed your secret key
  correctly, and then you'd have a password you could never reproduce.
* It sends the password directly to your clipboard. In a future version it might
  wipe the clipboard after a few seconds.
* Usage: 

  ```$ ./passgen.py website.com``` 

  It will prompt for a master password
  (twice if you haven't saved one on this computer before).
  
## Notes
* Chrome might store your passwords in plaintext (at least, you can look at them at any time).
  You may consider not letting chrome save your passwords.
* Some websites may require fewer characters or disallow symbols or have other requirements
  that this scheme violates. I haven't thought of a good solution for this.
