# Solving passwords once and for all
pwgen is a utility that implements a secure scheme for generating passwords.

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
  disagree.
* There is a unique component to every password which is obvious to you. For
  example, for a password for a website, the unique component can be the domain
  name. It doesn't have to be secure, it just has to be unique and obvious (so
  you'll never wonder what you picked).
* *Your password for a given service will be the sha1 hash of the unique component
  concatenated with your secret key.* This produces a 40 hex character password,
  which is as good as a 26-character password using a wider charset.
* So to generate your password at any time, you can simply run 
  ```$ sha1sum "website.comYourSecretKey" ```
  Put a space before `sha1sum` to not save your secret key in your shell history.

## So what does pwgen do?
* It makes sure your secret key isn't stored anywhere. You type it into a
  password input, rather than directly as an argument.
* It saves the sha512 hash of your secret key on your computer to check for
  typos. Otherwise, there'd be no way to tell if you had typed your secret key
  correctly, and then you'd have a password you could never reproduce.
* It sends the password directly to your clipboard. In a future version it might
  wipe the clipboard after a few seconds.
* Usage: ```$ ./pwgen.py website.com``` It will prompt for a master password
  (twice if you haven't saved one on this computer before).

