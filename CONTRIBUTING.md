# Contributing

When contributing to this repository, please first discuss the change you wish to make via an issue.

Please note we have a code of conduct, please follow it in all your interactions with the project.

- [Project Folder Structure](#project-folder-structure)
- [Blueprints Organise Things](#blueprints-organise-things)
- [Logging](#logging)
- [Debugging](#debugging)
## How to I made a change to the template?



First you need to find the template, so [read Project folder structure first](#project-folder-structure).

Once you've found the `@route` for the page you want to update (e.g. `/admin/dashboard`) then, you'll see a call to `render_template` e.g:

```
return render_template(
        "admin/dashboard.html", ...
```



If you're [editing a blueprint](#blueprints-organise-things) then the template will be inside a subfolder called `templates` below the blueprint (e.g. `subscribie/blueprints/admin/templates/admin/dashboard.html`).

When editing a template locally, to make flask automatically reload you needed to `export FLASK_DEBUG=1` otherwise flask won't reload and you don't see the changes (unless you manually restart (`Ctl+c` and `flask run`).  

## Project folder structure
### Help finding things: Where do I find x? Where is file y?


### `./subscribie/views.py` - Defines the public routes e.g. homepage & most public routes

For example the route `/choose` (e.g. `http://127.0.0.1/choose`) is defined in: `./subscribie/views.py` for example:

```
@bp.route("/choose")
def choose():
    # ...
    return render_template("choose.html")
```

### `./subscribie/blueprints/admin/` - Defines the admin routes e.g. the dashboard

For example `http://127.0.0.1:5000/admin/dashboard` is defined in:
`subscribie/blueprints/admin/__init__.py`:

```
@admin.route("/dashboard")
@login_required
def dashboard():
    #...
    render_template("admin/dashboard.html")
```

`admin` is a [Flask blueprint](https://flask.palletsprojects.com/en/2.0.x/blueprints/) which is a way to orgnise things.


### `./migrations` is the database migrations folder

All the database migrations (changes to the database schema) are in `./migrations`. You never create these files manually, but you do *edit* them after you've created a database migration if it needs adjustment.

## Blueprints organise things

`admin` is a [Flask blueprint](https://flask.palletsprojects.com/en/2.0.x/blueprints/) which is a way to orgnise things.

Inside each blueprint there are `@route` decorators for each of the paths the blueprint provides. 

Subscribie has multiple blueprints:

- `admin` - For the shop owner admin routes (e.g. `/dashboard`)
  - subscribie/blueprints/admin/ 
- `checkout` - The checkout / sign-up & payment process (e.g. `/new_customer` and begins Stripe checkout)
  - subscribie/blueprints/checkout/
- `subscriber` - Subscribers can login and see their subscriptions (e.g. `/account/subscriptions`)
  - subscribie/blueprints/subscriber/
- `style` - Shop owners can change the colour shade of their shop
  - subscribie/blueprints/style/
- `pages` - Allows shop owners to create custom pages
  - subscribie/blueprints/pages/
- `iframe` - Allows shop owners to copy/paste iframe code to embed their shop in another website. 
  - subscribie/blueprints/iframe/
- `seo` - Allows shop owners to provide search engine friendly page titles/names
  - subscribie/blueprints/seo/
 
## Logging
### Debugging without logging is a bad experience. Turn on logging!

To increase or decrease the amount of logs you see change the `PYTHON_LOG_LEVEL` setting:

```
export PYTHON_LOG_LEVEL=DEBUG
flask run
# .. now more logs will show
```

These are all the options from [python docs](https://docs.python.org/3/library/logging.html#logging-levels)
```
CRITICAL
ERROR # Only show Errors and critical
WARNING
INFO
DEBUG # Show everything and above
NOTSET # Turn off logging
```

Logs only show if you write them! If you see code which has no useful logging consider adding some. The logger automatically include the line number, filename, and function being called, so you don't need to mention that. Here's an [example of writing a useful error message](https://github.com/Subscribie/subscribie/blob/9b19d59812f62dd9e72f9022f3a7853e44d9f08b/subscribie/blueprints/checkout/__init__.py#L71).

## Debugging
### Something is broken/not working, how do I investigate?

See also [Logging](#Logging)

See also very cool [Wizard Zine for debugging tips!](https://wizardzines.com/zines/wizard/)


Python has a built in debugger called `pdb`. To use it, 

1. put `breakpoint()` in your code. 

2. Refresh/restart the application (`e.g. flask run`),  
3. Go to / visit the page which has the error
4. Python will pause at that line in
your code so you can inspect what's happening
5. Press `n` to go to the next line, and `l` to see the lined around the code your at and `ll` to see all the code.
6. Try typing in the variables into the terminal when paused and press enter, and following the code step-by step- is the code going where you expect?

# Git Pull Request Process- how do I raise a pull request?

Question:
> I would like to ask for an explanation about git best practices. Like naming branches etc, I was in most cases working alone on projects so things like this were not important to me but now I need some guidance about these things. 

Answer: 

- Contributions and changes must start with creating a github issue, even if a tiny change. This gives you an issue number to use later on


Locally developing code, after coning the repo (see README.md)

- checkout to master branch 
- make sure your master branch is up to date.
  - git fetch origin  (this fetches all changes into the .git folder , but it does not change your files yet)
  - git rebase origin/master (this does change your files and makes them up to date with master) 

- create a new branch for the issue, using the number
  - e.g. git checkout 376-shop-owner-subscribers-mobile-friendly
  - (remember your on the master branch, which is good because it contains the most up to date code because you fetched, then rebased) 
- git checkout -b <issue-number>-name-of-issue 
- do your coding , creating small commits which reference the issue e.g. if you updated template.html file
- git add template.html (or which ever fils you changed)
- git commit -m "#376 my subscribers mobile friendly"
- when you use the "#<issue-number>" in a commit message, GitHub automatically shows that commit on the GitHub issue. This is very useful for seeing the issue/code relationship.

- when you say git commit -m "Fix #<issue number> my comment about the code " , if the commit is merged into master, then it automatically closes the issue (which is very cool and useful)
- if you're finished , push the branch , but wait!
  - maybe the master branch has more changes since you wrote your code... you need to fetch and apply those first
- git fetch origin/master (fetches any changes which happened whilst you were working)
- git rebase origin/master  (applies those changes to your current branch) 
- now you're ready to push! Finally!
- git push origin 376-shop-owner-subscribers-mobile-friendly
- never use force push if your working with others in the branch, it will destroy their work. If you're not 100% sure, don't ever use force push. It's only needed 0.1% of the time.
- go to GitHub and raise a pull request 
- there is no need to delete the branch remotely because branches are copy on write (very tiny file size) but locally you might want to delete them if you have hundreds or don't want to see them anymore (git branch -d <branch-name>)
- it's normally a bad idea to delete a branch 10mins after raising a pull request, because you might need to add things later on. You can always get the branch back, it takes seconds, but it's a hassle. Just keep the branch locally , it's not causing any problems, it's helping you because you might want to go back to it in a few weeks.



## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community and platform
* Encourage helping each other learn (e.g. pair programming) from eachothers experience
* Showing empathy towards other community members and users

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
  address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
  professional setting

### Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

### Scope

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project team is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

### Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 1.4,
available at [http://contributor-covenant.org/version/1/4][version]

[homepage]: http://contributor-covenant.org
[version]: http://contributor-covenant.org/version/1/4/
