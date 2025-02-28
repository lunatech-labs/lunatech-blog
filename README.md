# lunatech-blog
Contains our blog in [Asciidoctor](https://asciidoc.org/) format.

Each post is located in the `posts` directory with the following format: `yyyy-MM-dd-title.adoc`

In the `media` directory there should be a matching image named `yyyy-MM-dd-title/background.png`

All media used in the posts should be located in the `media` directory under a `yyyy-MM-dd-title` directory ie `media/yyy-MM-dd-title`

To add you blog post:
* Install giter8, via coursier
```commandline
brew install coursier/formulas/coursier
cs install giter8
```
* Fork this repo
* Checkout the forked repo
* In the repo directory `g8 file://.`
* Write your blog post
* Submit a pull request and follow the template

# Information regarding giter8

If you see this error :

Error: giter8 has been disabled because it fetches unversioned dependencies at runtime!

Then you can bypass the warning message by doing the following:

brew edit giter8

and delete this line:

disable! because: "fetches unversioned dependencies at runtime"

then run brew install giter8 again.

# Provide compressed images
Every blogpost has at least one image which makes the Lunatech blog relatively heavy in memory consumption.
One way of to combat this is by compressing images using `pngcrush`. You can install it using brew:
```commandline
brew install pngcrush
```
You can then create a compressed version of each image (png/jpeg/gif) you are submitting alongside your blogpost:
```commandline
pngcrush -rem allb -brute -reduce in.png out.png
```
For very large images the command may take a long time to complete.

# How to deploy your post

Merging your PR will update the `main` branch only. In order to share your blog post with the world,
you'll need to deploy it first in [Acceptance](https://blog.acceptance.lunatech.com/), and then
in [Production](https://blog.lunatech.com/).

You can do both with the help of GitHub Actions:
* [Deploy Acceptance](https://github.com/lunatech-labs/lunatech-blog/actions/workflows/deploy_acceptance.yaml)
* [Deploy Production](https://github.com/lunatech-labs/lunatech-blog/actions/workflows/deploy_production.yaml)
