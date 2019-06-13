BASH_INSTALL_COMPLETION = """
# in case is not defined
if [[ $(type -t _get_comp_words_by_ref) == "" ]]; then
    echo "[completions] bash-completion is not installed. Install it first."
    exit 1
fi
"""

BASH_WITH_COMMANDS = BASH_INSTALL_COMPLETION + """

{complete_function}() {{
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

        COMPREPLY=($(compgen -W "${{opts}}" -- ${{cur}}))
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
}}

{exclude_block}
"""

BASH_WITH_COMMANDS_COMMAND = """
            ({command})
            opts="${{opts}} {options}"
            ;;
"""

BASH_EXECUTE = "complete -o default -F {complete_function!r} {name!r}"


BASH_WITHOUT_COMMANDS = BASH_INSTALL_COMPLETION + """

{complete_function}() {{
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

        COMPREPLY=($(compgen -W "${{opts}}" -- ${{cur}}))
        __ltrim_colon_completions "$cur"

        return 0;
    fi
}}

{exclude_block}
"""

FISH_WITH_COMMANDS = """
function {no_command_function}
    for i in (commandline -opc)
            if contains -- $i {commands}
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

FISH_WITH_COMMANDS_GLOBAL_OPTION = \
    "complete -c {name!r} -n {no_command_function!r} -{optype} {option!r} -d {desc!r}"
FISH_WITH_COMMANDS_COMMAND = \
    "complete -c {name!r} -f -n {no_command_function!r} -a {command!r} -d {desc!r}"
FISH_WITH_COMMANDS_COMMAND_OPTION = \
    "complete -c {name!r} -A -n '__fish_seen_subcommand_from {command}' -{optype} {option!r} -d {desc!r}"

FISH_WITHOUT_COMMANDS = """
{option_block}
"""

FISH_WITHOUT_COMMANDS_OPTION = "complete -c {name!r} -{optype} {option!r} -d {desc!r}"

ZSH_WITH_COMMANDS = """#compdef {name}

