
BASH_WITH_COMMANDS = """
# in case is not defined
if [[ $(type -t _get_comp_words_by_ref) == "" ]]; then
	_get_comp_words_by_ref() {{
		local exclude flag i OPTIND=1
		local cur cword words=()
		local upargs=() upvars=() vcur vcword vprev vwords

		while getopts "c:i:n:p:w:" flag "$@"; do
			case $flag in
				c) vcur=$OPTARG ;;
				i) vcword=$OPTARG ;;
				n) exclude=$OPTARG ;;
				p) vprev=$OPTARG ;;
				w) vwords=$OPTARG ;;
			esac
		done
		while [[ $# -ge $OPTIND ]]; do
			case ${{!OPTIND}} in
				cur)   vcur=cur ;;
				prev)  vprev=prev ;;
				cword) vcword=cword ;;
				words) vwords=words ;;
				*) echo "bash_completion: $FUNCNAME: \`${{!OPTIND}}':" \
					"unknown argument" >&2; return 1 ;;
			esac
			(( OPTIND += 1 ))
		done

		__get_cword_at_cursor_by_ref "$exclude" words cword cur

		[[ $vcur   ]] && {{ upvars+=("$vcur"  ); upargs+=(-v $vcur   "$cur"  ); }}
		[[ $vcword ]] && {{ upvars+=("$vcword"); upargs+=(-v $vcword "$cword"); }}
		[[ $vprev && $cword -ge 1 ]] && {{ upvars+=("$vprev" ); upargs+=(-v $vprev
			"${{words[cword - 1]}}"); }}
		[[ $vwords ]] && {{ upvars+=("$vwords"); upargs+=(-a${{#words[@]}} $vwords
			"${{words[@]}}"); }}

		(( ${{#upvars[@]}} )) && local "${{upvars[@]}}" && _upvars "${{upargs[@]}}"
	}}
fi

if [[ $(type -t __ltrim_colon_completions) == "" ]]; then
	__ltrim_colon_completions() {{
		if [[ "$1" == *:* && "$COMP_WORDBREAKS" == *:* ]]; then
			# Remove colon-word prefix from COMPREPLY items
			local colon_word=${{1%"${{1##*:}}"}}
			local i=${{#COMPREPLY[*]}}
			while [[ $((--i)) -ge 0 ]]; do
				COMPREPLY[$i]=${{COMPREPLY[$i]#"$colon_word"}}
			done
		fi
	}}
fi

{complete_function}() {
	local cur script coms opts com
	COMPREPLY=()
	_get_comp_words_by_ref -n : cur words

	# for an alias, get the real script behind it
	if [[ $(type -t ${{words[0]}}) == "alias" ]]; then
		script=$(alias ${{words[0]}} | sed -E "s/alias ${{words[0]}}='(.*)'/\\1/")
	else
		script=${{words[0]}}
	fi

	# lookup for command
	for word in ${{words[@]:1}}; do
		if [[ $word != -* ]]; then
			com=$word
			break
		fi
	done

	# completing for an option
	if [[ ${{cur}} == -* ]] ; then
		opts="{global_options}"

		case "$com" in
{command_block}
		esac

		COMPREPLY=($(compgen -W "${{opts}}" -- ${cur}))
		__ltrim_colon_completions "$cur"

		return 0;
	fi

	# completing for a command
	if [[ $cur == $com ]]; then
		coms="{commands}"

		COMPREPLY=($(compgen -W "${{coms}}" -- ${{cur}}))
		__ltrim_colon_completions "$cur"

		return 0
	fi
}

{exclude_block}
"""

BASH_WITH_COMMANDS_COMMAND = """
			({command})
			opts="${{opts}} {options}"
			;;
"""

BASH_EXECUTE = "complete -o default -F {complete_function!r} {name!r}"


