"""Definition of Completer class"""
import os
import re
import textwrap
from hashlib import sha256
from pyparam import Params

COMPLETION_SCRIPTS = {
    'bash': """
        _pip_completion()
        {{
            COMPREPLY=( $( COMP_WORDS="${{COMP_WORDS[*]}}" \\
                           COMP_CWORD=$COMP_CWORD \\
                           PIP_AUTO_COMPLETE=1 $1 2>/dev/null ) )
        }}
        complete -o default -F _pip_completion {prog}
    """,
    'zsh': """
        function _pip_completion {{
          local words cword
          read -Ac words
          read -cn cword
          reply=( $( COMP_WORDS="$words[*]" \\
                     COMP_CWORD=$(( cword-1 )) \\
                     PIP_AUTO_COMPLETE=1 $words[1] 2>/dev/null ))
        }}
        compctl -K _pip_completion {prog}
    """,
    'fish': """
        function __fish_complete_pip
            set -lx COMP_WORDS (commandline -o) ""
            set -lx COMP_CWORD ( \\
                math (contains -i -- (commandline -t) $COMP_WORDS)-1 \\
            )
            set -lx PIP_AUTO_COMPLETE 1
            string split \\  -- (eval $COMP_WORDS[1])
        end
        complete -fa "(__fish_complete_pip)" -c {prog}
    """,
}

class Completer(Params):
    """A completer is actually a Params object but do the completions instead"""

    @property
    def uname(self):
        # type: () -> Tuple[str, str]
        """Generate the name that can be used as a variable name according to
        the self.prog and the uuid for the original self.prog"""
        uid = sha256(self.prog).hexdigest()[:6]
        prog = re.sub(r'[^\w_]+', '', self.prog)
        return prog, uid

    @property
    def env_name(self):
        # type: () -> str
        """Generate the env name as the switch for complete"""
        uprog, uid = self.uname
        return f"{uprog.upper()}_COMPLETE_{uid.upper()}"

    def generate(self, shell, python=None):
        # type: (str, Optional[str]) -> None
        """Generate the shell code to be integrated

        For bash, it should be appended to ~/.profile
        For zsh, it should be appended to ~/.zprofile
        For fish, it should be appended to
            ~/.config/fish/completions/{prog}.fish
        """

        if shell == 'zsh':
            print(self._generate_zsh(python=python))
        elif shell == 'fish':
            print(self._generate_fish(python=python))
        elif shell == 'bash':
            print(self._generate_bash(python=python))
        raise ValueError(f'Shell not supported: {shell}')

    def _generate_bash(self, python):
        # type: (Optional[str]) -> str
        """Generate the shell code for bash"""
        uprog, uid = self.uname
        code = f"""\
            _{uprog}_completion_{uid}()
            {{
                COMPREPLY=( $( COMP_WORDS="${{COMP_WORDS[*]}}" \\
                            COMP_CWORD=$COMP_CWORD \\
                            {self.env_name}=1 $1 2>/dev/null ) )
            }}
            complete -o default -F _pip_completion {python or self.prog}
        """
        return textwrap.dedent(code)

    def _generate_fish(self, python):
        # type: (Optional[str]) -> str
        """Generate the shell code for fish"""
        uprog, uid = self.uname
        code = f"""\
            function __fish_complete_{uprog}_{uid}
                set -lx COMP_WORDS (commandline -o) ""
                set -lx COMP_CWORD ( \\
                    math (contains -i -- (commandline -t) $COMP_WORDS)-1 \\
                )
                set -lx {self.env_name} 1
                string split \\  -- (eval $COMP_WORDS[1])
            end
            complete -fa "(__fish_complete_{uprog}_{uid})" \\
                -c {python or self.prog}
        """
        return textwrap.dedent(code)

    def _generate_zsh(self, python):
        # type: (Optional[str]) -> str
        """Generate the shell code for zsh"""
        uprog, uid = self.uname
        code = f"""\
            function _{uprog}_completion_{uid} {{
                local words cword
                read -Ac words
                read -cn cword
                reply=( $( COMP_WORDS="$words[*]" \\
                           COMP_CWORD=$(( cword-1 )) \\
                           {self.env_name}=1 $words[1] 2>/dev/null ))
            }}
            compctl -K _{uprog}_completion_{uid} {python or self.prog}
        """
        return textwrap.dedent(code)

    def complete(self):
        # type: () -> None
        """Do the completion"""
        if not int(os.environ.get(self.env_name, 0)):
            return
