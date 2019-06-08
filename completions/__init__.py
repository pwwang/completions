#!/usr/bin/env python
"""
Generate completions for shells
"""
import re
import sys
import uuid
import warnings
from os import path, sep, rename
from simpleconf import Config


def checkOptname(optname):
	if optname.startswith('--') and len(optname) <= 3:
		warnings.warn('Long option %r specified, but the name has length < 2' % optname)
	if optname.startswith('-') and not optname.startswith('--') and len(optname) > 2:
		warnings.warn('Short option %r specified, but the name has length > 1' % optname)

def log(msg, *args):
	sys.stderr.write('- %s\n' % (msg % args))

def pushcode(ret, msg, level = 0):
	ret.append('%s%s' % ('\t' * level, msg))

class CompletionsLoadError(Exception):
	"""Raises while failed to load completions from configuration file"""

class Command:

	def __init__(self, name, desc, options = None):
		self.name = name
		self.desc = desc
		self.options = options or {}

	def addOption(self, opt, desc):
		self.options[opt] = desc

class Completions(Command):

	def __init__(self, name = None, desc = None, options = None, fullpath = None):
		super(Completions, self).__init__(name, desc, options)
		self.name = name or sys.argv[0]
		self.desc = desc or ''
		self.commands = {}
		self.uid      = None
		self.fullpath = fullpath and path.realpath(fullpath)

		if sep in self.name:
			self.fullpath = self.fullpath or path.realpath(self.name)
			self.name = path.basename(self.name)

	@property
	def availname(self):
		return re.sub(r'[^\w_]+', '_', path.basename(self.name))

	def addCommand(self, name, desc, options = None):
		self.commands[name] = Command(name, desc, options)

	def command(self, name):
		return self.commands[name]

	def _generateBashWithoutCommands(self):
		pass

	def _generateBashWithCommands(self):
		complete_function = '_%s_%s_complete' % (self.availname, self.uid)
		ret = []
		pushcode(ret, '%s() {' % complete_function)
		pushcode(ret, 'local cur script coms opts com', 1)
		pushcode(ret, 'COMPREPLY=()', 1)
		pushcode(ret, '_get_comp_words_by_ref -n : cur words', 1)
		pushcode(ret, '# for an alias, get the real script behind it', 1)
		pushcode(ret, r'if [[ $(type -t ${words[0]}) == "alias" ]]; then', 1)
		pushcode(ret, r'script=$(alias ${words[0]} | sed -E "s/alias ${words[0]}=\'(.*)\'/\1/")', 2)
		pushcode(ret, 'else', 1)
		pushcode(ret, r'script=${words[0]}', 2)
		pushcode(ret, 'fi', 1)
		pushcode(ret, '# lookup for command', 1)
		pushcode(ret, r'for word in ${words[@]:1}; do', 1)
		pushcode(ret, 'if [[ $word != -* ]]; then', 2)
		pushcode(ret, 'com=$word', 3)
		pushcode(ret, 'break', 3)
		pushcode(ret, 'fi', 2)
		pushcode(ret, 'done', 1)
		pushcode(ret, '# completing for an option', 1)
		pushcode(ret, 'if [[ ${cur} == --* ]] ; then', 1)
		pushcode(ret, '	opts="--ansi --help --no-ansi --no-interaction --quiet --verbose --version"', 1)

		pushcode(ret, '	case "$com" in', 2)

		pushcode(ret, '		(about)', 3)
		pushcode(ret, '		opts="${opts} "', 3)
		pushcode(ret, '		;;', 3)

		pushcode(ret, '		(add)', 3)
		pushcode(ret, '		opts="${opts} --allow-prereleases --dev --dry-run --extras --git --optional --path --platform --python"', 3)
		pushcode(ret, '		;;', 3)

		pushcode(ret, '	esac', 2)

		pushcode(ret, '	COMPREPLY=($(compgen -W "${opts}" -- ${cur}))', 2)
		pushcode(ret, '	__ltrim_colon_completions "$cur"', 2)

		pushcode(ret, '	return 0;', 2)
		pushcode(ret, 'fi', 1)

		pushcode(ret, '# completing for a command', 1)
		pushcode(ret, 'if [[ $cur == $com ]]; then', 1)
		pushcode(ret, '	coms="about add build cache:clear check config debug:info debug:resolve develop help init install list lock new publish remove run script search self:update shell show update version"', 2)

		pushcode(ret, '	COMPREPLY=($(compgen -W "${coms}" -- ${cur}))', 2)
		pushcode(ret, '	__ltrim_colon_completions "$cur"', 2)

		pushcode(ret, '	return 0', 2)
		pushcode(ret, 'fi', 1)
		pushcode(ret, '}')
		pushcode(ret, 'complete -o default -F %s %s' % (complete_function, self.name))
		if self.fullpath:
			pushcode(ret, 'complete -o default -F %s %s' % (complete_function, self.fullpath))
		return '\n'.join(ret)

	def _generateFishWithCommands(self):
		'''
		Generate completions for fish with subcommands:
		'''
		command_check_function = '__fish_%s_%s_complete_no_subcommand' % (self.availname, self.uid)
		ret = []
		pushcode(ret, "function %s" % command_check_function)
		pushcode(ret, "for i in (commandline -opc)", 1)
		pushcode(ret, "if contains -- $i %s" % ' '.join(self.commands.keys()), 2)
		pushcode(ret, "return 1", 3)
		pushcode(ret, "end", 2)
		pushcode(ret, "end", 1)
		pushcode(ret, "return 0", 1)
		pushcode(ret, "end")

		pushcode(ret, "")
		pushcode(ret, "# general options")
		for key, val in self.options.items():
			checkOptname(key)
			key = "-l %r" % key[2:] if key.startswith('--') else '-s %r' % key[1:]
			pushcode(ret, "complete -c %r -n %r %s -d %r" % (
				self.name, command_check_function, key, val))

		pushcode(ret, "")
		pushcode(ret, "# commands")
		for key, val in self.commands.items():
			pushcode(ret, "complete -c %r -f -n %r -a %r -d %r" % (
				self.name, command_check_function, key, val.desc))

		pushcode(ret, "")
		pushcode(ret, "# command options")

		for key, val in self.commands.items():
			pushcode(ret, "# %s" % key)
			for opt, optdesc in val.options.items():
				checkOptname(key)
				opt = "-l %r" % opt[2:] if opt.startswith('--') else '-s %r' % opt[1:]
				pushcode(ret, "complete -c %r -A -n '__fish_seen_subcommand_from %s' %s -d %r" % (
					self.name, key, opt, optdesc))
		return '\n'.join(ret)

	def _generateFishWithoutCommands(self):
		ret = []
		def pushcode(ret, msg, level = 0):
			ret.append('%s%s' % ('\t' * level, msg))

		pushcode(ret, "")
		pushcode(ret, "# options")
		for key, val in self.options.items():
			checkOptname(key)
			key = "-l %r" % key[2:] if key.startswith('--') else '-s %r' % key[1:]
			pushcode(ret, "complete -c %r %s -d %r" % (self.name, key, val))

		return '\n'.join(ret)

	def _generateZshWithCommands(self):
		pass

	def _generateZshWithoutCommands(self):
		pass

	def _automateFish(self, source):
		compfile = path.expanduser('~/.config/fish/completions/%s.fish' % self.name)
		backfile = compfile + '.completions.bak'
		if path.isfile(compfile):
			log('Completion file exists: %r', compfile)
			log('Back it up to: %r', backfile)
			rename(compfile, backfile)
		log('Writing completion code to: %r', compfile)
		with open(compfile, 'w') as fcomp:
			fcomp.write(source)
		log('Done, you may need to restart your shell in order for the changes to take effect.')

	def generateBash(self):
		if self.commands:
			return self._generateBashWithCommands()
		return self._generateBashWithoutCommands()

	def generateFish(self):
		if self.commands:
			return self._generateFishWithCommands()
		return self._generateFishWithoutCommands()

	def generateZsh(self):
		if self.commands:
			return self._generateZshWithCommands()
		return self._generateZshWithoutCommands()

	def generate(self, shell, auto = False):
		self.uid = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.name)).split('-')[-1]
		if shell == 'fish':
			source = self.generateFish()
			if not auto:
				return source
			self._automateFish(source)
		elif shell == 'bash':
			source = self.generateBash()
			if not auto:
				return source
			self._automateBash(source)
		elif shell == 'zsh':
			source = self.generateZsh()
			if not auto:
				return source
			self._automateZsh(source)
		else:
			raise ValueError('Currently only bash, fish and zsh supported.')

	def load(self, dict_var):
		# integrity check
		if 'program' not in dict_var:
			raise CompletionsLoadError("No 'program' key found.")

		program = dict_var['program']
		if 'name' not in program:
			raise CompletionsLoadError("A program name should be given by 'program.name'")
		self.name = program['name']
		self.desc = program['desc']
		if sep in self.name:
			self.fullpath = path.realpath(self.name)
			self.name = path.basename(self.name)

		for key, val in program.get('options', {}).items():
			self.addOption(key, val)

		commands = dict_var.get('commands', '')
		for key, val in commands.items():
			self.addCommand(
				name = key,
				desc = val.get('desc') or '',
				options = val.get('options', {})
			)

	def loadFile(self, compfile):
		config = Config(with_profile = False)
		config._load(compfile)
		self.load(config)

