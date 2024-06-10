~~~~~~~~~~~~~~~~~~~~TIPS~~~~~~~~~~~~~~~~~~~~
WORKFLOW FOR MAKING CODE CHANGES

  in the terminal:
    -Make sure there is a link between your repo and our github

    git remote add origin [URL + .git]

  work in your branch: 
    -this will tell git and IDE that you want to work in your branch

    git checkout your_branch_name

  pull changes from main if any:
    -if any changes happened from somone elses commit, it will pull them into your branch

    git pull origin main

  modify files
   -now you can work safely without fear of changing the main file

  stage changes:
    -this makes sure all the files will be ready to commit

    git add .

  commit the changes: 
    -this is git's way of version control. commit often with a good   description so we you can go back versions if we need to
    -you can commit more than once on each push
    -its common to see multiple commits before a push

    git commit -m "your commit message"

  push changes to remote: 
    - when you are ready to push your commits to your github branch

    git push origin your_branch_name