{complete_function}() {{
    local state com cur

    cur=${{words[${{#words[@]}}]}}

    # lookup for command
    for word in ${{words[@]:1}}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    if [[ ${{cur}} == -* ]]; then
        state="option"
        opts=({global_options})
    elif [[ $cur == $com ]]; then
        state="command"
        coms=({commands})
    fi

    case $state in
        (command)
            _describe 'command' coms
        ;;
        (option)
            case "$com" in
{command_block}
            esac

            _describe 'option' opts
        ;;
        *)
            # fallback to file completion
            _arguments '*:file:_files'
    esac
}}

{complete_function} "$@"
compdef {complete_function} {fullpath}
"""

ZSH_WITHOUT_COMMANDS = """#compdef {name}

{complete_function}() {{
    local cur

    cur=${{words[${{#words[@]}}]}}

    if [[ ${{cur}} == -* ]]; then
        state="option"
        opts=({options})
        _describe 'option' opts
    else
        # fallback to file completion
        _arguments '*:file:_files'
    fi
}}

{complete_function} "$@"
compdef {complete_function} {fullpath}
"""

ZSH_WITH_COMMANDS_COMMAND = """
            ({command})
            opts=({options})
            ;;
"""

def _optionStyle(option):
	"""
	Tell the style of an option.
	1. '-' or '--': naked   (a)
	2. '--abc'    : long    (l)
	3. 'abc'      : commnad (a)
	4. '-abc'     : oldlong (o)
	5. '-a'       : short   (s)
	"""
	if option in ('-', '--'):
		return 'a'
	if option.startswith('--'):
		return 'l'
	if not option.startswith('-'):
		return 'f -a'
	if len(option) > 2:
		return 'o'
	return 's'

def assembleBashWithCommands(name, complete_function, global_options, commands, fullpath = None):
	command_block = [
		BASH_WITH_COMMANDS_COMMAND.format(
			command = command.name,
			options = ' '.join(command.options.keys())
		) for command in commands.values()
	]
	exclude_block = [BASH_EXECUTE.format(complete_function = complete_function, name = name)]
	if fullpath:
		exclude_block.append(
			BASH_EXECUTE.format(complete_function = complete_function, name = fullpath))

	return BASH_WITH_COMMANDS.format(
		complete_function = complete_function,
		global_options    = ' '.join(global_options.keys()),
		command_block     = '\n'.join(command_block),
		commands          = ' '.join(commands.keys()),
		exclude_block     = '\n'.join(exclude_block)
	)

def assembleBashWithoutCommands(name, complete_function, options, fullpath = None):
	exclude_block = [BASH_EXECUTE.format(complete_function = complete_function, name = name)]
	if fullpath:
		exclude_block.append([
			BASH_EXECUTE.format(complete_function = complete_function, name = fullpath)])
	return BASH_WITHOUT_COMMANDS.format(
		complete_function = complete_function,
		options           = ' '.join(options.keys()),
		exclude_block     = '\n'.join(exclude_block)
	)

def assembleFishWithCommands(name, no_command_function, global_options, commands, fullpath = None):
	global_option_block = [
		FISH_WITH_COMMANDS_GLOBAL_OPTION.format(
			name                = name,
			no_command_function = no_command_function,
			optype              = _optionStyle(option),
			option              = option.lstrip('-') \
				if _optionStyle(option) != 'a' else option,
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
		FISH_WITH_COMMANDS_COMMAND_OPTION.format(
			name    = name,
			command = cmdname,
			optype  = _optionStyle(option),
			option  = option.lstrip('-') \
				if _optionStyle(option) != 'a' else option,
			desc    = desc
		)
		for cmdname, command in commands.items()
		for option, desc in command.options.items()
	]
	return FISH_WITH_COMMANDS.format(
		no_command_function  = no_command_function,
		global_option_block  = '\n'.join(global_option_block),
		commands             = ' '.join(repr(cmd) for cmd in commands),
		command_block        = '\n'.join(command_block),
		command_option_block = '\n'.join(command_option_block),
	)

def assembleFishWithoutCommands(name, no_command_function, options, fullpath = None):
	option_block = [
		FISH_WITHOUT_COMMANDS_OPTION.format(
			name   = name,
			optype = _optionStyle(option),
			option = option.lstrip('-') \
				if _optionStyle(option) != 'a' else option,
			desc   = desc
		)
		for option, desc in options.items()
	]
	option_block.insert(0, '# ' + no_command_function)
	return FISH_WITHOUT_COMMANDS.format(
		option_block = '\n'.join(option_block)
	)

def _escapeColon(name):
	"""Escape colon in command/option name for zsh"""
	return name.replace(':', '\\:')

def assembleZshWithCommands(name, complete_function, global_options, commands, fullpath = None):
	command_block = [
		ZSH_WITH_COMMANDS_COMMAND.format(
			command = comname,
			options = ' '.join(repr(_escapeColon(option) + ':' + _escapeColon(desc))
			for option, desc in command.options.items())
		) for comname, command in commands.items()
	]
	return ZSH_WITH_COMMANDS.format(
		name              = name,
		fullpath          = fullpath,
		complete_function = complete_function,
		command_block     = '\n'.join(command_block),
		global_options    = ' '.join(repr(_escapeColon(option) + ':' + _escapeColon(desc))
			for option, desc in global_options.items()),
		commands          = ' '.join(repr(_escapeColon(comname) + ':' + _escapeColon(command.desc))
			for comname, command in commands.items()),
	)

def assembleZshWithoutCommands(name, complete_function, options, fullpath = None):
	return ZSH_WITHOUT_COMMANDS.format(
		name              = name,
		fullpath          = fullpath,
		complete_function = complete_function,
		options           = ' '.join("'%s'" % (_escapeColon(option) + ':' + _escapeColon(desc))
			for option, desc in options.items())
	)
