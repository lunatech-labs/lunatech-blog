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


# How to deploy your post
Merging your PR will update the `master` branch only. Besides `master` there's also `acceptance` and `production` branches.

### Getting your post to the acceptance environment
`acceptance` will allow you to see how your post looks like in `https://blog.acceptance.lunatech.com/`.
```
git checkout acceptance
git rebase master
git push origin acceptance
```
The blog engine needs to be manually restarted in clever cloud as well. Please ask your colleagues, if you don't know where to find it.

### Getting your post to the production environment
`production` will allow you to finally share your post with the world.
```
git checkout production
git rebase acceptance
git push origin production
```
The blog engine needs to be manually restarted in clever cloud as well. Please ask your colleagues, if you don't know where to find it.