BASH_WITHOUT_COMMANDS = """
# in case is not defined
if [[ $(type -t _get_comp_words_by_ref) == "" ]]; then
	_get_comp_words_by_ref() {{
		local exclude flag i OPTIND=1
		local cur cword words=()
		local upargs=() upvars=() vcur vcword vprev vwords

		while getopts "c:i:n:p:w:" flag "$@"; do
			case $flag in
				c) vcur=$OPTARG ;;
				i) vcword=$OPTARG ;;
				n) exclude=$OPTARG ;;
				p) vprev=$OPTARG ;;
				w) vwords=$OPTARG ;;
			esac
		done
		while [[ $# -ge $OPTIND ]]; do
			case ${{!OPTIND}} in
				cur)   vcur=cur ;;
				prev)  vprev=prev ;;
				cword) vcword=cword ;;
				words) vwords=words ;;
				*) echo "bash_completion: $FUNCNAME: \`${{!OPTIND}}':" \
					"unknown argument" >&2; return 1 ;;
			esac
			(( OPTIND += 1 ))
		done

		__get_cword_at_cursor_by_ref "$exclude" words cword cur

		[[ $vcur   ]] && {{ upvars+=("$vcur"  ); upargs+=(-v $vcur   "$cur"  ); }}
		[[ $vcword ]] && {{ upvars+=("$vcword"); upargs+=(-v $vcword "$cword"); }}
		[[ $vprev && $cword -ge 1 ]] && {{ upvars+=("$vprev" ); upargs+=(-v $vprev
			"${{words[cword - 1]}}"); }}
		[[ $vwords ]] && {{ upvars+=("$vwords"); upargs+=(-a${{#words[@]}} $vwords
			"${{words[@]}}"); }}

		(( ${{#upvars[@]}} )) && local "${{upvars[@]}}" && _upvars "${{upargs[@]}}"
	}}
fi

if [[ $(type -t __ltrim_colon_completions) == "" ]]; then
	__ltrim_colon_completions() {{
		if [[ "$1" == *:* && "$COMP_WORDBREAKS" == *:* ]]; then
			# Remove colon-word prefix from COMPREPLY items
			local colon_word=${{1%"${{1##*:}}"}}
			local i=${{#COMPREPLY[*]}}
			while [[ $((--i)) -ge 0 ]]; do
				COMPREPLY[$i]=${{COMPREPLY[$i]#"$colon_word"}}
			done
		fi
	}}
fi

{complete_function}() {
	local cur script coms opts com
	COMPREPLY=()
	_get_comp_words_by_ref -n : cur words

	# for an alias, get the real script behind it
	if [[ $(type -t ${{words[0]}}) == "alias" ]]; then
		script=$(alias ${{words[0]}} | sed -E "s/alias ${{words[0]}}='(.*)'/\\1/")
	else
		script=${{words[0]}}
	fi

	# completing for an option
	if [[ ${{cur}} == -* ]] ; then
		opts="{options}"

		COMPREPLY=($(compgen -W "${{opts}}" -- ${cur}))
		__ltrim_colon_completions "$cur"

		return 0;
	fi
}

{exclude_block}
"""

FISH_WITH_COMMANDS = """
function {no_command_function}
        for i in (commandline -opc)
                if contains -- $i self generate
                        return 1
                end
        end
        return 0
end

# global options
{global_option_block}

# commands
{command_block}

# command options
{command_option_block}
"""

FISH_WITH_COMMANDS_GLOBAL_SHORT_OPTION = "complete -c {name!r} -n {no_command_function!r} -s {option!r} -d {desc!r}"
FISH_WITH_COMMANDS_GLOBAL_LONG_OPTION = "complete -c {name!r} -n {no_command_function!r} -l {option!r} -d {desc!r}"
FISH_WITH_COMMANDS_COMMAND = "complete -c {name!r} -f -n {no_command_function!r} -a {command!r} -d {desc!r}"
FISH_WITH_COMMANDS_COMMAND_SHORT_OPTION = "complete -c {name!r} -A -n '__fish_seen_subcommand_from {command}' -s {option!r} -d {desc!r}"
FISH_WITH_COMMANDS_COMMAND_LONG_OPTION = "complete -c {name!r} -A -n '__fish_seen_subcommand_from {command}' -l {option!r} -d {desc!r}"

FISH_WITHOUT_COMMANDS = """
{option_block}
"""

FISH_WITHOUT_COMMANDS_SHORT_OPTION = "complete -c {name!r} -s {option!r} -d {desc!r}"
FISH_WITHOUT_COMMANDS_LONG_OPTION = "complete -c {name!r} -s {option!r} -d {desc!r}"

