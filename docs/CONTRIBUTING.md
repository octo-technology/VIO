# Contributing

## Contribution rules
- The code must be exhaustively tested.
- Python test package: `pytest` (with possibility to use unittest mocks)
- Code style: PEP8
- Programming language for code and comments: English

## Coding conventions
- 120 character max per line
- Use python 3.6 `fstring` instead of `format()` or `%s`
- Directories, filenames, function and method names in `snake_case`
- Class names in `UpperCamelCase`
- Private and protected function and method names prefixed with `_`
- Please implement private function and method under the corresponding public for more readability
- Variables name in `snake_case`, constants `MAJ_SNAKE_CASE`
- Static method should be used only when needed (for example a method is called without the instance of the 
corresponding class).
- Don't let any dead code. Prefer to create a ticket in the backlog board. Package `vulture` can be used to check any
 existing dead code.
- Use [pathlib](https://docs.python.org/3/library/pathlib.html#module-pathlib) instead of native Python [os.path](https://docs.python.org/3/library/os.path.html)

## Exception conventions
- Create a custom exception in the module `exception.py` as follow:
```python
class MyCustomException(Exception):
    pass
```
- Add a custom message when it is raised:
```python
if not something:
    raise MyCustomException('My custom message.')
```
- Log the custom exception message when it is caught via the `exception` method of the logger as follow:
```python
try:
    do_something()
except MyCustomException as e:
    self.logger.exception(e)
    return True
```

## Logging conventions
- The logger should always be used at the class level and not the module level.
- The logger should always be created through the _getChild_ method as a class attribute.
- The created child logger should always be used in the class.
- Be aware that all nodes classes that inherit from AbstractNode have already a logger that should be used in the class scope
```python
from aivi.tools.logger import logger


class MyClassWithLogging:
    def __init__(self):
        self.logger = logger.getChild(f'{self.__class__.__name__}')
        self.attr1 = "attr1"
        self.attr2 = 2
    
    def my_method(self):
        do_something()
        self.logger.info('Doing something!')
```

## Test conventions
- The same file hierarchy should be used between a project and the associated tests.
```
my_project
    |my_project
    |   |my_module.py
    |   |
    |tests
    |   |test_my_module.py
    |   |
```
- Please respect the matching: one class method for one class (or one function if there is no class). 
- Respect the following syntax (given when then & only one assert):
```python
def my_function(arg):
    toto = ''
    if arg:
        toto += 'a string'
    return toto

class TestMyFunction:
    def test_returns_a_string_if_arg_is_true(self):
        # Given
        arg = True
        expected = 'a string'
    
        # When
        result = my_function(arg)
    
        # Then
        assert result == expected

    def test_returns_empty_string_if_arg_is_none(self):
        # Given
        arg = None
        expected = ''
    
        # When
        result = my_function(arg)
    
        # Then
        assert result == expected
```
- If a mock is needed, use a decorator instead of a context manager:
```python
def my_function(arg):
    another_function(arg)

class TestMyFunction:
    @patch('aivi.path.to.module.another_function')
    def test_returns_a_string_if_arg_is_true(self, mock_another_function):
        # Given
        arg = True
    
        # When
        my_function(arg)
    
        # Then
        mock_another_function.assert_called_once_with(arg)
```
- Don't mistake a stub for a mock. A mock is used to assert that it has been called (see above example). A stub 
is used to simulate the returned value.

### Testing and docker images
- In order to run the tests, your docker instance will need to be connected to github, allowing docker to pull the images.
You can follow [these steps](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-with-a-personal-access-token-classic)
to establish a token connection between docker and github.

⚠ If you are not working with a M1 processor ⚠

You may encounter some deployment problems when starting the Orchestrator's tests.
To resolve them you will have to build a docker image that fits your system using the Orchestrator's makefile and modify
the `conftest.py` file to edit the `image_name` field.
```
VIO/edge_orchestrator/tests/conftest.py

EDGE_MODEL_SERVING = {
    "image_name": --NEW_DOCKER_IMAGE--,
    "container_volume_path": "/tf_serving",
    "host_volume_path_suffix": "edge_model_serving",
}
```
You will need to change the `starting_log` parameter and remove the call to `check_image_presence_or_pull_it_from_registry` 
from the `container.py` file.

```
VIO/edge_orchestrator/tests/fixtures/containers.py

if tf_serving_host is None or tf_serving_port is None:
    port_to_expose = 8501
    container = TfServingContainer(
        image=image_name,
        port_to_expose=port_to_expose,
        env={"MODEL_NAME": exposed_model_name},
        host_volume_path=host_volume_path,
        container_volume_path=container_volume_path,
    )
    container.start("INFO:     Application startup complete.")
```

## Versioning strategy
- Git tutorial:
    - [Basic git tutorial](http://rogerdudler.github.io/git-guide/)
    - [Learn git branching](https://learngitbranching.js.org/)
- Naming rules for commits and branches:
    - One commit per functionality
    - Describe your commits and branches names with a description of the feature
    - [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
    - [Semantic Commit Messages](https://seesparkbox.com/foundry/semantic_commit_messages)
- Semantic versioning : _X.Y.Z_
    - _X_ needs to be incremented each time a __major__ change is made (e.g. Python 2 to Python 3)
    - _Y_ needs to be incremented each time a __minor__ change is made (e.g. new features)
    - _Z_ needs to be incremented each time a __patch__ is made (e.g. bug fixing)
- Versioning strategy: [Trunk Based Development](https://trunkbaseddevelopment.com/). 
  To implement a new US, please follow the steps:
    - Checkout on master and update the branch with the remote repository
    - Create a new branch following the naming convention below and checkout on it:
      <ticket_id>_feature_description_in_snake_case_starting_with_a_verb (ex: 123_add_users_table)
    - Develop the functionality and don't forget to rebase frequently on master
    - Make sure that all the tests are green
    - Make sure that the `README.md` doesn't need to be updated
    - Add the files to be tracked and commit your modifications
    - Open a merge request with target `master` (check the `squach commits` and `remove branch after merge` options)
    - The MR must launch a CI pipeline (lint, test and build stage) and this pipeline needs to be green to allow to merge the MR
    - The final MR commit must follow the following naming conventing: `[US-ID] Add my brand new feature`
    - Organize a review with all your teammates to challenge and validate the code
    - All discussions must be closed before merging
    - After validation: rebase your branch on master, wait for the CI pipeline to be green and merge on master (`fast-forward` option activated on gitlab)

Reminder of the git commands:

git checkout master && git fetch -p origin && git reset --hard origin master
git checkout -b 123_add_a_new_feature
### 
git add my_file.py
git commit -m '[US-ID] Add my brand new feature'
git push origin 123_add_a_new_feature
###
git checkout master
git pull --rebase origin/master
pytest tests

git tag (Listing the existing tags)
git tag -a <version> -m <message> (Create new tag)
git push origin <version> (Sharing the tags to the remote)
```
- When to do?
	- When you want to add new dependency package.
	- When you want to remove existing dependency package.
