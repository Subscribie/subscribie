# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change. 

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Git Pull Request Process

Question:
> I would like to ask for explanation about git best practices. Like naming branches, I was in most cases worked alone projects so things like this were not important to me but now I need some guidance about those stuffs. 

Answer: 

- Contribution and change must start with creating a github issue, even if a tiny change. This gives you an issue number to use later on


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