ZSH_WITH_COMMANDS = """
#compdef poetry

_poetry_7a8fd1e1bf4c5afe_complete()
{
    local state com cur

    cur=${words[${#words[@]}]}

    # lookup for command
    for word in ${words[@]:1}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    if [[ ${cur} == --* ]]; then
        state="option"
        opts=("--ansi:Force ANSI output" "--help:Display this help message" "--no-ansi:Disable ANSI output" "--no-interaction:Do not ask any interactive question" "--quiet:Do not output any message" "--verbose:Increase the verbosity of messages: 1 for normal output, 2 for more verbose output and 3 for debug" "--version:Display this application version")
    elif [[ $cur == $com ]]; then
        state="command"
        coms=("about:Short information about Poetry." "add:Add a new dependency to pyproject.toml." "build:Builds a package, as a tarball and a wheel by default." "cache\:clear:Clears poetry\'s cache." "check:Checks the validity of the pyproject.toml file." "config:Sets/Gets config options." "debug\:info:Shows debug information." "debug\:resolve:Debugs dependency resolution." "develop:Installs the current project in development mode. \(Deprecated\)" "help:Displays help for a command" "init:Creates a basic pyproject.toml file in the current directory." "install:Installs the project dependencies." "list:Lists commands" "lock:Locks the project dependencies." "new:Creates a new Python project at <path\>" "publish:Publishes a package to a remote repository." "remove:Removes a package from the project dependencies." "run:Runs a command in the appropriate environment." "script:Executes a script defined in pyproject.toml. \(Deprecated\)" "search:Searches for packages on remote repositories." "self\:update:Updates poetry to the latest version." "shell:Spawns a shell within the virtual environment." "show:Shows information about packages." "update:Update dependencies as according to the pyproject.toml file." "version:Bumps the version of the project.")
    fi

    case $state in
        (command)
            _describe 'command' coms
        ;;
        (option)
            case "$com" in

            (about)
            opts+=()
            ;;

            (add)
            opts+=("--allow-prereleases:Accept prereleases." "--dev:Add package as development dependency." "--dry-run:Outputs the operations but will not execute anything \(implicitly enables --verbose\)." "--extras:Extras to activate for the dependency." "--git:The url of the Git repository." "--optional:Add as an optional dependency." "--path:The path to a dependency." "--platform:Platforms for which the dependencies must be installed." "--python:Python version\( for which the dependencies must be installed.")
            ;;

            (build)
            opts+=("--format:Limit the format to either wheel or sdist.")
            ;;

            (cache:clear)
            opts+=("--all:Clear all caches.")
            ;;

            (check)
            opts+=()
            ;;

            (config)
            opts+=("--list:List configuration settings" "--unset:Unset configuration setting")
            ;;

            (debug:info)
            opts+=()
            ;;

            (debug:resolve)
            opts+=("--extras:Extras to activate for the dependency." "--install:Show what would be installed for the current system." "--python:Python version\(s\) to use for resolution." "--tree:Displays the dependency tree.")
            ;;

            (develop)
            opts+=()
            ;;

            (help)
            opts+=("--format:The output format \(txt, json, or md\)" "--raw:To output raw command help")
            ;;

            (init)
            opts+=("--author:Author name of the package" "--dependency:Package to require with an optional version constraint, e.g. requests:\^2.10.0 or requests=2.11.1" "--description:Description of the package" "--dev-dependency:Package to require for development with an optional version constraint, e.g. requests:\^2.10.0 or requests=2.11.1" "--license:License of the package" "--name:Name of the package")
            ;;

            (install)
            opts+=("--develop:Install given packages in development mode." "--dry-run:Outputs the operations but will not execute anything \(implicitly enables --verbose\)." "--extras:Extra sets of dependencies to install." "--no-dev:Do not install dev dependencies.")
            ;;

            (list)
            opts+=("--format:The output format \(txt, json, or md\)" "--raw:To output raw command list")
            ;;

            (lock)
            opts+=()
            ;;

            (new)
            opts+=("--name:Set the resulting package name." "--src:Use the src layout for the project.")
            ;;

            (publish)
            opts+=("--build:Build the package before publishing." "--password:The password to access the repository." "--repository:The repository to publish the package to." "--username:The username to access the repository.")
            ;;

            (remove)
            opts+=("--dev:Removes a package from the development dependencies." "--dry-run:Outputs the operations but will not execute anything \(implicitly enables --verbose\).")
            ;;

            (run)
            opts+=()
            ;;

            (script)
            opts+=()
            ;;

            (search)
            opts+=("--only-name:Search only in name.")
            ;;

            (self:update)
            opts+=("--preview:Install prereleases.")
            ;;

            (shell)
            opts+=()
            ;;

            (show)
            opts+=("--all:Show all packages \(even those not compatible with current system\)." "--latest:Show the latest version." "--no-dev:Do not list the dev dependencies." "--outdated:Show the latest version but only for packages that are outdated." "--tree:List the dependencies as a tree.")
            ;;

            (update)
            opts+=("--dry-run:Outputs the operations but will not execute anything \(implicitly enables --verbose\)." "--lock:Do not perform install \(only update the lockfile\)." "--no-dev:Do not install dev dependencies.")
            ;;

            (version)
            opts+=()
            ;;

            esac

            _describe 'option' opts
        ;;
        *)
            # fallback to file completion
            _arguments '*:file:_files'
    esac
}

_poetry_7a8fd1e1bf4c5afe_complete "$@"
compdef _poetry_7a8fd1e1bf4c5afe_complete /data2/junwenwang/shared/tools/miniconda3/bin/poetry
"""

