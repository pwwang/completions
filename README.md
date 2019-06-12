# completions

Shell completions for your program made easy.

[![pypi][1]][2] [![tag][3]][4] [![travis][5]][6] [![codacy quality][7]][8] ![pyver][11]

Shell completions for your program made easy.

## Installation
```shell
pip install completions
# install lastest version using poetry
git clone https://github.com/pwwang/completions
cd completions
poetry install
```

## Usage

### Defining your completions
You may define your completions, basically commands and options, by following schema (showed in `yaml`, but can be any format supported by [`python-simpleconf`][12]:
`example.yaml`
```yaml
program:
    # your program, or path to your program
    name: completions-example
    desc: Shell completions for your program made easy.
    # whether global options should be inherited by commands
    inherit: true
    # options or global options if you have commands
    options:
        -s: The shell, one of bash, fish, zsh and auto.
        --shell: The shell, one of bash, fish, zsh and auto.
        -a: Automatically write completions to destination file.
        --auto: Automatically write completions to destination file.
commands:
    # No other options for command, give the description
    self: Generate completions for myself.
    generate:
        desc: Generate completions from configuration files.
        options:
            -c: The configuration file to load.
            --config: The configuration file to load.
```

How it looks like in `fish`:
![command][13]
![option][14]

### Generating completion scripts
- Bash
    ```shell
    > completions generate --shell bash \
        --config example.yaml > ~/bash_completion.d/completions.bash-completion
    ```
    You may need to `source` it in your `.bashrc` and restart your shell for the changes to take effect.
- Fish
    ```shell
    > completions generate --shell fish \
        --config example.yaml > ~/.config/fish/completions/completions.fish
    ```
    You may need to restart your shell for the changes to take effect.
- Zsh
    ```shell
    > completions generate --shell zsh \
        --config example.yaml > ~/.zsh-completions/_completions
    ```
    Make sure `fpath+=~/.zsh-completions` is put before `compinit` in you `.zshrc`

### Saving completions scripts automatically
- Bash
    ```shell
    > completions generate --shell bash --config example.yaml --auto
    ```

- Fish
    ```shell
    > completions generate --shell fish --config example.yaml --auto
    ```

- Zsh
    ```shell
    > completions generate --shell zsh --config example.yaml --auto
    ```

### Python API
```python
from completions import Completions
completions = Completions(
    # if not given, will be read from sys.argv[0]
    name    = 'completions',
    # Add global options to commands
    inherit = True,
    desc    = 'Shell completions for your program made easy.')
completions.addOption(
    ['-s', '--shell'],
    'The shell, one of bash, fish, zsh and auto.')
completions.addOption(
    ['-a', '--auto'],
    'Automatically write completions to destination file.')
completions.addCommand(
    'self', 'Generate completions for myself.')
completions.addCommand(
    'generate', 'Generate completions from configuration files.')
completions.command('generate').addOption(
    ['-c', '--config'], 'The configuration file to load.')
completions.generate(shell = 'fish', auto = False)
```

[1]: https://img.shields.io/pypi/v/completions.svg?style=flat-square
[2]: https://pypi.org/project/completions/
[3]: https://img.shields.io/github/tag/pwwang/completions.svg?style=flat-square
[4]: https://github.com/pwwang/completions
[5]: https://img.shields.io/travis/pwwang/completions.svg?style=flat-square
[6]: https://travis-ci.org/pwwang/completions
[7]: https://img.shields.io/codacy/grade/completions.svg?style=flat-square
[8]: https://app.codacy.com/project/pwwang/completions/dashboard
[11]: https://img.shields.io/pypi/pyversions/completions.svg?style=flat-square
[12]: https://github.com/pwwang/simpleconf
[13]: https://raw.githubusercontent.com/pwwang/completions/master/examples/command.png
[14]: https://raw.githubusercontent.com/pwwang/completions/master/examples/option.png