if __name__ == '__main__':
	from pyparam import commands
	commands._.shell.desc     = 'The shell, one of bash, fish and zsh.'
	commands._.shell.required = True
	commands._.auto           = False
	commands._.auto.desc      = [
		'Automatically write completions to destination file:',
		'Bash: `~/bash_completion.d/<name>.bash-completion`',
		'  Also try to source it in ~/.bash_completion',
		'Fish: `~/.config/fish/completions/<name>.fish`',
		'Zsh:  `~/.zfunc/_<name>`',
		'  `fpath+=~/.zfunc` is ensured to add before `compinit`'
	]
	commands._.a                  = commands._.auto
	commands._.s                  = commands._.shell
	commands.self                 = 'Generate completions for myself.'
	commands.self._hbald          = False
	commands.generate             = 'Generate completions from configuration files'
	commands.generate.config.desc = [
		'The configuration file. Scheme should be aligned following json data:',
		'{',
		'	"program": {',
		'		"name": "program",',
		'		"desc": "A program",',
		'		"options": {',
		'			"-o": "Output file",',
		'			"--output": "Long version of -o"',
		'		}',
		'	},',
		'	"commands": {',
		'		"list": {',
		'			"desc": "List commands",',
		'			"options": {',
		'				"-a": "List all commands",',
		'				"--all": "List all commands"',
		'			}',
		'		}',
		'	}',
		'}',
		'',
		'Configuration file that is supported by `python-simpleconf` is supported.'
	]
	commands.generate.config.required = True
	commands.generate.c = commands.generate.config
	command, options, coptions = commands._parse()

	auto = coptions['auto']
	if command == 'self':
		source = commands._complete(coptions['shell'], auto = auto)
		if not auto:
			print(source)
	else:
		completions = Completions()
		completions.loadFile(options['config'])
		source = completions.generate(coptions['shell'], auto = auto)
		if not auto:
			print(source)