def assembleBashWithCommands(name, complete_function, global_options, commands):
	if not isinstance(name, list):
		name = [name]
	command_block = [
		BASH_WITH_COMMANDS_COMMAND.format(
			command = command.name,
			options = ' '.join(command.options.keys())
		) for command in commands.values()
	]
	exclude_block = [
		BASH_EXECUTE.format(complete_function = complete_function, name = n)
		for n in name
	]
	return BASH_WITH_COMMANDS.format(
		complete_function = complete_function,
		global_options    = ' '.join(global_options.keys()),
		command_block     = '\n'.join(command_block),
		commands          = ' '.join(commands.keys()),
		exclude_block     = '\n'.join(exclude_block)
	)

def assembleBashWithoutCommands(name, complete_function, options):
	exclude_block = [
		BASH_EXECUTE.format(complete_function = complete_function, name = n)
		for n in name
	]
	return BASH_WITHOUT_COMMANDS.format(
		complete_function = complete_function,
		options           = ' '.join(options.keys())
		exclude_block     = '\n'.join(exclude_block)
	)

def assembleFishWithCommands(name, no_command_function, global_options, commands):
	global_option_block = [
		(FISH_WITH_COMMANDS_GLOBAL_LONG_OPTION if option.startswith('--') \
			else FISH_WITH_COMMANDS_GLOBAL_SHORT_OPTION).format(
			name                = name,
			no_command_function = no_command_function,
			option              = option.lstrip(':'),
			desc                = desc
		) for option, desc in global_options.items()
	]
	command_block = [
		FISH_WITH_COMMANDS_COMMAND.format(
			name                = name,
			no_command_function = no_command_function,
			command             = comname,
			desc                = command.desc
		) for comname, command in commands.items()
	]
	command_option_block = [
		(FISH_WITH_COMMANDS_COMMAND_LONG_OPTION if option.startswith('--') \
			else FISH_WITH_COMMANDS_COMMAND_SHORT_OPTION).format(
			name    = name,
			command = command,
			option  = option.lstrip('-'),
			desc    = desc
		)
		for command in commands.values()
		for option, desc in command.options.items()
	]
	return FISH_WITH_COMMANDS.format(
		no_command_function  = no_command_function,
		global_option_block  = '\n'.join(global_option_block),
		command_block        = '\n'.join(command_block),
		command_option_block = '\n'.join(command_option_block),
	)

def assembleFishWithoutCommands(name, no_command_function, options):
	option_block = [
		(FISH_WITHOUT_COMMANDS_COMMAND_LONG_OPTION if option.startswith('--') \
			else FISH_WITHOUT_COMMANDS_COMMAND_SHORT_OPTION).format(
			name   = name,
			option = option.lstrip('-'),
			desc   = desc
		)
		for option, desc in options.items()
	]
	return FISH_WITHOUT_COMMANDS.format(
		option_block = '\n'.join(option_block)
	)

