**Content**
- [How to contribute](#how-to-contribute)
- [Coding Guideline](#coding-guideline)

# How to contribute

#### **Did you find a bug?**
- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/MasterZydra/WurzelimperiumBot/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/rails/rails/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

#### **Did you write a patch that fixes a bug?**
- Open a new GitHub pull request with the patch.
- Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

#### **Do you have questions about the source code?**
- Ask any question about how to use as [Issue](https://github.com/MasterZydra/WurzelimperiumBot/issues) with the label **question**.

#### **What is a pull request?**
A pull request, short PR, is the best way to get changes from a forked repository merged into the main repository.  
PRs have multiple advantages:
- The maintainers can review the changes and see what will change if it is accepted and merged.
- If the branch in the forked repository changed, the PR gets automatically updated with that new changes.
- When creating a PR or changes are pushed from the forked repository a check is executed if it can merge without conflicts.

#### **What is the process to get a pull request merged?**
- The maintainer(s) of the main repository have to review the PR.
- If changes are requested these have to be fixed, to ensure the quality and stability of the project.
- The changes must not break the functionality so that the main branch will be defective.

# Coding Guideline
Please follow the rules below:

- We want to **focus on new features** instead of changing "good enough code".  
  This way the changes should provide added value.

- **Prioritize readability over cleverness**:  
  This article is more or less the way I think about it:  
  https://remarkablemark.org/blog/2022/01/16/readable-versus-clever-code/

- **Keep changes small**:  
  Refactoring is great and absolutely necessary!  
  However, if a new feature is added and the same commit includes numerous small changes such as indentation and empty lines, it can be challenging to perform a code review.

- **Coding in English**:  
  Because the WurzelimperiumBot is now also used for e.g. the Bulgarian Wurzelimperium equivalent, it would be more accessible for new contributors if the code is written in English.

- **Python Coding Standard Recommendations**:  
  There is a coding standard on the official python website. We try to follow it:  
  https://peps.python.org/pep-0008/#function-and-variable-names
