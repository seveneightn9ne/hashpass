#HashPass
HashPass deterministically generates secure passwords by combining your master password
with a unique slug, e.g. the name of the service the password is for.

There are currently three interfaces: a command-line program, a GUI, and a web app.

## Using the command line program

Usage:
`hashpass [options] [<website>]`

If you provide `<website>`, HashPass will prompt you for your master password and output the
generated password to your clipboard. If you didn't, it ask continuously for website names until
you kill it.

Options:

`  -s --show   Display the password instead of putting it in the clipboard`

If this is the first time using HashPass on this computer, it will ask you for your master
twice, to confirm it's correct and save the hash securely on disk, to prevent future typos.

## Using the web app

I am hosting it on `https://jesskenney.com/hashpass`. You can host it yourself by simply
serving the `web/` directory (it's completely static). If you serve it over HTTP instead of
HTTPS it will give a big ugly warning.

## How does it work / why is this a good idea / etc?

See [`manifesto.md`](https://github.com/seveneightn9ne/hashpass/blob/master/manifesto.md) for
a full explanation of the algorithm and why it's secure.


